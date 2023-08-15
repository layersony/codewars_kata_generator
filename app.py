from flask import Flask, render_template, request, jsonify
import requests, random, datetime, psycopg2
from bs4 import BeautifulSoup

app = Flask(__name__)

# Create a connection to the database
def create_connection():
    conn = psycopg2.connect(
        database="codekatas",
        user="theElite",
        password="theElite",
        host="localhost",
        port="5433"
    )
    return conn

def get_challenge_info_by_kyu(kyu_level):
    url = f'https://www.codewars.com/kata/search/?q=&r%5B%5D=-{kyu_level}&order_by=sort_date%20desc'

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_challenges', methods=['POST'])
def get_challenges():
    if request.method == 'POST':
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
    cur = conn.cursor()

    if request.method == 'POST':
        date = datetime.datetime.now().date()
        group_name = request.form['group_name']
        code_kata_url = request.form['code_kata_url']
        kyu = request.form['kyu']

        query = "INSERT INTO katas (date, group_name, code_kata_url, kyu) VALUES (%s, %s, %s, %s);"
        cur.execute(query, (date, group_name, code_kata_url, kyu))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify("Kata added to database.")

if __name__ == '__main__':
    app.run()
