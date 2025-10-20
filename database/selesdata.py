import sqlite3
conn = sqlite3.connect('Selesdata.db')
c = conn.cursor()
c.execute ('''CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY AUTOINCREMENT,
        user_id varchar(30) NOT NULL,
        subtotal varchar(30) NOT NULL,
        total    varchar(30) NOT NULL,
        created_at    varchar(30) NOT NULL)''')