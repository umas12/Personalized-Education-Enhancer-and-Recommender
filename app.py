from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import psycopg2
import requests
from requests.auth import HTTPBasicAuth
from IPython.display import HTML, display
import operator
from recommendation_book import recommend
from recommend_online import recommend_online

import re




app = Flask(__name__)

# Updated users list with dictionaries
users = [
    {'username': 'user1', 'password': 'pass1', 'status': '0', 'categories': [], 'queries': [], 'book_clicks': [], 'udemy_clicks': []},
    {'username': 'user2', 'password': 'pass2', 'status': '1', 'categories': [], 'queries': [], 'book_clicks': [], 'udemy_clicks': []}
]


class Udemy(object):

    __BASE_URL = "https://www.udemy.com/api-2.0/"

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.__client_id = client_id
        self.__client_secret = client_secret

    @property
    def url(self) -> str:
        return self.__BASE_URL

    @property
    def client_id(self):
        return self.__client_id

    @property
    def client_secret(self) -> str:
        return self.__client_secret

    def _get_full_url(self, resource: str, **kwargs) -> str:
        url = f"{self.url}{resource}/?"
        field_string = ""
        for param, value in sorted(kwargs.items(), key=operator.itemgetter(0)):
            if param != "fields":
                if "category" in param and "&" in value:
                    value = value.replace(" & ", "+%26+")
                url += f"{param}={value}&"
            else:
                for ele in value:
                    object_name = ele["Object"]
                    params = ",".join(
                        filter(None, [ele["Setting"], ",".join(ele["Additions"]),
                                      ",".join(["-" + x for x in ele["Minus"]])]))
                    field_string += f"fields[{object_name}]={params}&"
        url += field_string
        return url

    @property
    def _authentication(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.client_id, self.client_secret)

    def courses(self, page=1, page_size=10, **kwargs):
        kwargs['page'] = page
        kwargs['page_size'] = page_size
        full_url = self._get_full_url("courses", **kwargs)
        response = requests.get(full_url, auth=self._authentication)
        return response.json()

    def course_detail(self, id: int) -> dict:
        return requests.get(self._get_full_url(f"courses/{id}"), auth=self._authentication).json()




def fetch_udemy_courses(client_id, client_secret, page=1, page_size=10):
    """Initialize Udemy client and fetch courses."""
    udemy_client = Udemy(client_id, client_secret)
    courses_data = udemy_client.get_courses(page, page_size)
    return format_course_details(courses_data)



def transform_data_list(data_list):
    transformed_data_list = []
    for data in data_list:
        data_dict = {
            "Title": data[1],
            "Author": data[2],
            "Publisher": data[3],
            "Publication Date": data[4],
            "Description": data[5],
            "Language": data[17],
            "Price": data[18],
            "Discounted Price": data[19],
            "Google Play": data[10],
            "image_url": data[15]
        }
        transformed_data_list.append(data_dict)
    return transformed_data_list






def format_course_details(courses_data):
    
    formatted_courses = []

    for course_data in courses_data:
        # Construct full URL from the provided partial URL
        url = course_data[2]
        full_url = f"https://www.udemy.com{url}" if url != 'N/A' else 'N/A'       

        # Format course details into a dictionary
        if not course_data[14][0]:
            course_data[14][0]='N/A'

        
        
        course_details = {
            'title': course_data[1],
            'full_url': full_url,
            
            'instructor': course_data[14][0],
            'headline': course_data[4],
            'image_url': course_data[19]
        }

        formatted_courses.append(course_details)

    return formatted_courses




