from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests, sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from decouple import config
import psycopg2

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

CORS(app, origins=['*'])

# Read database connection variables from .env
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')

# Create a connection to the database
def create_connection():
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def get_challenge_info_by_kyu(kyu_level):
    for pageno in range(30):
        url = f'https://www.codewars.com/kata/search/?q=&r%5B%5D=-{kyu_level}&beta=false&order_by=sort_date+desc&page={pageno}'

        response = requests.get(url)
        codewarIds = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            div_elements = soup.find_all('div', class_='list-item-kata')

            for div_element in div_elements:
                challenge_id = div_element.get('id')
                codewarIds.append(challenge_id)
                    
        return codewarIds

def is_challenge_id_allocated_in_database(challenge_id):
    conn = create_connection()
    cur = conn.cursor()

    query = "SELECT code_kata_url FROM katas WHERE code_kata_url = %s;"
    cur.execute(query, (challenge_id,))
    existing_challenge_id = cur.fetchone()

    cur.close()
    conn.close()

    return existing_challenge_id is not None

def is_group_kata_allocated_in_database(group_name, date):
    conn = create_connection()
    cur = conn.cursor()

    query = "SELECT code_kata_url FROM katas WHERE group_name = %s AND date = %s;"
    cur.execute(query, (group_name, date))
    existing_code_kata_url = cur.fetchone()

    cur.close()
    conn.close()

    return existing_code_kata_url

## Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_challenges', methods=['POST'])
def get_challenges():
    if request.method == 'POST':
        group_name = request.form['group_name']
        current_datetime = datetime.now()

        date = current_datetime.strftime('%Y-%m-%d')

        # Check if a code kata for the specified group name and date exists
        existing_code_kata_url = is_group_kata_allocated_in_database(group_name, date)
        
        if existing_code_kata_url:
            return jsonify({"challenge_id": existing_code_kata_url[0], "found":"true"})

        kyu_level = request.form['kyu_level']
        challenge_ids = get_challenge_info_by_kyu(kyu_level) # this is a list

        for challenge_id in challenge_ids:
            # Check if the challenge ID is not in the database
            if not is_challenge_id_allocated_in_database(challenge_id):
                return jsonify({"challenge_id": challenge_id})

        return jsonify({"message": "No available unallocated challenge IDs."})
    
@app.route('/api/add_kata', methods=['POST'])
def add_kata():
    conn = create_connection() 

    if request.method == 'POST':
        current_datetime = datetime.now()

        date = current_datetime.strftime('%Y-%m-%d')
        group_name = request.form['group_name']
        code_kata_url = request.form['code_kata_url']
        kyu = request.form['kyu']

        query = "INSERT INTO katas (date, group_name, code_kata_url, kyu) VALUES (%s, %s, %s, %s);"
        cur = conn.cursor()
        cur.execute(query, (date, group_name, code_kata_url, kyu))
        conn.commit()
        cur.close()

        conn.close()

        return jsonify("Kata added to database.")

@app.route('/api/get_all_katas', methods=['GET'])
def get_all_katas():
    date_param = request.args.get('date')
    conn = create_connection()
    cur = conn.cursor()

    if date_param:
        query = "SELECT * FROM katas WHERE date = %s ORDER BY id ASC;"
        cur.execute(query, (date_param,))
    else:
        query = "SELECT * FROM katas ORDER BY id DESC;"
        cur.execute(query)

    katas = []
    for row in cur.fetchall():
        kata = {
            'date': row[1],
            'group_name': row[2],
            'code_kata_url': row[3],
            'kyu': row[4]
        }
        katas.append(kata)

    cur.close()
    conn.close()

    return jsonify({'katas': katas})

if __name__ == '__main__':
    app.run()
