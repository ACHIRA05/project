# seed_albums_update.py  (วางไฟล์นี้ไว้ตรงไหนก็ได้ในโปรเจกต์)
import sqlite3, os

# ตั้งค่าพาธฐานของโปรเจกต์
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "album_data.db")
BTS_ASSET   = os.path.join(PROJECT_ROOT, "assets","bts_album")
BLACKPINK_ASSET =  os.path.join(PROJECT_ROOT, "assets","blackpink_album")
SEVENTEEN_ASSET = os.path.join(PROJECT_ROOT, "assets","seventeen_album")
AESPA_ASSET = os.path.join(PROJECT_ROOT, "assets","aespa_album")
ENHYPEN_ASSET = os.path.join(PROJECT_ROOT, "assets","enhypen_album")
TWICE_ASSET = os.path.join(PROJECT_ROOT, "assets","twice_album")
# เผื่อโฟลเดอร์ database ยังไม่มี
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(BTS_ASSET,BLACKPINK_ASSET,SEVENTEEN_ASSET,AESPA_ASSET,ENHYPEN_ASSET,TWICE_ASSET, exist_ok=True)

seed = [
  # BTS
  ("BTS","Love Yourself: Her","E Ver.",680,18, os.path.join(BTS_ASSET,"Love_Yourself_Her.Jpg")),
  ("BTS","Love Yourself: Tear","Y Ver.",720,15, os.path.join(BTS_ASSET,"Love_Yourself_Tear.Jpg")),
  ("BTS","Love Yourself: Answer","S Ver.",750,20, os.path.join(BTS_ASSET,"Love_Yourself_Answer.Jpg")),
  ("BTS","Map of the Soul: Persona","L Ver.",800,12, os.path.join(BTS_ASSET,"Map _of_the_Soul_Persona.Jpg")),
  ("BTS","Map of the Soul: 7","Ver.2",820,15, os.path.join(BTS_ASSET,"Map_of_the_Soul_7.Jpg")),
  ("BTS","BE","Deluxe Ver.",670,10, os.path.join(BTS_ASSET,"BE.Jpg")),
  ("BTS","Butter","Promo Ver.",600,25, os.path.join(BTS_ASSET,"BUTTER.Jpg")),
  ("BTS","Proof","Standard Ver.",890,8, os.path.join(BTS_ASSET,"Proof.Jpg")),
  ("BTS","Wings","Y Ver.",650,22, os.path.join(BTS_ASSET,"Wings.Jpg")),
  ("BTS","Skool Luv Affair","Special Edition",620,16, os.path.join(BTS_ASSET,"Skool_Luv_Affair.J")),

  # BLACKPINK
  ("BLACKPINK","Square Up","Standard Ver.",720,14, os.path.join(BLACKPINK_ASSET,"bp_square_up.png")),
  ("BLACKPINK","Kill This Love","CD+DVD Ver.",780,12, os.path.join(BLACKPINK_ASSET,"bp_kill_this_love.png")),
  ("BLACKPINK","THE ALBUM","Black Ver.",790,18, os.path.join(BLACKPINK_ASSET,"bp_the_album.png")),
  ("BLACKPINK","Born Pink","Box Set Ver.",850,10, os.path.join(BLACKPINK_ASSET,"bp_born_pink.png")),
  ("BLACKPINK","BLACKPINK 2019-2020 Repackage","Repackage Ver.",730,13, os.path.join(BLACKPINK_ASSET,"bp_2019_2020.png")),
  ("BLACKPINK","Kill This Love (Re-package)","Re Ver.",760,20, os.path.join(BLACKPINK_ASSET,"bp_kill_this_love_re.png")),
  ("BLACKPINK","How You Like That","Standard Ver.",700,19, os.path.join(BLACKPINK_ASSET,"bp_how_you_like_that.png")),
  ("BLACKPINK","Square Two","Standard Ver.",680,17, os.path.join(BLACKPINK_ASSET,"bp_square_two.png")),
  ("BLACKPINK","Blackpink in Your Area","Limited Ver.",810,9, os.path.join(BLACKPINK_ASSET,"bp_in_your_area.png")),
  ("BLACKPINK","Light Up the Sky","Digital Ver.",650,21, os.path.join(BLACKPINK_ASSET,"bp_light_up_the_sky.png")),

  # SEVENTEEN
  ("SEVENTEEN","Love & Letter","Alpha Ver.",630,20, os.path.join(SEVENTEEN_ASSET,"svt_love_letter.png")),
  ("SEVENTEEN","Teen, Age","Standard Ver.",670,18, os.path.join(SEVENTEEN_ASSET,"svt_teen_age.png")),
  ("SEVENTEEN","An Ode","Standard Ver.",720,14, os.path.join(SEVENTEEN_ASSET,"svt_an_ode.png")),
  ("SEVENTEEN","Heng:garæ","Deluxe Ver.",790,11, os.path.join(SEVENTEEN_ASSET,"svt_heng_garae.png")),
  ("SEVENTEEN","Face the Sun","Ray Ver.",770,25, os.path.join(SEVENTEEN_ASSET,"svt_fts.png")),
  ("SEVENTEEN","Attacca","Standard Ver.",760,16, os.path.join(SEVENTEEN_ASSET,"svt_attacca.png")),
  ("SEVENTEEN","Your Choice","Standard Ver.",750,17, os.path.join(SEVENTEEN_ASSET,"svt_your_choice.png")),
  ("SEVENTEEN","FML","Standard Ver.",830,10, os.path.join(SEVENTEEN_ASSET,"svt_fml.png")),
  ("SEVENTEEN","Semicolon","Standard Ver.",700,19, os.path.join(SEVENTEEN_ASSET,"svt_semicolon.png")),
  ("SEVENTEEN","17 Carat","Debut Ver.",620,22, os.path.join(SEVENTEEN_ASSET,"svt_17carat.png")),

  # AESPA
  ("AESPA","Savage","Standard Ver.",640,20, os.path.join(AESPA_ASSET,"aespa_savage.png")),
  ("AESPA","Next Level","Standard Ver.",610,22, os.path.join(AESPA_ASSET,"aespa_next_level.png")),
  ("AESPA","Girls","Standard Ver.",630,24, os.path.join(AESPA_ASSET,"aespa_girls.png")),
  ("AESPA","MY WORLD","Zine Ver.",660,12, os.path.join(AESPA_ASSET,"aespa_myworld.png")),
  ("AESPA","Drama","Standard Ver.",650,21, os.path.join(AESPA_ASSET,"aespa_drama.png")),
  ("AESPA","Hot Air","Standard Ver.",620,23, os.path.join(AESPA_ASSET,"aespa_hot_air.png")),
  ("AESPA","Black Mamba","Standard Ver.",600,26, os.path.join(AESPA_ASSET,"aespa_black_mamba.png")),
  ("AESPA","Forever","Standard Ver.",640,18, os.path.join(AESPA_ASSET,"aespa_forever.png")),
  ("AESPA","New Norm","Standard Ver.",630,19, os.path.join(AESPA_ASSET,"aespa_new_norm.png")),
  ("AESPA","Savage (Re-package)","Re Ver.",670,14, os.path.join(AESPA_ASSET,"aespa_savage_re.png")),

  # ENHYPEN
  ("ENHYPEN","BORDER : DAY ONE","Standard Ver.",650,23, os.path.join(ENHYPEN_ASSET,"enh_bord_day_one.png")),
  ("ENHYPEN","BORDER : CARNIVAL","Carnival Ver.",680,20, os.path.join(ENHYPEN_ASSET,"enh_border_carnival.png")),
  ("ENHYPEN","DIMENSION : DILEMMA","Standard Ver.",720,17, os.path.join(ENHYPEN_ASSET,"enh_dimension_dilemma.png")),
  ("ENHYPEN","DIMENSION : ANSWER","Answer Ver.",740,13, os.path.join(ENHYPEN_ASSET,"enh_dimension_answer.png")),
  ("ENHYPEN","DRIVE : 0","Standard Ver.",690,19, os.path.join(ENHYPEN_ASSET,"enh_drive_zero.png")),
  ("ENHYPEN","FATE : FINAL","Standard Ver.",710,12, os.path.join(ENHYPEN_ASSET,"enh_fate_final.png")),
  ("ENHYPEN","BORDER : DAY ONE (Ver.2)","Ver.2",670,22, os.path.join(ENHYPEN_ASSET,"enh_border_dayone2.png")),
  ("ENHYPEN","DIMENSION : DILEMMA (Ver.2)","Ver.2",730,14, os.path.join(ENHYPEN_ASSET,"enh_dimension_dilemma2.png")),
  ("ENHYPEN","Fate : (For) Winners","Standard Ver.",700,18, os.path.join(ENHYPEN_ASSET,"enh_fate_for_winners.png")),
  ("ENHYPEN","Polaroid Love","Standard Ver.",640,24, os.path.join(ENHYPEN_ASSET,"enh_polaroid_love.png")),

  # TWICE
  ("TWICE","Twicetagram","Standard Ver.",640,21, os.path.join(TWICE_ASSET,"twice_twicetagram.png")),
  ("TWICE","What is Love?","Standard Ver.",670,18, os.path.join(TWICE_ASSET,"twice_what_is_love.png")),
  ("TWICE","YES or YES","Standard Ver.",680,17, os.path.join(TWICE_ASSET,"twice_yes_or_yes.png")),
  ("TWICE","FANCY YOU","Standard Ver.",710,14, os.path.join(TWICE_ASSET,"twice_fancy_you.png")),
  ("TWICE","Formula of Love","Study Ver.",750,10, os.path.join(TWICE_ASSET,"twice_fol.png")),
  ("TWICE","MORE & MORE","Standard Ver.",720,16, os.path.join(TWICE_ASSET,"twice_more_and_more.png")),
  ("TWICE","Eyes Wide Open","Standard Ver.",760,12, os.path.join(TWICE_ASSET,"twice_eyes_wide_open.png")),
  ("TWICE","Feel Special","Standard Ver.",730,15, os.path.join(TWICE_ASSET,"twice_feel_special.png")),
  ("TWICE","Taste of Love","Standard Ver.",740,13, os.path.join(TWICE_ASSET,"twice_taste_of_love.png")),
  ("TWICE","READY TO TWICE","Standard Ver.",690,19, os.path.join(TWICE_ASSET,"twice_ready_to_twice.png")),
]

def ensure_schema(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS albums (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      group_name  TEXT NOT NULL,
      album_name  TEXT NOT NULL,
      version     TEXT,
      price       REAL,
      stock       INTEGER,
      cover_path  TEXT
    )
    """)
    # ดักไม่ให้ซ้ำ (ถ้ามี index แล้ว จะไม่สร้างซ้ำ)
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_albums_unique
      ON albums(group_name, album_name, version)
    """)

def main():
    print("DB_PATH =>", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # กันเหนียว สร้างตาราง/unique index
    ensure_schema(cur)

    inserted = skipped = 0
    for g, a, v, p, s, c in seed:
        cur.execute("""
          INSERT OR IGNORE INTO albums(group_name, album_name, version, price, stock, cover_path)
          VALUES (?,?,?,?,?,?)
        """, (g, a, v, p, s, c))
        if cur.rowcount == 0:
            skipped += 1
            print(f"⏭️  Skipped (exists): {g} – {a} ({v})")
        else:
            inserted += 1
            print(f"✅ Added: {g} – {a} ({v})")

    conn.commit()
    conn.close()
    print(f"Done. inserted={inserted}, skipped={skipped}")

if __name__ == "__main__":
    main()