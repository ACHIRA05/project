import sqlite3
import os

DB = "Userdata.db"

def fix_user_table():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 1) รีเนมตารางเดิมเก็บไว้ก่อน
    cur.execute("ALTER TABLE users RENAME TO users_old")

    # 2) สร้างตารางใหม่ตามที่ต้องการ
    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            birth_date TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            profile_image BLOB
        )
    """)

    # 3) ย้ายข้อมูลจากตารางเก่า (map เฉพาะคอลัมน์ที่มี)
    cur.execute("""
        INSERT INTO users (id, username, password, email, phone, profile_image)
        SELECT id, username, password, email, phone, profile_image
        FROM users_old
    """)

    # 4) ลบทิ้งตารางเก่า
    cur.execute("DROP TABLE users_old")

    con.commit()
    con.close()
    print("✅ users table fixed successfully!")

if __name__ == "__main__":
    fix_user_table()