def execute_query(user,complexity):
    DB_HOST = "isrpeer.ctw842oc69v3.us-east-2.rds.amazonaws.com"
    DB_NAME = "isr_books"
    DB_USER = "isr_peer"
    DB_PASS = "ISRpeer2024"

    conn = None
    results = []
    try:
        conn_string = f"host={DB_HOST} port=5432 dbname={DB_NAME} user={DB_USER} password={DB_PASS}"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        if user['queries']:  # Check if the 'queries' list is not empty
            latest_query = user['queries'][-1]  # Get the latest query
            latest_query = re.sub(r'\s+', '_', latest_query)  # Replace one or more spaces with a single underscore
            latest_query = re.sub(r'[^\w\s]', '', latest_query)  # Remove special characters
            print(latest_query)
            sql_query = f"""
            SELECT * FROM new_merged_books WHERE Complexity = '{complexity}'
            ORDER BY ts_rank(ts, to_tsquery('english', '{latest_query}')) DESC;
            """
            cursor.execute(sql_query)
            results = cursor.fetchmany(size=10)  # Fetch the results
        else:
            raise ValueError(f"No queries available for {user['username']}")
        
    except Exception as e:
        raise Exception(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
    return transform_data_list(results)

def execute_online_query(user,complexity):
    DB_HOST = "isrpeer.ctw842oc69v3.us-east-2.rds.amazonaws.com"
    DB_NAME = "isr_books"
    DB_USER = "isr_peer"
    DB_PASS = "ISRpeer2024"

    conn = None
    results = []
    try:
        conn_string = f"host={DB_HOST} port=5432 dbname={DB_NAME} user={DB_USER} password={DB_PASS}"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        if user['queries']:  # Check if the 'queries' list is not empty
            latest_query = user['queries'][-1]  # Get the latest query
            latest_query = user['queries'][-1]  # Get the latest query
            latest_query = re.sub(r'\s+', '_', latest_query)  # Replace one or more spaces with a single underscore
            latest_query = re.sub(r'[^\w\s]', '', latest_query)  # Remove special characters
            print(latest_query)
            sql_query = f"""
            SELECT * FROM new_merged_course WHERE Complexity = '{complexity}'
            ORDER BY ts_rank(ts, to_tsquery('english', '{latest_query}')) DESC;
            """
            cursor.execute(sql_query)
            results = cursor.fetchmany(size=10)  # Fetch the results
        else:
            raise ValueError(f"No queries available for {user['username']}")
        

    except Exception as e:
        raise Exception(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    
    return format_course_details(results)




def execute_query_dashboard(user):
    DB_HOST = "isrpeer.ctw842oc69v3.us-east-2.rds.amazonaws.com"
    DB_NAME = "isr_books"
    DB_USER = "isr_peer"
    DB_PASS = "ISRpeer2024"

    conn = None
    results = []
    try:
        conn_string = f"host={DB_HOST} port=5432 dbname={DB_NAME} user={DB_USER} password={DB_PASS}"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        if user['categories']: 
                
                for c in user['categories']:  
                    
                    c = re.sub(r'\s+', '_', c)  # Replace one or more spaces with a single underscore
                    c = re.sub(r'[^\w\s]', '', c)  # Remove special characters
                    print(c)

                    sql_query = f"""
                    SELECT * FROM new_merged_books
                    ORDER BY ts_rank(ts, to_tsquery('english', '{c}')) DESC;
                    """
                    cursor.execute(sql_query)
                    x = cursor.fetchmany(size=5)  
                    for i in x:
                        results.append(i)
        else:
            raise ValueError(f"No categories available for {user['username']}")

    except Exception as e:
        raise Exception(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return transform_data_list(results)

def execute_online_dashboard(user):
    DB_HOST = "isrpeer.ctw842oc69v3.us-east-2.rds.amazonaws.com"
    DB_NAME = "isr_books"
    DB_USER = "isr_peer"
    DB_PASS = "ISRpeer2024"

    conn = None
    results = []
    try:
        conn_string = f"host={DB_HOST} port=5432 dbname={DB_NAME} user={DB_USER} password={DB_PASS}"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        if user['categories']: 
                
                for c in user['categories']:  
                    c = re.sub(r'\s+', '_', c)  # Replace one or more spaces with a single underscore
                    c = re.sub(r'[^\w\s]', '', c)  # Remove special characters
                    print(c)

                    sql_query = f"""
                    SELECT * FROM new_merged_course
                    ORDER BY ts_rank(ts, to_tsquery('english', '{c}')) DESC;
                    """
                    cursor.execute(sql_query)
                    x = cursor.fetchmany(size=5)  
                    for i in x:
                        results.append(i)
        else:
            raise ValueError(f"No categories available for {user['username']}")

    except Exception as e:
        raise Exception(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return format_course_details(results)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists and the password is correct using dictionary keys
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            if user['status'] == '0':  # New user
                user['status'] = '1'  # Update status to existing user
                return redirect(url_for('welcome', username=username))
            return redirect(url_for('dashboard', username=username))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        if any(u['username'] == username for u in users):
            return render_template('register.html', error='Username already exists.')

        # Add the new user as a dictionary
        new_user = {'username': username, 'password': password, 'status': '0', 'categories': [], 'queries': [], 'book_clicks':[], 'udemy_clicks':[]}
        users.append(new_user)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/welcome/<username>')
def welcome(username):
    return render_template('welcome.html', username=username)

@app.route('/dashboard/<username>')
def dashboard(username):
    # Find the user using dictionary access
    user = next((u for u in users if u['username'] == username), None)
    
    selected_level = request.form.get('level', 'Beginner')

    #
    
    recommendations1=[]
    recommendations2=[]
    recommendations_online1=[]
    recommendations_online2=[]
    if user['book_clicks'] and user ['udemy_clicks']:
        
#For books        
        recommendations1= execute_query_dashboard(user)
        recommendations2 =  transform_data_list(recommend(user))        
        


# For online
        recommendations_online1 = execute_online_dashboard(user)
        recommendations_online2= format_course_details(recommend_online(user))
        

    elif user['book_clicks']:
        
        recommendations1= execute_query_dashboard(user)
        recommendations2 =  transform_data_list(recommend(user))        
        
             
        recommendations_online1 = execute_online_dashboard(user)
        
    elif user['udemy_clicks']:
        
        recommendations_online1 = execute_online_dashboard(user)
        print(user)
        recommendations_online2= format_course_details(recommend_online(user))
        
        print("recommendations_online2",recommendations_online2)
             
        recommendations1= execute_query_dashboard(user)
    
    else:
        recommendations1= execute_query_dashboard(user)
        recommendations_online1 = execute_online_dashboard(user)

  
    indexed_recommendations1 = [{"index": i, "data": rec} for i, rec in enumerate(recommendations1)]
    indexed_recommendations2 = [{"index": i, "data": rec} for i, rec in enumerate(recommendations2)]
    indexed_recommendations_online1 =  [{"index": i, "data": rec} for i, rec in enumerate(recommendations_online1)]
    indexed_recommendations_online2 =  [{"index": i, "data": rec} for i, rec in enumerate(recommendations_online2)]

    # indexed_recommendations = [{"index": i, "data": rec} for i, rec in enumerate(recommendations)]
    # indexed_recommendations_online = [{"index": i, "data": rec} for i, rec in enumerate(recommendation_online)]

    
    #return render_template('search.html', username=username, recommendations=indexed_recommendations,recommendation_online =  indexed_recommendations_online, selected_level=selected_level)



    if user:
        return render_template('dashboard.html', username=username, categories=user['categories'], recommendations2 = indexed_recommendations2 , recommendations1 = indexed_recommendations1, recommendations_online1 = indexed_recommendations_online1, recommendations_online2 = indexed_recommendations_online2, selected_level=selected_level)
    else:
        return render_template('error.html', message='User not found')
    

@app.route('/update_categories', methods=['POST'])
def update_categories():
    data = request.json
    username = data['username']
    categories = data['categories']

    user = next((u for u in users if u['username'] == username), None)
    if user:
        user['categories'] = categories
        return jsonify({'message': 'Categories updated successfully'})
    return jsonify({'message': 'User not found'}), 404

@app.route('/search2/<username>', methods=['GET', 'POST'])
def search(username):
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        client_id = "muxVGW0Maqc4lWlD72WmaIBtLGQizFJbQCaQwaO4"
        client_secret = "Lc9CMgXeeLftUO0BVvRL6MlxhB4Ek6jrXVz27qzr1pOk0NyuGFggyKZNAhM7IRle1EDakoJkhodfhhpDgVjHv7kWdF464EwqF3asT2PttG2vjRZd0tN3HTAYaliju7Uz"
        
        # Fetch Udemy courses
        udemy = Udemy(client_id, client_secret)
        courses_data = udemy.courses(page=1, page_size=10)  # This is already JSON data

              

        query = request.form.get('query', '')
        
        selected_level = request.form.get('level', 'Beginner')
          

        user['queries'].append(query)    
        recommendation_online = execute_online_query(user,selected_level)
        recommendations = execute_query(user,selected_level)
        
        indexed_recommendations = [{"index": i, "data": rec} for i, rec in enumerate(recommendations)]
        indexed_recommendations_online = [{"index": i, "data": rec} for i, rec in enumerate(recommendation_online)]
        

        return render_template('search2.html', username=username, recommendations=indexed_recommendations,recommendation_online =  indexed_recommendations_online, query=query, selected_level=selected_level)
    return redirect(url_for('dashboard', username=username))


@app.route('/track_click/<username>', methods=['POST'])
def track_click(username):
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        return "User not found", 404
    
    if 'book_clicks' not in user:
        user['book_clicks'] = []
    print('came here')
    book_title = request.form.get('book_title')
    author_name = request.form.get('author_name')
    description = request.form.get('description')

    for entry in user['book_clicks']:
        if entry[0] == book_title:
            # If found, increment the count
            entry[3] += 1
            break
    else:
        # If not found, append a new entry to the 'book_clicks'
        user['book_clicks'].append([book_title, author_name, description, 1])

    # Print updated user data for debugging
    

    return "Click recorded", 200


@app.route('/track_udemy_click/<username>', methods=['POST'])
def track_udemy_click(username):
    course_title = request.form['course_title']
    instructor_name = request.form['instructor_name']
    headline = request.form['headline']
    user = next((user for user in users if user['username'] == username), None)

    if 'udemy_clicks' not in user:
        user['udemy_clicks'] = []

    if user:
        # Check if the course already exists in udemy_clicks
        for course in user['udemy_clicks']:
            if course[0] == course_title and course[1] == instructor_name and course[2] == headline:
                course[3] += 1
                break
        else:
            # Add new course click
            user['udemy_clicks'].append([course_title, instructor_name, headline, 1])

        
    return jsonify(success=True)




@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)


@app.template_filter('zip')
def zip_lists(a, b):
    return zip(a, b)



if __name__ == '__main__':

    
    app.run(debug=True)
    
    execute_query(users)
    execute_query_dashboard(users)
