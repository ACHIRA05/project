import sqlite3,os
print('ABS PATH =', os.path.abspath('Userdata.db')) 
conn = sqlite3.connect('Userdata.db')
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        profile_image BLOB)""")
conn.commit()
conn.close()