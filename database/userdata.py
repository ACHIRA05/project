import sqlite3,os
conn = sqlite3.connect('Userdata.db')
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT UNIQUE NOT NULL,
  password      TEXT NOT NULL,
  first_name    TEXT,
  last_name     TEXT,
  gender        TEXT,  
  birth_date    TEXT,    
  email         TEXT UNIQUE NOT NULL,
  phone         TEXT UNIQUE NOT NULL,
  profile_image BLOB
)""")
conn.commit()
conn.close()
