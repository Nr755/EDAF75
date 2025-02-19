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
    try:
        c.execute(
            """
            INSERT
            INTO        performances(imdb_key, theater, date, start_time)
            VALUES      (?, ?, ?, ?)
            RETURNING   id
            """,
            [performance['imdbKey'], performance['theater'], performance['date'], performance['time']]
        )
    except sqlite3.IntegrityError:
        response.status = 400
        return "No such movie or theater"
    else:
        id = c.fetchone()[0]
        db.commit()
        response.status = 201
        return f"/performances/{id}"

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
    return json.dumps({"data": movies_list})

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
    return json.dumps({"data": movie})


@get('/performances')
def get_performances():
    return "Not implemented"

@post('/tickets')
def post_tickets():
    return "Not implemented"

@get('/users/<username>/tickets')
def get_tickets(username):
    return "Not implemented"

run(host = 'localhost', port = PORT)