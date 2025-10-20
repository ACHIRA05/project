import sqlite3
conn = sqlite3.connect('Albumsdata.db')
c = conn.cursor()
c.execute ('''CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY AUTOINCREMENT,
        sku        varchar(30) NOT NULL ,
        group_name varchar(30) NOT NULL,
        album_name varchar(30) NOT NULL,
        version    varchar(30) NOT NULL,
        release    varchar(30) NOT NULL,
        price      varchar(30) NOT NULL,
        stock      varchar(30) NOT NULL)''')