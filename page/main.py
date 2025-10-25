import customtkinter as ctk
from PIL import Image , ImageOps
import os, sqlite3, io , sys
import tkinter as tk

#พาธฐานของโปรเจ็กต์
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USER_DATA    = os.path.join(BASE_DIR, "database", "Userdata.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DEFAULT_PROFILE_IMAGE = os.path.join(ASSETS_DIR, "default_user.png")  # มีไฟล์นี้ไว้เป็นรูปสำรอง
ALBUM_DATA   = os.path.join(BASE_DIR, "database", "album_data.db")

# รับ username จาก login.py
# #if len( sys.argv ) > 1: 
    # login_username = sys.argv[1] 
#else: 
    # login_username = None

# โหมด dev: ตั้ง username ไว้ชั่วคราว 
login_username = "achira"

# รายชื่อวง
GROUPS = [ "BTS","BLACKPINK","SEVENTEEN","AESPA","ENHYPEN","TWICE"]

# พาธรูปภาพศิลปิน
Artist_Images = {
    "BTS":       os.path.join(ASSETS_DIR, "BTS.png"),
    "BLACKPINK": os.path.join(ASSETS_DIR, "Blackpink.png"),
    "SEVENTEEN": os.path.join(ASSETS_DIR, "seventeen.png"),
    "AESPA":     os.path.join(ASSETS_DIR, "Aespa.png"),
    "ENHYPEN":   os.path.join(ASSETS_DIR, "enhypen.png"),
    "TWICE":     os.path.join(ASSETS_DIR, "Twice.png"),
}

#ข้อความอธิบายศิลปิน
Artist_Descriptions = {
    "BTS": """BTS (방탄소년단)

    BTS หรือ บังทันโซนยอนดัน เป็นบอยแบนด์จากเกาหลีใต้ภายใต้ค่าย HYBE เดบิวต์เมื่อปี 2013 ด้วยแนวเพลงฮิปฮอป ก่อนพัฒนามาสู่ดนตรีที่หลากหลายมากขึ้น พวกเขามีเอกลักษณ์ในการสื่อสารกับแฟนๆ ผ่านเนื้อหาที่จริงใจเกี่ยวกับชีวิต การกดดันในสังคม และการยอมรับตัวเอง
    สมาชิก: RM, Jin, Suga, J-Hope, Jimin, V, Jungkook
    พวกเขามีฐานแฟนคลับชื่อ ARMY และเป็นหนึ่งในวง K-POP ที่ประสบความสำเร็จระดับโลกมากที่สุด ทั้งยอดขาย อัลบั้ม การทัวร์คอนเสิร์ต และการขึ้นอันดับ 1 บนชาร์ต Billboard หลายครั้ง""",
    
    "BLACKPINK": """BLACKPINK (블랙핑크)

    BLACKPINK เป็นเกิร์ลกรุ๊ประดับโลกจากค่าย YG Entertainment เดบิวต์ปี 2016 ด้วยคอนเซปต์สวย แรง และเท่ เพลงมีสไตล์ที่โดดเด่นด้วยบีตฮิปฮอปผสม EDM ทำให้พวกเธอได้รับความนิยมทั่วโลกในเวลาไม่นาน
    สมาชิก: Jisoo, Jennie, Rosé, Lisa
    พวกเธอเป็นเกิร์ลกรุ๊ป K-POP วงแรกที่ขึ้นแสดงในงาน Coachella และมีฐานแฟนคลับ BLINK ทั่วโลก รวมถึงมีสถิติยอดวิว YouTube ระดับมหาศาลหลายเพลง""",
    
    "SEVENTEEN": """SEVENTEEN (세븐틴)

    SEVENTEEN เป็นบอยแบนด์จากค่าย Pledis Entertainment เดบิวต์ในปี 2015 จุดเด่นของวงคือ การมีส่วนร่วมในการแต่งเพลงและออกแบบท่าเต้นเอง จนได้รับฉายา "ไอดอลโปรดิวเซอร์"
    สมาชิก: S.Coups, Jeonghan, Joshua, Jun, Hoshi, Wonwoo, Woozi, DK, Mingyu, The8, Seungkwan, Vernon, Dino
    แบ่งออกเป็น 3 ยูนิต: Hip-hop / Vocal / Performance
    พวกเขาเป็นหนึ่งในวงที่มีพลังบนเวทีสูงที่สุดและมีฐานแฟนคลับ CARAT ที่เหนียวแน่น""",
    
    "AESPA": """AESPA (에스파)

    aespa เป็นเกิร์ลกรุ๊ปรุ่นใหม่จากค่าย SM Entertainment เดบิวต์ปี 2020 และมีคอนเซปต์ที่ไม่เหมือนใคร ด้วยโลก Metaverse และ "ae-avatar" ที่อยู่ในโลกเสมือน ทำให้พวกเธอโดดเด่นตั้งแต่เปิดตัว
    สมาชิก: Karina, Giselle, Winter, Ningning
    พวกเธอมาพร้อมคอนเซปต์เข้มและดนตรีแนว Future Bass และ EDM ที่มีเอกลักษณ์ ทำให้ aespa เป็นหนึ่งในเกิร์ลกรุ๊ปรุ่นใหม่ที่มาแรงที่สุด""",
    
    "ENHYPEN": """ENHYPEN (엔하이픈)

    ENHYPEN เป็นบอยแบนด์จากค่าย BELIFT LAB เดบิวต์ปี 2020 ผ่านรายการ I-LAND ที่คัดเลือกโดย HYBE พวกเขามีคอนเซปต์ลึกลับและเนื้อเรื่องในอัลบั้มต่อเนื่องเกี่ยวกับการเติบโตและสายสัมพันธ์
    สมาชิก: Jungwon, Heeseung, Jay, Jake, Sunghoon, Sunoo, Ni-ki
    ด้วยเสน่ห์ด้าน Performance และ Visual ที่แข็งแรง ENHYPEN จึงเป็นหนึ่งในวงเจน 4 ที่เติบโตเร็วที่สุด""",
    
    "TWICE": """TWICE (트와이스)

    TWICE เป็นเกิร์ลกรุ๊ปจากค่าย JYP Entertainment เดบิวต์ปี 2015 ผ่านรายการ SIXTEEN ด้วยคอนเซปต์สดใส น่ารัก และพลังบวก ทำให้พวกเธอได้รับฉายา “Queen of Cheer-up Songs”
    สมาชิก: Nayeon, Jeongyeon, Momo, Sana, Jihyo, Mina, Dahyun, Chaeyoung, Tzuyu
    ด้วยเพลงที่ติดหูและท่าเต้นที่โด่งดัง TWICE เป็นวงที่มีอิทธิพลมากในเอเชียและทั่วโลก"""
}

# ---------- DB ----------
def get_profile_image_by_username(username: str):
    conn = sqlite3.connect(USER_DATA)
    cur  = conn.cursor()
    cur.execute("SELECT profile_image FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else None 

# ฟังก์ชันรันคำสั่ง SQL และคืนค่าทุกแถว
def qall(sql, args=()):
    conn = sqlite3.connect(ALBUM_DATA)   # path นี้ขอให้ตรงกับไฟล์จริง
    cur  = conn.cursor()
    cur.execute(sql, args)
    rows = cur.fetchall()
    conn.close()
    return rows

# แปลง BLOB เป็น PIL Image
def blob_to_pil(blob: bytes) -> Image.Image:
    return Image.open(io.BytesIO(blob)).convert("RGBA")

# ดึงรายชื่อวงจากฐานข้อมูล
def get_group():
    # จากตาราง albums
    rows = qall("SELECT DISTINCT group_name FROM albums WHERE group_name<>'' ORDER BY group_name")
    return [r[0] for r in rows]

# แปลงค่าเป็น float
def to_float(value):
    try:
        return float(str(value).replace(',', '').strip())
    except:
        return 0.0

# ดึงอัลบั้มตามชื่อวง
def get_album_by_group(group_name):
    # ดึงจากตาราง albums
    rows = qall("""
        SELECT id, album_name, version, price, stock, cover_path
        FROM albums
        WHERE group_name=?
        ORDER BY id DESC
    """, (group_name,))
    out = []
    for id_, aname, ver, price, stock, cover in rows:
        title = f"{aname} ({ver})" if ver else aname
        out.append((id_, title, to_float(price), int(stock) if stock is not None else 0, cover or ""))
    return out

#เซ็ตอัพหน้าต่างหลัก
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

main = ctk.CTk()
main.title("Purple Album — ร้านค้า")
main.geometry("1000x600")
main.configure(fg_color="#dac5ff")
    
#ส่วนหัว
hearder=ctk.CTkFrame(main, fg_color="#b868e6", height=70)
hearder.pack(fill="x")

# โลโก้
logo_path = r"C:\Python\project\LOGOproject.png"   # ปรับ path ให้ตรงเครื่อง
logo_ctk  = ctk.CTkImage(light_image=Image.open(logo_path),
                         dark_image=Image.open(logo_path),
                         size=(85, 85))
ctk.CTkLabel(hearder, image=logo_ctk, text="", fg_color="transparent",
             font=ctk.CTkFont(family="Mitr")).pack(side="left", padx=(10, 50))

# เมนู
btn_home   = ctk.CTkButton(hearder, text="หน้าหลัก",   fg_color="#b868e6", 
                          hover_color="#9a79f7", font=("Mitr", 20))
btn_home.pack(side="left", padx=(0, 120))

btn_artist = ctk.CTkButton(hearder, text="ศิลปิน",     fg_color="#b868e6", 
                          hover_color="#9a79f7", font=("Mitr", 20))
btn_artist.pack(side="left", padx=(0, 120))

btn_about  = ctk.CTkButton(hearder, text="เกี่ยวกับเรา", fg_color="#b868e6", 
                          hover_color="#9a79f7", font=("Mitr", 20))
btn_about.pack(side="left", padx=(0, 120))

# ช่องค้นหา
search = ctk.CTkEntry(hearder, placeholder_text="ค้นหา", width=300, height=30, fg_color="white", font=("Mitr", 14,))
search.pack(side="left", padx=(0, 80), pady=8)

# โปรไฟล์ 
def open_profile():
    print("เปิดหน้าโปรไฟล์…")   # TODO: ใส่โค้ดเปิดหน้าโปรไฟล์จริง

btn_profile = ctk.CTkButton(hearder, text="โปรไฟล์", fg_color="#b868e6", 
                           hover_color="#9a79f7", font=("Mitr", 20),
                            command=open_profile)
btn_profile.pack(side="left", padx=(0,0), pady=8)

# รูปโปรไฟล์
blob = get_profile_image_by_username(login_username)
if blob:
    pil_img = blob_to_pil(blob)
elif os.path.exists(DEFAULT_PROFILE_IMAGE):
    pil_img = Image.open(DEFAULT_PROFILE_IMAGE).convert("RGBA")
else:
    # ถ้าไม่มีจริง ๆ ใช้ภาพขาวใส ๆ ไปก่อน
    pil_img = Image.new("RGBA", (50, 50), (255, 255, 255, 0))

avatar_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(50, 50))
avatar_label = ctk.CTkLabel(hearder, image=avatar_ctk, text="", fg_color="transparent")
avatar_label.pack(side="left", padx=(0, 0), pady=8)

# container สำหรับแท็บ artist
tap_artist = ctk.CTkFrame(main, fg_color="#dac5ff", height=70)
tap_artist.pack(fill="x", pady=(0,10))

current_group = ctk.StringVar(value=GROUPS[0])

# โหลดอัลบั้มตามวงที่เลือก
def change_group(value):
    current_group.set(value)
    load_albums() 

# สร้างปุ่มแท็บเลือกศิลปิน
taps = ctk.CTkSegmentedButton(
    tap_artist,values=GROUPS,command=change_group,fg_color="#dac5ff",selected_color="#b868e6",
    unselected_color="#dac5ff",text_color="black",font=ctk.CTkFont(family="Mitr")
)

taps.set(GROUPS[0])  # ค่าเริ่มต้น
taps.pack(padx=15, fill="x",pady=(10,0))

album_area = ctk.CTkScrollableFrame(main, fg_color="#f7f5ff")
album_area.pack(fill="both",expand=True,padx=30,pady=(0,30))

def clear_album_area():
    for w in album_area.winfo_children():
        w.destroy()

def load_image(path, size=(500,300)):
    try:
        img = Image.open(path).convert("RGBA")
        # ให้พอดีกรอบโดยไม่บิดสัดส่วน
        img = ImageOps.contain(img, size)
        canvas = Image.new("RGBA", size, (255,255,255,0))
        canvas.paste(img, ((size[0]-img.width)//2, (size[1]-img.height)//2), img)
    except Exception:
        canvas = Image.new("RGBA", size, (230,220,255,255))  # placeholder
    return ctk.CTkImage(light_image=canvas, dark_image=canvas, size=size)


def artist_info(group_name: str):
    # กล่อง Header
    head = ctk.CTkFrame(album_area, fg_color="white", corner_radius=12)
    head.pack(fill="x", padx=0, pady=(0,12))

    # รูป (500x300)
    img_path = Artist_Images.get(group_name)
    if img_path and os.path.exists(img_path):
        img_ctk = load_image(img_path, size=(400,200))
    else:
        img_ctk = load_image("", size=(500,300))  # placeholder

    img_lbl = ctk.CTkLabel(head, image=img_ctk, text="")
    img_lbl.image = img_ctk
    img_lbl.pack(side="left",padx=5, pady=10, anchor="w")

    # ข้อความคำอธิบาย
    desc = Artist_Descriptions.get(group_name, "")
    if desc:
        ctk.CTkLabel(
            head,
            text=desc,
            font=("Mitr", 15),
            text_color="#2F2A44",
            justify="left",
            wraplength=860
        ).pack(side="right",padx=5, pady=(0,12), anchor="w")

def refresh_content(keyword: str = ""):
    clear_album_area()
    # 1) หัวศิลปิน (รูป+ข้อความ) ก่อน
    artist_info(current_group.get())
    # 2) อัลบั้มค่อยตามมา (จะใส่ load_albums() ทีหลังได้)
    # load_albums(keyword)   # ถ้ายังไม่มีฟังก์ชันนี้ ให้คอมเมนต์ไว้ก่อน


#def add_album_card(id_, title, price, stock, cover_path):

MARGIN_W = 40
MARGIN_H = 80

def layout_panel(final=False):
    global _last_panel_size
    w = max(main.winfo_width(),  400)
    h = max(main.winfo_height(), 300)
    taps.update_idletasks()
    need_w = taps.winfo_reqwidth()
    need_h = taps.winfo_reqheight()
    panel_w = max(min(int(w * 0.86), w - 40), need_w + MARGIN_W)
    panel_h = max(min(int(h * 0.78), h - 40), need_h + MARGIN_H)

    PADDING_X = 80
    PADDING_Y = 120

    inner_w = max(panel_w - PADDING_X, need_w)
    inner_h = max(panel_h - PADDING_Y, need_h)

# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}
def _apply_layout_later():
    main.after(20, lambda: layout_panel(final=True))
    
def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = main.winfo_geometry()
    try:
        main.state("zoomed")
    except tk.TclError:
        pass
    main.attributes("-fullscreen", True)
    main.geometry(f"{main.winfo_screenwidth()}x{main.winfo_screenheight()}+0+0")
    _apply_layout_later()

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    main.attributes("-fullscreen", False)
    try:
        main.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        main.geometry("1000x600")
    _apply_layout_later()

def _toggle_fullscreen(event=None):
    if _fullscreen_state["value"]:
        _leave_fullscreen()
    else:
        _enter_fullscreen()
    return "break"

def _exit_fullscreen(event=None):
    _leave_fullscreen()
    return "break"
main.bind("<F11>", _toggle_fullscreen)
main.bind("<Escape>", _exit_fullscreen)

_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    main.after(0, _enter_fullscreen)
    
# โหลดหน้าวงแรกตอนเปิดแอป
refresh_content()
main.mainloop()
