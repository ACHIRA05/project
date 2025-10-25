# create_album_db.py
import sqlite3, os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "album_data.db")
BTS_ASSET   = os.path.join(PROJECT_ROOT, "assets","bts_album")
BLACKPINK_ASSET =  os.path.join(PROJECT_ROOT, "assets","blackpink_album")
SEVENTEEN_ASSET = os.path.join(PROJECT_ROOT, "assets","seventeen_album")
AESPA_ASSET = os.path.join(PROJECT_ROOT, "assets","aespa_album")
ENHYPEN_ASSET = os.path.join(PROJECT_ROOT, "assets","enhypen_album")
TWICE_ASSET = os.path.join(PROJECT_ROOT, "assets","twice_album")
ASSET = BTS_ASSET + BLACKPINK_ASSET + SEVENTEEN_ASSET + AESPA_ASSET + ENHYPEN_ASSET + TWICE_ASSET

# เผื่อโฟลเดอร์ database ยังไม่มี


conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

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

# NOTE:
seed = [
  # BTS
  ("BTS","Love Yourself: Her","E Ver.",680,18, os.path.join(BTS_ASSET,"Love_Yourself_Her.jpg")),
  ("BTS","Love Yourself: Tear","Y Ver.",720,15, os.path.join(BTS_ASSET,"Love_Yourself_Tear.jpg")),
  ("BTS","Love Yourself: Answer","S Ver.",750,20, os.path.join(BTS_ASSET,"Love_Yourself_Answer.jpg")),
  ("BTS","Map of the Soul: Persona","L Ver.",800,12, os.path.join(BTS_ASSET,"Map _of_the_Soul_Persona.jpg")),
  ("BTS","Map of the Soul: 7","Ver.2",820,15, os.path.join(BTS_ASSET,"Map_of_the_Soul_7.jpg")),
  ("BTS","BE","Deluxe Ver.",670,10, os.path.join(BTS_ASSET,"BE.jpg")),
  ("BTS","Butter","Promo Ver.",600,25, os.path.join(BTS_ASSET,"BUTTER.jpg")),
  ("BTS","Proof","Standard Ver.",890,8, os.path.join(BTS_ASSET,"Proof.jpg")),
  ("BTS","Wings","Y Ver.",650,22, os.path.join(BTS_ASSET,"Wings.jpg")),
  ("BTS","Skool Luv Affair","Special Edition",620,16, os.path.join(BTS_ASSET,"Skool_Luv_Affair.jpg")),

  # BLACKPINK
  ("BLACKPINK","Square Up","Standard Ver.",720,14, os.path.join(BLACKPINK_ASSET,"bp_square_up.jpg")),
  ("BLACKPINK","Kill This Love","CD+DVD Ver.",780,12, os.path.join(BLACKPINK_ASSET,"bp_kill_this_love.jpg")),
  ("BLACKPINK","THE ALBUM","Black Ver.",790,18, os.path.join(BLACKPINK_ASSET,"bp_the_album.jpg")),
  ("BLACKPINK","Born Pink","Box Set Ver.",850,10, os.path.join(BLACKPINK_ASSET,"bp_born_pink.jpg")),
  ("BLACKPINK","BLACKPINK 2019-2020 Repackage","Repackage Ver.",730,13, os.path.join(BLACKPINK_ASSET,"bp_2019_2020.jpg")),
  ("BLACKPINK","Kill This Love (Re-package)","Re Ver.",760,20, os.path.join(BLACKPINK_ASSET,"bp_kill_this_love_re.jpg")),
  ("BLACKPINK","How You Like That","Standard Ver.",700,19, os.path.join(BLACKPINK_ASSET,"bp_how_you_like_that.jpg")),
  ("BLACKPINK","Square Two","Standard Ver.",680,17, os.path.join(BLACKPINK_ASSET,"bp_square_two.jpg")),
  ("BLACKPINK","Blackpink in Your Area","Limited Ver.",810,9, os.path.join(BLACKPINK_ASSET,"bp_in_your_area.jpg")),
  ("BLACKPINK","Light Up the Sky","Digital Ver.",650,21, os.path.join(BLACKPINK_ASSET,"bp_light_up_the_sky.jpg")),

  # SEVENTEEN
  ("SEVENTEEN","Love & Letter","Alpha Ver.",630,20, os.path.join(SEVENTEEN_ASSET,"svt_love_letter.jpg")),
  ("SEVENTEEN","Teen, Age","Standard Ver.",670,18, os.path.join(SEVENTEEN_ASSET,"svt_teen_age.jpg")),
  ("SEVENTEEN","An Ode","Standard Ver.",720,14, os.path.join(SEVENTEEN_ASSET,"svt_an_ode.jpg")),
  ("SEVENTEEN","Heng:garæ","Deluxe Ver.",790,11, os.path.join(SEVENTEEN_ASSET,"svt_heng_garae.jpg")),
  ("SEVENTEEN","Face the Sun","Ray Ver.",770,25, os.path.join(SEVENTEEN_ASSET,"svt_fts.jpg")),
  ("SEVENTEEN","Attacca","Standard Ver.",760,16, os.path.join(SEVENTEEN_ASSET,"svt_attacca.jpg")),
  ("SEVENTEEN","Your Choice","Standard Ver.",750,17, os.path.join(SEVENTEEN_ASSET,"svt_your_choice.jpg")),
  ("SEVENTEEN","FML","Standard Ver.",830,10, os.path.join(SEVENTEEN_ASSET,"svt_fml.jpg")),
  ("SEVENTEEN","Semicolon","Standard Ver.",700,19, os.path.join(SEVENTEEN_ASSET,"svt_semicolon.jpg")),
  ("SEVENTEEN","17 Carat","Debut Ver.",620,22, os.path.join(SEVENTEEN_ASSET,"svt_17carat.jpg")),

  # AESPA
  ("AESPA","Savage","Standard Ver.",640,20, os.path.join(AESPA_ASSET,"aespa_savage.jpg")),
  ("AESPA","Next Level","Standard Ver.",610,22, os.path.join(AESPA_ASSET,"aespa_next_level.jpg")),
  ("AESPA","Girls","Standard Ver.",630,24, os.path.join(AESPA_ASSET,"aespa_girls.jpg")),
  ("AESPA","MY WORLD","Zine Ver.",660,12, os.path.join(AESPA_ASSET,"aespa_myworld.jpg")),
  ("AESPA","Drama","Standard Ver.",650,21, os.path.join(AESPA_ASSET,"aespa_drama.jpg")),
  ("AESPA","Hot Air","Standard Ver.",620,23, os.path.join(AESPA_ASSET,"aespa_hot_air.jpg")),
  ("AESPA","Black Mamba","Standard Ver.",600,26, os.path.join(AESPA_ASSET,"aespa_black_mamba.jpg")),
  ("AESPA","Forever","Standard Ver.",640,18, os.path.join(AESPA_ASSET,"aespa_forever.jpg")),
  ("AESPA","New Norm","Standard Ver.",630,19, os.path.join(AESPA_ASSET,"aespa_new_norm.jpg")),
  ("AESPA","Savage (Re-package)","Re Ver.",670,14, os.path.join(AESPA_ASSET,"aespa_savage_re.jpg")),

  # ENHYPEN
  ("ENHYPEN","BORDER : DAY ONE","Standard Ver.",650,23, os.path.join(ENHYPEN_ASSET,"enh_bord_day_one.jpg")),
  ("ENHYPEN","BORDER : CARNIVAL","Carnival Ver.",680,20, os.path.join(ENHYPEN_ASSET,"enh_border_carnival.jpg")),
  ("ENHYPEN","DIMENSION : DILEMMA","Standard Ver.",720,17, os.path.join(ENHYPEN_ASSET,"enh_dimension_dilemma.jpg")),
  ("ENHYPEN","DIMENSION : ANSWER","Answer Ver.",740,13, os.path.join(ENHYPEN_ASSET,"enh_dimension_answer.jpg")),
  ("ENHYPEN","DRIVE : 0","Standard Ver.",690,19, os.path.join(ENHYPEN_ASSET,"enh_drive_zero.jpg")),
  ("ENHYPEN","FATE : FINAL","Standard Ver.",710,12, os.path.join(ENHYPEN_ASSET,"enh_fate_final.jpg")),
  ("ENHYPEN","BORDER : DAY ONE (Ver.2)","Ver.2",670,22, os.path.join(ENHYPEN_ASSET,"enh_border_dayone2.jpg")),
  ("ENHYPEN","DIMENSION : DILEMMA (Ver.2)","Ver.2",730,14, os.path.join(ENHYPEN_ASSET,"enh_dimension_dilemma2.jpg")),
  ("ENHYPEN","Fate : (For) Winners","Standard Ver.",700,18, os.path.join(ENHYPEN_ASSET,"enh_fate_for_winners.jpg")),
  ("ENHYPEN","Polaroid Love","Standard Ver.",640,24, os.path.join(ENHYPEN_ASSET,"enh_polaroid_love.jpg")),

  # TWICE
  ("TWICE","Twicetagram","Standard Ver.",640,21, os.path.join(TWICE_ASSET,"twice_twicetagram.jpg")),
  ("TWICE","What is Love?","Standard Ver.",670,18, os.path.join(TWICE_ASSET,"twice_what_is_love.jpg")),
  ("TWICE","YES or YES","Standard Ver.",680,17, os.path.join(TWICE_ASSET,"twice_yes_or_yes.jpg")),
  ("TWICE","FANCY YOU","Standard Ver.",710,14, os.path.join(TWICE_ASSET,"twice_fancy_you.jpg")),
  ("TWICE","Formula of Love","Study Ver.",750,10, os.path.join(TWICE_ASSET,"twice_fol.jpg")),
  ("TWICE","MORE & MORE","Standard Ver.",720,16, os.path.join(TWICE_ASSET,"twice_more_and_more.jpg")),
  ("TWICE","Eyes Wide Open","Standard Ver.",760,12, os.path.join(TWICE_ASSET,"twice_eyes_wide_open.jpg")),
  ("TWICE","Feel Special","Standard Ver.",730,15, os.path.join(TWICE_ASSET,"twice_feel_special.jpg")),
  ("TWICE","Taste of Love","Standard Ver.",740,13, os.path.join(TWICE_ASSET,"twice_taste_of_love.jpg")),
  ("TWICE","READY TO TWICE","Standard Ver.",690,19, os.path.join(TWICE_ASSET,"twice_ready_to_twice.jpg")),
]


# ใส่เฉพาะถ้ายังว่าง
count = cur.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
if count == 0:
    cur.executemany(
      "INSERT INTO albums(group_name,album_name,version,price,stock,cover_path) VALUES (?,?,?,?,?,?)",
      seed
    )
    conn.commit()
    print(" Seeded:", len(seed), "rows")
else:
    print("มีข้อมูลแล้ว:", count, "rows (ไม่ใส่ซ้ำ)")

conn.close()
print(" DB สร้างแล้วที่", DB_PATH)


