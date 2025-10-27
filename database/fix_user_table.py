import os, sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH  = os.path.join(BASE_DIR, "database", "Userdata.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def ensure_schema():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # สร้างตาราง (ถ้ายังไม่มี)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username      TEXT PRIMARY KEY
        )
    """)
    # ดูคอลัมน์ปัจจุบัน
    cur.execute("PRAGMA table_info(users)")
    have = {r[1] for r in cur.fetchall()}

    # เฉพาะคอลัมน์ที่เราต้องใช้ (แบบเบสิค)
    required = {
        "password":      "TEXT",  
        "first_name":    "TEXT",
        "last_name":     "TEXT",
        "gender":        "TEXT",  
        "birth_date":    "TEXT",  
        "age":           "INTEGER",
        "email":         "TEXT",
        "phone":         "iNTEGER",
        "profile_image": "BLOB"
    }

    for col, typ in required.items():
        if col not in have:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")

    con.commit()
    con.close()

if __name__ == "__main__":
    ensure_schema()
    print("users table is ready.")
