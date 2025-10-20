import sqlite3
conn = sqlite3.connect('Selitemata.db')
c = conn.cursor()
c.execute ('''CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY AUTOINCREMENT,
        sale_id varchar(30) NOT NULL,
        album_id varchar(30) NOT NULL,
        qty    varchar(30) NOT NULL,
        unit_price    varchar(30) NOT NULL)''')