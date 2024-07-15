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

def fetch_all_books_data(cursor):
    cursor.execute("SELECT title, description FROM new_merged_books;")
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=['title', 'description'])

def fetch_book_details(cursor, book_titles):
    print(len(book_titles))
    escaped_titles = [title.replace("'", "''") for title in book_titles]
    
    # Create an ordered list of titles for the SQL query using a CASE statement in ORDER BY
    ordering_clause = "ORDER BY title, CASE title "
    ordering_clause += " ".join(f"WHEN '{title}' THEN {index}" for index, title in enumerate(escaped_titles))
    ordering_clause += " END"
    
    # Use f-string to format the titles list into SQL command
    formatted_titles = ', '.join(f"'{title}'" for title in escaped_titles)
    
    # SQL query to fetch book details with ordering
    query = f"SELECT DISTINCT ON (title) *\
        FROM new_merged_books WHERE title IN ({formatted_titles}) {ordering_clause};"
    
    try:
        cursor.execute(query)
        books_details = cursor.fetchall()
        print(len(books_details))
        return books_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def recommend(users):
    conn, cursor = connect()
    
    user_books_df = pd.DataFrame(users['book_clicks'], columns=['Title', 'Author', 'Description', 'View Count'])

    # Fetch all books data from the database
    all_books_df = fetch_all_books_data(cursor)

    # Attempt to load cached embeddings for all books
    all_books_embeddings_filename = 'all_books_final_2.pkl'
    all_books_embeddings = get_cached_embeddings(all_books_embeddings_filename)

    # If cache doesn't exist, generate and cache the embeddings
    if all_books_embeddings is None:
        embeddings_list = []
        for desc in all_books_df['description']:
            embedding = get_embeddings(desc)
            if embedding is not None and embedding.shape == (1, 768):  # Ensure embedding is correctly shaped
                embeddings_list.append(embedding)
            else:
                # Handle cases with no or incorrect embedding
                embeddings_list.append(np.zeros((1, 768)))  # Placeholder for missing embeddings
        all_books_embeddings = np.vstack(embeddings_list)
        cache_embeddings_if_missing(all_books_embeddings, all_books_embeddings_filename)

    # Generate embeddings for user books, assuming these change frequently and shouldn't be cached
    user_books_embeddings = []
    for desc in user_books_df['Description']:
        embedding = get_embeddings(desc)
        if embedding is not None and embedding.shape == (1, 768):
            user_books_embeddings.append(embedding)
        else:
            user_books_embeddings.append(np.zeros((1, 768)))  # Placeholder for missing embeddings
    user_books_embeddings = np.vstack(user_books_embeddings)

    # Compute cosine similarity
    cosine_sim = cosine_similarity(user_books_embeddings, all_books_embeddings)

    # Find top recommendations
    recommendations_set = set()
    for user_book_index in range(cosine_sim.shape[0]):
        top_indices = cosine_sim[user_book_index].argsort()[::-1][:3]  # Get more than 5 to ensure diversity
        for index in top_indices:
            if index<len(all_books_df) and len(recommendations_set) < 15:  # Collect only 5 unique recommendations
                recommendations_set.add(all_books_df.iloc[index]['title'])
                #recommendations_set.add(index)
            if len(recommendations_set) == 15:
                break
        if len(recommendations_set) == 15:
            break

    recommended_books = list(recommendations_set)
    Book_deets = fetch_book_details(cursor, recommended_books)
    
    return Book_deets   
