import psycopg2
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import pickle
import os

# Database connection details
DB_HOST = "isrpeer.ctw842oc69v3.us-east-2.rds.amazonaws.com"
DB_NAME = "isr_books"
DB_USER = "isr_peer"
DB_PASS = "ISRpeer2024"

def save_embeddings(embeddings, filename):
    with open(filename, 'wb') as f:
        pickle.dump(embeddings, f)

def load_embeddings(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def get_cached_embeddings(filename):
    if os.path.exists(filename):
        return load_embeddings(filename)
    else:
        return None

def cache_embeddings_if_missing(embeddings, filename):
    if not os.path.exists(filename):
        print("Caching embeddings...")
        save_embeddings(embeddings, filename)

def connect():
    conn_string = f"host={DB_HOST} port='5432' dbname={DB_NAME} user={DB_USER} password={DB_PASS}"
    conn = psycopg2.connect(conn_string)
    print("Connected!")
    return conn, conn.cursor()

# Initialize tokenizer and model from Hugging Face Transformers
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(text):
    if text is None or not isinstance(text, str) or text.strip() == "":
        return None
    # Tokenize and convert to input format
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the mean of the last hidden state as embedding
    return outputs.last_hidden_state.mean(dim=1).cpu().numpy()

def fetch_all_courses_data(cursor):
    cursor.execute("SELECT id, title, url, description, headline, num_subscribers, avg_rating, num_reviews, published_title, primary_category, primary_subcategory, num_quizzes, num_lectures, num_curriculum_items, visible_instructors, is_paid, price, what_you_will_learn, who_should_attend, image_480x270, image_50x50, complexity, ts FROM new_merged_course;")
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=['id', 'title', 'url', 'description', 'headline', 'num_subscribers', 'avg_rating', 'num_reviews', 'published_title', 'primary_category', 'primary_subcategory', 'num_quizzes', 'num_lectures', 'num_curriculum_items', 'visible_instructors', 'is_paid', 'price', 'what_you_will_learn', 'who_should_attend', 'image_480x270', 'image_50x50', 'complexity', 'ts'])

def fetch_course_details(cursor, course_titles):
    #query = "SELECT id, title, url, description, headline, num_subscribers, avg_rating, num_reviews, published_title, primary_category, primary_subcategory, num_quizzes, num_lectures, num_curriculum_items, visible_instructors, is_paid, price, what_you_will_learn, who_should_attend, image_480x270, image_50x50, complexity, ts FROM online_courses WHERE title IN %s;"
    escaped_titles = [title.replace("'", "''") for title in course_titles]
    ordering_clause = "ORDER BY title, CASE title "
    ordering_clause += " ".join(f"WHEN '{title}' THEN {index}" for index, title in enumerate(escaped_titles))
    ordering_clause += " END"
    
    # Use f-string to format the titles list into SQL command
    formatted_titles = ', '.join(f"'{title}'" for title in escaped_titles)
    
    # SQL query to fetch book details with ordering
    query = f"SELECT DISTINCT ON (title) *\
        FROM new_merged_course WHERE title IN ({formatted_titles}) {ordering_clause};"
    
    
    try:
        #cursor.execute(query, (tuple(course_titles),))
        cursor.execute(query)
        course_details = cursor.fetchall()
        return course_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def recommend_online(users):
    conn, cursor = connect()
    
    user_courses_df = pd.DataFrame(users['udemy_clicks'], columns=['Title', 'Author', 'Headline', 'View Count'])
    
    # Fetch all courses data from the database
    all_courses_df = fetch_all_courses_data(cursor)

    # Attempt to load cached embeddings for all courses
    all_courses_embeddings_filename = 'all_courses_trial_2.pkl'
    all_courses_embeddings = get_cached_embeddings(all_courses_embeddings_filename)

    # If cache doesn't exist, generate and cache the embeddings
    if all_courses_embeddings is None:
        embeddings_list = []
        for desc in all_courses_df['headline']:
            embedding = get_embeddings(desc)
            if embedding is not None and embedding.shape == (1, 768):  # Ensure embedding is correctly shaped
                embeddings_list.append(embedding)
            else:
                # Handle cases with no or incorrect embedding
                embeddings_list.append(np.zeros((1, 768)))  # Placeholder for missing embeddings
        all_courses_embeddings = np.vstack(embeddings_list)
        cache_embeddings_if_missing(all_courses_embeddings, all_courses_embeddings_filename)


    # Generate embeddings for user courses, assuming these change frequently and shouldn't be cached
    user_courses_embeddings = []
    for desc in user_courses_df['Headline']:
        embedding = get_embeddings(desc)
        if embedding is not None and embedding.shape == (1, 768):
            user_courses_embeddings.append(embedding)
        else:
            user_courses_embeddings.append(np.zeros((1, 768)))  # Placeholder for missing embeddings
    user_courses_embeddings = np.vstack(user_courses_embeddings)

    # Compute cosine similarity
    cosine_sim = cosine_similarity(user_courses_embeddings, all_courses_embeddings)

    # Find top recommendations
    recommendations_set = set()
    print("cosine shape: ",cosine_sim.shape[0])
    for user_course_index in range(cosine_sim.shape[0]):

        top_indices = cosine_sim[user_course_index].argsort()[::-1][:3]  # Get more than 5 to ensure diversity
        
        for index in top_indices:
            if index<len(all_courses_df) and len(recommendations_set) < 15:  # Collect only 5 unique recommendations
                recommendations_set.add(all_courses_df.iloc[index]['title'])
            if len(recommendations_set) == 15:
                break
        if len(recommendations_set) == 15:
            break
        
    
    recommended_courses = list(recommendations_set)
    Course_deets = fetch_course_details(cursor, recommended_courses)
    return Course_deets



