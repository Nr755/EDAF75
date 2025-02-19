import sqlite3
import hashlib
import os
from bottle import response, get, post, run, request
import json

db = sqlite3.connect("/Users/mikolajsinicka/Desktop/EDAF75/lab3/movies.sqlite")
db.execute("PRAGMA foreign_keys = ON")
PORT = 7007

@get('/ping')
def get_ping():
    response.status = 200
    return "pong"

@post('/reset')
def reset():
    os.system('sqlite3 movies.sqlite < lab3.sql')

def hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@post('/users')
def post_users():
    user = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO       customers(username, full_name, password)
            VALUES     (?, ?, ?)
            RETURNING  username
            """,
            [user['username'], user['fullName'], hash(user['pwd'])]
        )
    except sqlite3.IntegrityError:
        response.status = 400
        return ""
    else:
        existing_user = c.fetchone()
        db.commit()
        response.status = 201
        return f"/users/{existing_user[0]}"

@post('/movies')
def post_movie():
    movie = request.json
    run_time = movie.get('runTime', 0)
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO    movies(imdb_key, title, year, run_time)
            VALUES  (?, ?, ?, ?);
            """,
            [movie['imdbKey'], movie['title'], movie['year'], run_time]
        )
    except sqlite3.IntegrityError:
        response.status = 400
        return ""
    else:
        db.commit()
        response.status = 201
        return f"/movies/{movie['imdbKey']}"

@post('/performances')
def post_performance():
    performance = request.json
    c = db.cursor()

    c.execute(
        """
        SELECT performanceId FROM performances
        WHERE imdb_key = ? AND theater = ? AND date = ? AND start_time = ?
        """,
        [performance['imdbKey'], performance['theater'], performance['date'], performance['time']]
    )
    existing_performance = c.fetchone()

    if existing_performance:
        response.status = 200
        return f"/performances/{existing_performance[0]}"

    try:
        c.execute(
            """
            INSERT INTO performances(performanceId, imdb_key, theater, date, start_time)
            VALUES (lower(hex(randomblob(16))), ?, ?, ?, ?)
            RETURNING performanceId
            """,
            [performance['imdbKey'], performance['theater'], performance['date'], performance['time']]
        )
        performanceId = c.fetchone()[0]
        db.commit()
        response.status = 201
        return f"/performances/{performanceId}"

    except sqlite3.IntegrityError:
        response.status = 400
        return "No such movie or theater"


@get('/movies')
def get_movies():
    c = db.cursor()
    c.execute(
        """
        SELECT  imdb_key, title, year
        FROM    movies
        """
    )
    movies = c.fetchall()

    movies_list = [
        {"imdbKey": imdb_key, "title": title, "year": year}
        for (imdb_key, title, year) in movies
    ]

    response.content_type = "application/json"
    return json.dumps({"data": movies_list}, indent = 4)

@get('/movies/<imdb_key>')
def get_movies(imdb_key):
    c = db.cursor()
    c.execute(
        """
        SELECT imdb_key, title, year
        FROM movies
        WHERE imdb_key = ?
        """,
        [imdb_key]
    )
    
    movie = [
        {"imdbKey": imdb_key, "title": movie_name, "year": production_year}
        for imdb_key, movie_name, production_year in c
    ]
    
    if not movie:
        response.status = 404
        return {"data": []}

    response.content_type = "application/json"
    return json.dumps({"data": movie}, indent = 4)

@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute(
            """
            SELECT 
                p.performanceId,
                p.date,
                p.start_time AS startTime,
                m.title,
                m.year,
                p.theater,
                t.capacity - COALESCE(s.sold_tickets, 0) AS remainingSeats
            FROM performances p
            JOIN movies m ON p.imdb_key = m.imdb_key
            JOIN theaters t ON p.theater = t.name
            LEFT JOIN (
                SELECT performanceId, COUNT(*) AS sold_tickets
                FROM tickets
                GROUP BY performanceId
            ) s ON p.performanceId = s.performanceId
            """
        )

    fetched_data = c.fetchall()

    if not fetched_data:
        response.status = 200
        return json.dumps({"data": []}, indent=4)

    performances = [
        {
            "performanceId": performanceId,
            "date": date,
            "startTime": start_time,
            "title": title,
            "year": year,
            "theater": theater,
            "remainingSeats": remaining_seats
        }
        for performanceId, date, start_time, title, year, theater, remaining_seats in fetched_data
    ]

    response.content_type = "application/json"
    return json.dumps({"data": performances}, indent=4)

@post('/tickets')
def post_tickets():
    return "Not implemented"

@get('/users/<username>/tickets')
def get_tickets(username):
    return "Not implemented"

run(host = 'localhost', port = PORT)