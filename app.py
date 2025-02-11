from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'SuperSecret'

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'palachick_db')
DB_USER = os.getenv('DB_USER', 'palachick')
DB_PASS = os.getenv('DB_PASS', '20power')
DB_PORT = os.getenv('DB_PORT', 5432)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

headers_map_museums_with_subjects = {
    'id': '№',
    'museum_name': 'Название музея',
    'foundation_year': 'Год основания',
    'city': 'Город',
    'museum_type': 'Тип музея',
    'visitors_per_year': 'Кол-во посетителей',
    'museum_area': 'Площадь музея',
    'ticket_price': 'Стоимость билета',
    'director': 'Директор',
    'capital': 'Центр субъекта',
    'federal_district': 'Федеральный округ',
    'gdp': 'ВВП',
    'density': 'Плотность',
    'official_language': 'Официальный язык',
    'population': 'Численность',
    'region_type': 'Тип субъекта',
    'subject_name': 'Название субъекта',
    'name': 'Название',
    'area': 'Площадь',
    'subject_area' : 'Площадь'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    user = request.form['user']
    password = request.form['password']

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=user,
            password=password,
            port=DB_PORT
        )
        session['user'] = user
        return redirect(url_for('home'))
    except psycopg2.Error as e:
        flash("Ошибка подключения к базе данных: " + str(e))
        return redirect(url_for('login_form'))  # Вернуться к форме логина

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('home.html')

@app.route('/home/view', methods=['GET'])
@login_required
def get_museums_with_subjects():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM museums_with_subjects;')
            museums_with_subjects = cursor.fetchall()

            column_names = [desc[0] for desc in cursor.description]
            headers = [headers_map_museums_with_subjects.get(name, name) for name in column_names]

    return render_template('table.html', headers=headers, rows=museums_with_subjects)

@app.route('/home/museums', methods=['GET'])
@login_required
def get_museums():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM museums;')
            museums = cursor.fetchall()

            column_names = [desc[0] for desc in cursor.description]
            headers = [headers_map_museums_with_subjects.get(name, name) for name in column_names]

    return render_template('table.html', headers=headers, rows=museums)

@app.route('/home/museums/<int:id>', methods=['GET'])
@login_required
def get_museum_by_id(id):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM museums WHERE id = %s;', (id,))
            museum = cursor.fetchone()

    if museum is None:
        return "Museum not found", 404

    column_names = [desc[0] for desc in cursor.description]
    headers = [headers_map_museums_with_subjects.get(name, name) for name in column_names]

    return render_template('table.html', headers=headers, rows=[museum])

@app.route('/home/subjects', methods=['GET'])
@login_required
def get_subjects():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM subjects;')
            subjects = cursor.fetchall()

            column_names = [desc[0] for desc in cursor.description]
            headers = [headers_map_museums_with_subjects.get(name, name) for name in column_names]

    return render_template('table.html', headers=headers, rows=subjects)

@app.route('/home/subjects/<int:id>', methods=['GET'])
@login_required
def get_subject_by_id(id):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM subjects WHERE id = %s;', (id,))
            subject = cursor.fetchone()

    if subject is None:
        return "Subject not found", 404

    column_names = [desc[0] for desc in cursor.description]
    headers = [headers_map_museums_with_subjects.get(name, name) for name in column_names]

    return render_template('table.html', headers=headers, rows=[subject])

if __name__ == '__main__':
    app.run(debug=True, port=10000)
