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
        SELECT p.performanceId, p.imdb_key, p.theater, p.date, p.start_time, t.capacity - COALESCE(s.sold_tickets, 0) AS remaining_seats
        FROM performances p
        JOIN theaters t ON p.theater = t.name
        LEFT JOIN (
            SELECT performanceId, COUNT(*) AS sold_tickets
            FROM tickets
            GROUP BY performanceId
        ) s ON p.performanceId = s.performanceId
        """
    )
    
    performances = c.fetchall()
    performances_list = [
        {
            "performanceId": p_id,
            "imdbKey": imdb_key,
            "theater": theater,
            "date": date,
            "startTime": start_time,
            "remainingSeats": remaining_seats
        }
        for p_id, imdb_key, theater, date, start_time, remaining_seats in performances
    ]

    response.content_type = "application/json"
    return json.dumps({"data": performances_list}, indent=4)

@post('/tickets')
def post_ticket():
    ticket_request = request.json
    username = ticket_request.get("username")
    password = ticket_request.get("pwd")
    performance_id = ticket_request.get("performanceId")

    c = db.cursor()
    c.execute(
        """
        SELECT username FROM customers
        WHERE username = ? AND password = ?
        """,
        (username, hashlib.sha256(password.encode('utf-8')).hexdigest())
    )
    existing_user = c.fetchone()

    if not existing_user:
        response.status = 401
        return "Wrong user credentials"
    
    c.execute(
        """
        SELECT (t.capacity - COALESCE(s.sold_tickets, 0)) AS remaining_seats
        FROM performances p
        JOIN theaters t ON p.theater = t.name
        LEFT JOIN (
            SELECT performanceId, COUNT(*) AS sold_tickets
            FROM tickets
            GROUP BY performanceId
        ) s ON p.performanceId = s.performanceId
        WHERE p.performanceId = ?
        """,
        (performance_id,)
    )

    seat_check = c.fetchone()
    if not seat_check:
        response.status = 400
        return "Performance does not exist"
    remaining_seats = seat_check[0]

    if remaining_seats <= 0:
        response.status = 400
        return "No tickets left"

    try:
        c.execute(
            """
            INSERT INTO tickets(id, username, performanceId, date_and_time)
            VALUES (lower(hex(randomblob(16))), ?, ?, CURRENT_TIMESTAMP)
            RETURNING id
            """,
            (username, performance_id)
        )

        new_ticket = c.fetchone()
        if new_ticket:
            db.commit()
            response.status = 201
            return f"/tickets/{new_ticket[0]}"

    except sqlite3.Error as e:
        response.status = 400
        return "Error"

@get('/users/<username>/tickets')
def get_tickets(username):
    c = db.cursor()
    c.execute(
        """
        SELECT p.imdb_key, p.theater, p.date, p.start_time, COUNT(*) as nbrOfTickets
        FROM tickets t
        JOIN performances p ON t.performanceId = p.performanceId
        WHERE t.username = ?
        GROUP BY p.imdb_key, p.theater, p.date, p.start_time
        """,
        (username,)
    )

    tickets = c.fetchall()
    tickets_list = [
        {
            "imdbKey": imdb_key,
            "theater": theater,
            "date": date,
            "startTime": start_time,
            "nbrOfTickets": nbr_of_tickets
        }
        for imdb_key, theater, date, start_time, nbr_of_tickets in tickets
    ]

    response.content_type = "application/json"
    return json.dumps({"data": tickets_list}, indent=4)

run(host = 'localhost', port = PORT)