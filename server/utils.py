from bs4 import BeautifulSoup 
import requests
from decouple import config
import psycopg2

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

def get_challenge_info_by_kyu(kyu_level, language):
    for pageno in range(1, 100):
        url = f'https://www.codewars.com/kata/search/{language}?q=&r%5B%5D=-{kyu_level}&order_by=sort_date+desc&page={pageno}'
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
