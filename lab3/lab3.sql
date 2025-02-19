-- First we drop everything from the tables in case anything exists

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS screening;

PRAGMA foreign_keys = ON;

-- We now create the blank tables

CREATE TABLE customers(
    username    TEXT NOT NULL,
    full_name   TEXT NOT NULL,
    password    TEXT NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE movies(
    imdb_key    TEXT NOT NULL,
    title       TEXT NOT NULL,
    year        INT NOT NULL,
    run_time    INT NOT NULL,
    PRIMARY KEY (imdb_key)
);

CREATE TABLE theaters(
    name        TEXT NOT NULL,
    capacity    INT NOT NULL,
    PRIMARY KEY (name)
);

CREATE TABLE performances(
    performanceId   TEXT DEFAULT (lower(hex(randomblob(16)))),
    start_time      TIME NOT NULL,
    theater         TEXT NOT NULL,
    date            DATE NOT NULL,
    imdb_key        TEXT NOT NULL,
    PRIMARY KEY     (performanceId)
    FOREIGN KEY     (theater) REFERENCES theaters(name)
    FOREIGN KEY     (imdb_key) REFERENCES movies(imdb_key)
);

CREATE TABLE tickets(
    id              TEXT DEFAULT (lower(hex(randomblob(16)))),
    username        TEXT NOT NULL,
    performanceId   TEXT NOT NULL,
    PRIMARY KEY     (id),
    FOREIGN KEY     (username) REFERENCES customers(username),
    FOREIGN KEY     (performanceId) REFERENCES performances(performanceId)
);

-- We insert stuff into the tables

INSERT
INTO    theaters(name, capacity)
VALUES  ('Kino', 10),
        ('Regal', 16),
        ('Skandia', 100);