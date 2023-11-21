from . import app
from datetime import datetime
from fastapi import Request
from .utils import get_challenge_info_by_kyu, is_challenge_id_allocated_in_database, is_group_kata_allocated_in_database, create_connection

## Routes
@app.get('/')
def index(request: Request):
    return {"message": f"Welcome {request.url._url}api/redoc"}

@app.post('/api/get_challenges')
async def get_challenges(request: Request):

    form_data = await request.form()
    
    group_name = form_data.get('group_name')
    current_datetime = datetime.now()

    date = current_datetime.strftime('%Y-%m-%d')

    # Check if a code kata for the specified group name and date exists
    existing_code_kata_url = is_group_kata_allocated_in_database(group_name, date)
    
    if existing_code_kata_url:
        return {"challenge_id": existing_code_kata_url[0], "found":"true"}

    kyu_level = form_data.get('kyu_level')
    language = form_data.get('language')
    challenge_ids = get_challenge_info_by_kyu(kyu_level, language) # this is a list

    for challenge_id in challenge_ids:
        # Check if the challenge ID is not in the database
        if not is_challenge_id_allocated_in_database(challenge_id):
            return {"challenge_id": challenge_id}

    return {"message": "No available unallocated challenge IDs."}
    
@app.post('/api/add_kata')
def add_kata(request: Request):
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

        return {"message":"Kata added to database."}

@app.get('/api/get_all_katas')
def get_all_katas(request: Request):
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

    return {'katas': katas}
