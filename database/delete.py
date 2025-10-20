import sqlite3

conn=sqlite3.connect('achidata.db')
c= conn.cursor()

try :
    c.execute('DELETE FROM users ')
    conn.commit()
    c.close()
    
except sqlite3.Error as e :
    print(e)
    
finally:
    if conn:
        conn.close()