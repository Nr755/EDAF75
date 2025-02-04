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

CREATE TABLE screening(
    id              TEXT DEFAULT (lower(hex(randomblob(16)))),
    start_time      TIME NOT NULL,
    theatre         TEXT NOT NULL,
    date            DATE NOT NULL,
    imdb_key        TEXT NOT NULL,
    PRIMARY KEY     (id)
    FOREIGN KEY     (theatre) REFERENCES theaters(name)
    FOREIGN KEY     (imdb_key) REFERENCES movies(imdb_key)
);

CREATE TABLE tickets(
    id              TEXT DEFAULT (lower(hex(randomblob(16)))),
    username        TEXT NOT NULL,
    date_and_time   TEXT NOT NULL,
    PRIMARY KEY     (id)
    FOREIGN KEY     (username) REFERENCES customers(username)
    FOREIGN KEY     (date_and_time) REFERENCES screening(id)
);

-- We insert stuff into the tables

INSERT OR REPLACE
INTO customers(username, full_name, password)
VALUES  ('miko', 'Mikolaj Sinicka', 'pass1'),
        ('ergus', 'Erik Gustavsson', 'pass2'),
        ('ludde', 'Ludwig Lundstedt', 'pass3');

INSERT OR REPLACE
INTO movies(imdb_key, title, year, run_time)
VALUES  ('tt1856101', 'Blade Runner 2049', 2017, 164),
        ('tt0056058', 'Harakiri', 1962, 133),
        ('tt0034583', 'Casablanca', 1942, 102),
        ('tt0100339', 'Patlabor: The Movie', 1989, 100),
        ('tt0033467', 'Citizen Kane', 1941, 119);

INSERT OR REPLACE
INTO theaters(name, capacity)
VALUES  ('Filmstaden Lund', 200),
        ('Filmstaden Malmö', 400),
        ('Kino', 150);

INSERT OR REPLACE
INTO screening(id, start_time, theatre, date, imdb_key)
VALUES  (lower(hex(randomblob(16))),  '10:00', 'Filmstaden Lund',   '2025-03-01', 'tt1856101'),
        (lower(hex(randomblob(16))),  '11:30', 'Filmstaden Malmö',  '2025-03-01', 'tt0056058'),
        (lower(hex(randomblob(16))),  '13:00', 'Kino',              '2025-03-01', 'tt0034583'),
        (lower(hex(randomblob(16))),  '14:30', 'Filmstaden Lund',   '2025-03-02', 'tt0100339'),
        (lower(hex(randomblob(16))),  '16:00', 'Filmstaden Malmö',  '2025-03-02', 'tt0033467'),
        (lower(hex(randomblob(16))),  '17:30', 'Kino',              '2025-03-02', 'tt1856101'),
        (lower(hex(randomblob(16))),  '19:00', 'Filmstaden Lund',   '2025-03-03', 'tt0056058'),
        (lower(hex(randomblob(16))),  '20:30', 'Filmstaden Malmö',  '2025-03-03', 'tt0034583'),
        (lower(hex(randomblob(16))),  '22:00', 'Kino',              '2025-03-03', 'tt0100339'),
        (lower(hex(randomblob(16))),  '10:15', 'Filmstaden Lund',   '2025-03-04', 'tt0033467'),
        (lower(hex(randomblob(16))),  '12:45', 'Filmstaden Malmö',  '2025-03-04', 'tt1856101'),
        (lower(hex(randomblob(16))),  '15:00', 'Kino',              '2025-03-04', 'tt0056058'),
        (lower(hex(randomblob(16))),  '17:15', 'Filmstaden Lund',   '2025-03-05', 'tt0034583'),
        (lower(hex(randomblob(16))),  '19:30', 'Filmstaden Malmö',  '2025-03-05', 'tt0100339'),
        (lower(hex(randomblob(16))),  '21:45', 'Kino',              '2025-03-05', 'tt0033467');