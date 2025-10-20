import os,sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db")
DB_PATH = os.path.abspath(DB_PATH)

conn=sqlite3.connect(DB_PATH)
c= conn.cursor()

try :
    data=('achira','acpo011148',1)
    c.execute('''UPDATE users SET username =?,password =? WHERE id =?''',data)
    conn.commit()
    c.close()
    
except sqlite3.Error as e :
    print(e)
    
finally:
    if conn:
        conn.close()