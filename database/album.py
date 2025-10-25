# create_album_db.py
import sqlite3, os

BASE = os.path.dirname(__file__)
DB    = os.path.join(BASE, "album_data.db")
ASSET = os.path.join(BASE, "assets")   # โฟลเดอร์เก็บรูป
os.makedirs(ASSET, exist_ok=True)

conn = sqlite3.connect(DB)
cur  = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS albums (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  group_name  TEXT NOT NULL,
  album_name  TEXT NOT NULL,
  version     TEXT,
  price       REAL,
  stock       INTEGER,
  cover_path  TEXT          -- << เก็บพาธรูป
)
""")

# NOTE: วางไฟล์รูปไว้ใน ./assets/ ให้ชื่อไฟล์ตามนี้หรือเปลี่ยนชื่อได้
seed = [
  ("BTS",       "Love Yourself: Answer", "Ver.S",     750, 20, os.path.join(ASSET, "bts_answer.png")),
  ("BTS",       "Map of the Soul: 7",    "Ver.2",     820, 15, os.path.join(ASSET, "bts_mots7.png")),
  ("BLACKPINK", "THE ALBUM",             "Black Ver.",790, 18, os.path.join(ASSET, "bp_the_album.png")),
  ("SEVENTEEN", "Face the Sun",          "Ray Ver.",  770, 25, os.path.join(ASSET, "svt_fts.png")),
  ("AESPA",     "MY WORLD",               "Zine Ver.", 660, 12, os.path.join(ASSET, "aespa_myworld.png")),
  ("ENHYPEN",   "Dark Blood",            "Engene Ver.",690, 22, os.path.join(ASSET, "enhypen_darkblood.png")),
  ("TWICE",     "Formula of Love",       "Study Ver.",750, 10, os.path.join(ASSET, "twice_fol.png")),
]

# ใส่เฉพาะถ้ายังว่าง
count = cur.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
if count == 0:
    cur.executemany(
      "INSERT INTO albums(group_name,album_name,version,price,stock,cover_path) VALUES (?,?,?,?,?,?)",
      seed
    )
    conn.commit()
    print("✅ Seeded:", len(seed), "rows")
else:
    print("ℹ️ มีข้อมูลแล้ว:", count, "rows (ไม่ใส่ซ้ำ)")

conn.close()
print("✅ DB สร้างแล้วที่", DB)