import customtkinter as ctk
from PIL import Image , ImageOps
import os, sqlite3, io , sys
import tkinter as tk
import glob
import os, sys

# ทำให้ import 'database' ได้
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import sell_db

BASE_DIR = PROJECT_ROOT
ALBUM_DATA = os.path.join(BASE_DIR, "database", "album_data.db")

# เริ่มระบบตะกร้า
sell_db.init(
    sell_db_path=os.path.join(BASE_DIR, "database", "Sell_item.db"),
    album_db_path=ALBUM_DATA)

from database import sell_db

#พาธฐานของโปรเจ็กต์
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USER_DATA    = os.path.join(BASE_DIR, "database", "Userdata.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DEFAULT_PROFILE_IMAGE = os.path.join(ASSETS_DIR, "default_user.png")  # มีไฟล์นี้ไว้เป็นรูปสำรอง
ALBUM_DATA   = os.path.join(BASE_DIR, "database", "album_data.db")

# เริ่มต้นโมดูลตะกร้า (บอกพาธ 2 DB)
sell_db.init(sell_db_path=os.path.join(BASE_DIR, "database", "Sell_item.db"),
             album_db_path=ALBUM_DATA)

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

#หน้าต่างหลัก
main = ctk.CTk()
main.title("Purple Album — ร้านค้า")
main.geometry("1000x600")
main.configure(fg_color="#dac5ff")


# ตัวแปรเก็บขนาด panel
MARGIN_W = 40
MARGIN_H = 80

# จัดวาง panel
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

# เลื่อนการจัดวาง layout ไปทำทีหลัง
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

def _on_escape_quit(event=None):
    # ปิดแอปทั้งโปรแกรม
    try:
        main.destroy()
    except Exception:
        main.quit()
    return "break"
main.bind("<F11>", _toggle_fullscreen)
main.bind("<Escape>", _on_escape_quit)

# เริ่มในโหมด fullscreen 
_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    main.after(0, _enter_fullscreen)  
      
#ส่วนหัว
hearder=ctk.CTkFrame(main, fg_color="#b868e6", height=70,corner_radius=0)
hearder.pack(fill="x")

# โลโก้
logo_path = r"C:\Python\project\LOGOproject.png"  
logo_ctk  = ctk.CTkImage(light_image=Image.open(logo_path),
                         dark_image=Image.open(logo_path),
                         size=(85, 85))
ctk.CTkLabel(hearder, image=logo_ctk, text="", fg_color="transparent",
             font=ctk.CTkFont(family="Mitr")).pack(side="left", padx=(10, 30))

# เมนู
btn_artist = ctk.CTkButton(hearder, text="ศิลปิน",     fg_color="#b868e6", 
                          hover_color="#9a79f7", font=("Mitr", 20))
btn_artist.pack(side="left", padx=(0, 110))

btn_about  = ctk.CTkButton(hearder, text="เกี่ยวกับเรา", fg_color="#b868e6", 
                          hover_color="#9a79f7", font=("Mitr", 20))
btn_about.pack(side="left", padx=(0, 110))

# ช่องค้นหา
search = ctk.CTkEntry(hearder, placeholder_text="ค้นหา", width=330, height=40, fg_color="white", font=("Mitr", 14,))
search.pack(side="left", padx=(0, 95), pady=8)
# ค้นหาแบบเรียลไทม์
search.bind("<KeyRelease>", lambda e: refresh_content(search.get()))

# ตะกร้าสินค้า
cart_badge_var = tk.StringVar(value="0")

# อัปเดตเลขในตะกร้า
def update_cart_badge():
    # ดึงจำนวนจาก DB แล้วใส่ใน badge
    cart_badge_var.set(str(sell_db.count(login_username)))
    # อัปเดตยอดในหน้าตะกร้า (ถ้ามี label อยู่)
    try:
        if cart_total_label.winfo_exists():
            cart_total_label.configure(text=f"รวมทั้งหมด: {sell_db.total(login_username):,.0f} บาท")
    except Exception:
        pass
    
# ปุ่มตะกร้า
btn_basket = ctk.CTkButton(
    hearder,
    text="ตะกร้า",
    fg_color="#b868e6", hover_color="#9a79f7", font=("Mitr", 20),
    command=lambda: (open_cart_window(), update_cart_badge())
)
btn_basket.pack(side="left", padx=(0,110))

# badge ตัวเลขเป็นลูกของปุ่ม (เกาะมุมขวาบนของปุ่ม)
BADGE_D = 24
cart_badge = ctk.CTkLabel(
    btn_basket,
    textvariable=cart_badge_var,
    fg_color="#ff7bd4", text_color="white",
    corner_radius=BADGE_D//2, width=BADGE_D, height=BADGE_D,
    font=("Mitr", 12),
    bg_color="transparent"
)
cart_badge.place(relx=1.0, rely=0.0, x=-(BADGE_D//2 - 4), y=2, anchor="ne")

# โปรไฟล์ 
def open_profile():
    print("เปิดหน้าโปรไฟล์…")   # TODO: ใส่โค้ดเปิดหน้าโปรไฟล์จริง

btn_profile = ctk.CTkButton(hearder, text="โปรไฟล์", fg_color="#b868e6", 
                           hover_color="#9a79f7", font=("Mitr", 20),
                            command=open_profile)
btn_profile.pack(side="left", pady=8)

# รูปโปรไฟล์
blob = get_profile_image_by_username(login_username)
if blob:
    pil_img = blob_to_pil(blob)
elif os.path.exists(DEFAULT_PROFILE_IMAGE):
    pil_img = Image.open(DEFAULT_PROFILE_IMAGE).convert("RGBA")
else:
    # ถ้าไม่มีจริงๆใช้ภาพขาวไปก่อน
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
    refresh_content(search.get())
 
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

# ตรวจสอบพาธรูปภาพอัลบั้ม
def resolve_cover_path(p: str) -> str:
    if not p:
        return ""

    def exists(x):
        try:
            return os.path.exists(x) and os.path.isfile(x)
        except Exception:
            return False

    cand = []
    # 1) พาธตามที่อยู่ใน DB
    cand.append(os.path.normpath(p))
    # 2) relative จาก BASE_DIR (root โปรเจกต์)
    cand.append(os.path.normpath(os.path.join(BASE_DIR, p)))
    # 3) relative จาก .../database
    DB_DIR = os.path.dirname(ALBUM_DATA)
    cand.append(os.path.normpath(os.path.join(DB_DIR, p)))

    # 4) สลับโฟลเดอร์ assets <-> database/assets ทั้งสองทาง
    more = []
    for c in cand:
        if f"database{os.sep}assets{os.sep}" in c:
            more.append(c.replace(f"database{os.sep}assets{os.sep}", f"assets{os.sep}"))
        if f"{os.sep}assets{os.sep}" in c and f"database{os.sep}assets{os.sep}" not in c:
            more.append(c.replace(f"{os.sep}assets{os.sep}", f"{os.sep}database{os.sep}assets{os.sep}"))
    cand.extend(more)

    # 5) เคลียร์ space แปลก ๆ เช่น "Map _of" -> "Map_of"
    def fix_spaces(s: str) -> str:
        s = s.replace(" _", "_")
        while "  " in s:
            s = s.replace("  ", " ")
        return s
    cand = [fix_spaces(c) for c in cand]

    # 6) ตรงตัวก่อน
    for c in cand:
        if exists(c):
            return c

    # 7) ลองเปลี่ยนนามสกุล
    exts = [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]
    for c in list(cand):
        root, ext = os.path.splitext(c)
        for e in exts:
            alt = root + e
            if exists(alt):
                return alt

    # 8) ค้นหาแบบหลวมในโฟลเดอร์ปลายทาง (ไม่สนตัวพิมพ์เล็ก/ใหญ่)
    for c in cand:
        base_dir = os.path.dirname(c)
        base_name = os.path.splitext(os.path.basename(c))[0]
        if os.path.isdir(base_dir):
            for hit in glob.glob(os.path.join(base_dir, "*")):
                try:
                    if os.path.splitext(os.path.basename(hit))[0].lower() == base_name.lower() and exists(hit):
                        return hit
                except:
                    pass
    return ""

# ข้อมูลศิลปิน (รูป+ข้อความ)
def artist_info(group_name: str):
    # กล่อง Header
    head = ctk.CTkFrame(album_area, fg_color="#f7f5ff", corner_radius=12)
    head.pack(fill="x", padx=0, pady=(0,12))

    # รูป (500x300)
    img_path = Artist_Images.get(group_name)
    img_ctk = load_image(img_path, size=(500,300))

    img_lbl = ctk.CTkLabel(head, image=img_ctk, text="")
    img_lbl.image = img_ctk
    img_lbl.pack(side="left",padx=(70,30), pady=(50,0), anchor="w")

    # ข้อความคำอธิบาย
    desc = Artist_Descriptions.get(group_name, "")
    if desc:
        ctk.CTkLabel(
            head,
            text=desc,
            font=("Mitr", 20),
            text_color="#2F2A44",
            justify="left",
            wraplength=860
        ).pack(side="left", pady=(50,0), anchor="w")

def refresh_content(keyword: str = ""):
    clear_album_area()
    # 1) หัวศิลปิน (รูป+ข้อความ) ก่อน
    artist_info(current_group.get())
    # 2) อัลบั้มค่อยตามมา (จะใส่ load_albums() ทีหลังได้)
    # load_albums(keyword)   # ถ้ายังไม่มีฟังก์ชันนี้ ให้คอมเมนต์ไว้ก่อน

# การ์ดอัลบั้มแต่ละใบ
def add_album_card(id_, title, price, stock, cover_path):
    # การ์ดหลัก
    card = ctk.CTkFrame(album_area, fg_color="white", corner_radius=16)
    card.pack(fill="x", pady=6)

    # --- ใช้ตัวช่วย resolve พาธรูป ---
    cover_real = resolve_cover_path(cover_path)
    cover_img = load_image(cover_real, size=(120,120))  # ถ้า cover_real ว่าง load_image จะขึ้น placeholder ให้

    img_lbl = ctk.CTkLabel(card, image=cover_img, text="")
    img_lbl.image = cover_img  # กัน GC
    img_lbl.pack(side="left", padx=12, pady=12)

    # ข้อมูล
    info = ctk.CTkFrame(card, fg_color="white")
    info.pack(side="left", fill="x", expand=True, padx=4, pady=8)

    ctk.CTkLabel(
        info, text=title, font=("Mitr", 18), text_color="#2F2A44"
    ).pack(anchor="w")

    ctk.CTkLabel(
        info, text=f"ราคา {to_float(price):,.0f} บาท  |  สต็อก {int(stock)}",
        font=("Mitr", 14), text_color="#666"
    ).pack(anchor="w", pady=(2,0))

    ctk.CTkButton(
    card, text="เพิ่มลงตะกร้า", fg_color="#b868e6", hover_color="#9a79f7",
    font=("Mitr", 14),
    command=lambda: (sell_db.add(login_username, id_, 1),update_cart_badge())
).pack(side="right", padx=12, pady=12)





#โหลดอัลบั้มของวงนั้น   
def load_albums_only(keyword: str = ""):
    rows = qall("""
        SELECT id, album_name, IFNULL(version,''), IFNULL(price,0),
               IFNULL(stock,0), IFNULL(cover_path,'')
        FROM albums
        WHERE group_name = ?
          AND (album_name || ' ' || IFNULL(version,'')) LIKE ? COLLATE NOCASE
        ORDER BY id DESC
    """, (current_group.get(), f"%{keyword.strip()}%"))

    if not rows:
        ctk.CTkLabel(album_area, text="ไม่พบอัลบั้ม", text_color="gray", font=("Mitr", 14)).pack(pady=10)
        return

    for id_, name, ver, price, stock, cover in rows:
        title = f"{name} ({ver})" if ver else name
        add_album_card(id_, title, price, stock, cover)


#หน้าต่างรายการสินค้า
def add_section_header(group_name: str):
    hdr = ctk.CTkLabel(
        album_area, 
        text=f"— {group_name} —", 
        font=("Mitr", 18),
        text_color="#6543a9"
    )
    hdr.pack(anchor="w", pady=(12, 4))

# โหลดอัลบั้มทั้งหมดตามคำค้นหา
def load_albums_all(keyword: str):
    kw = keyword.strip()
    if not kw:
        load_albums_only("")
        return

    rows = qall("""
        SELECT id, group_name, album_name, IFNULL(version,''), IFNULL(price,0),
               IFNULL(stock,0), IFNULL(cover_path,'')
        FROM albums
        WHERE (group_name || ' ' || album_name || ' ' || IFNULL(version,'')) LIKE ? COLLATE NOCASE
        ORDER BY group_name, id DESC
    """, (f"%{kw}%",))

    if not rows:
        ctk.CTkLabel(album_area, text=f"ไม่พบผลลัพธ์สำหรับ “{kw}”", text_color="gray", font=("Mitr", 14)).pack(pady=10)
        return

    last_group = None
    for id_, gname, name, ver, price, stock, cover in rows:
        if gname != last_group:
            add_section_header(gname)
            last_group = gname
        title = f"{name} ({ver})" if ver else name
        add_album_card(id_, title, price, stock, cover)
        
# เปิดหน้าตะกร้าสินค้า
def open_cart_window():
    # ถ้ามีอยู่แล้วไม่เปิดซ้ำ
    if hasattr(main, "_cart_win") and main._cart_win and main._cart_win.winfo_exists():
        main._cart_win.lift(); main._cart_win.focus_force()
        return
    # สร้างหน้าต่างใหม่
    win = ctk.CTkToplevel(main)
    main._cart_win = win
    win.title("ตะกร้าสินค้า")
    win.geometry("720x560+930+200")

    # ทำเป็น modal + อยู่หน้าเสมอ
    win.transient(main)
    win.grab_set()
    win.lift(); win.focus_force()
    win.attributes("-topmost", True)
    win.after(200, lambda: win.attributes("-topmost", False))

    # ---- ฟังก์ชันปิด (ต้อง release grab ก่อน) ----
    def _close():
        try:
            win.grab_release()
        except Exception:
            pass
        win.destroy()

    # กดกากบาทหรือกด ESC เพื่อปิด
    win.protocol("WM_DELETE_WINDOW", _close)
    win.bind("<Escape>", lambda e: _close())

    # ---------- UI ภายใน ----------
    shell = ctk.CTkFrame(win, fg_color="#f3ecff", corner_radius=20)
    shell.pack(fill="both", expand=True, padx=14, pady=14)

    header = ctk.CTkFrame(shell, fg_color="transparent")
    header.pack(fill="x", padx=14, pady=(6, 8))

    ctk.CTkLabel(header, text="ตะกร้าสินค้า", font=("Mitr", 20, "bold")).pack(side="left")
    
    # โปรโมชั่นพิเศษ
    ctk.CTkLabel(
        header, text="โปรโมชั่น: ซื้อครบ 3 อัลบั้ม ลด 20% 🔥",
        text_color="#7a3cff", font=("Mitr", 16)
    ).pack(side="right", padx=(0,8))

    # เนื้อหาเลื่อน
    body = ctk.CTkScrollableFrame(shell, fg_color="white", corner_radius=14)
    body.pack(fill="both", expand=True, padx=14, pady=(0, 8))

    # รายการสินค้า
    items = sell_db.items(login_username)
    if not items:
        ctk.CTkLabel(body, text="ยังไม่มีสินค้าในตะกร้า", text_color="gray", font=("Mitr", 16)).pack(pady=20)
    else:
        for album_id, title, price, qty, cover in items:
            row = ctk.CTkFrame(body, fg_color="white")
            row.pack(fill="x", pady=6, padx=8)

            cover_real = resolve_cover_path(cover)
            img = load_image(cover_real, size=(60,60))
            ctk.CTkLabel(row, image=img, text="").pack(side="left", padx=8, pady=8)

            info = ctk.CTkFrame(row, fg_color="white"); info.pack(side="left", fill="x", expand=True, padx=4, pady=8)
            ctk.CTkLabel(info, text=title, font=("Mitr", 16)).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{price:,.0f} บาท x {qty} = {price*qty:,.0f} บาท", text_color="#555", font=("Mitr", 16)).pack(anchor="w")

            ctrls = ctk.CTkFrame(row, fg_color="white"); ctrls.pack(side="right", padx=8, pady=8)
            ctk.CTkButton(ctrls, text="-", width=34,
                          command=lambda a=album_id, q=qty: (sell_db.set_qty(login_username, a, q-1),
                                                             win.destroy(), open_cart_window(), update_cart_badge())).pack(side="left", padx=2)
            ctk.CTkButton(ctrls, text="+", width=34,
                          command=lambda a=album_id, q=qty: (sell_db.set_qty(login_username, a, q+1),
                                                             win.destroy(), open_cart_window(), update_cart_badge())).pack(side="left", padx=2)
            ctk.CTkButton(ctrls, text="ลบ", width=46, fg_color="#e86", hover_color="#d55",
                          command=lambda a=album_id: (sell_db.remove(login_username, a),
                                                      win.destroy(), open_cart_window(), update_cart_badge())).pack(side="left", padx=6)

    # สรุปราคา
    calc = sell_db.pricing(login_username)
    footer = ctk.CTkFrame(shell, fg_color="transparent"); footer.pack(fill="x", padx=14, pady=(6, 14))
    right = ctk.CTkFrame(footer, fg_color="transparent"); right.pack(side="right")
    ctk.CTkLabel(right, text=f"สินค้ารวม: {calc['item_count']} ชิ้น", font=("Mitr", 14)).pack(anchor="e")
    ctk.CTkLabel(right, text=f"ราคารวม (Subtotal): {calc['subtotal']:,.0f} บาท", font=("Mitr", 14)).pack(anchor="e")
    if calc["discount_rate"] > 0:
        ctk.CTkLabel(right, text=f"ส่วนลด {int(calc['discount_rate']*100)}%: -{calc['discount']:,.0f} บาท",
                     text_color="#2ba84a", font=("Mitr", 14)).pack(anchor="e")

    global cart_total_label
    cart_total_label = ctk.CTkLabel(right, text=f"ยอดสุทธิ: {calc['total']:,.0f} บาท", font=("Mitr", 18, "bold"))
    cart_total_label.pack(anchor="e")

    left = ctk.CTkFrame(footer, fg_color="transparent"); left.pack(side="left")
    ctk.CTkButton(left, text="ล้างตะกร้า", fg_color="#ccc", text_color="black", font=("Mitr", 16),
                  command=lambda: (sell_db.clear(login_username), _close(), open_cart_window(), update_cart_badge())
    ).pack(side="left", padx=(0,6))
    ctk.CTkButton(left, text="ยืนยันการสั้งซื้อ", font=("Mitr", 16)).pack(side="left")
    
# โหลดหน้าวงแรกตอนเปิดแอป
def refresh_content(keyword: str = ""):
    clear_album_area()
    kw = keyword.strip()
    if kw:
        load_albums_all(kw)
    else:
        artist_info(current_group.get())
        load_albums_only("")

# --- โหลดคอนเทนต์ครั้งแรกตอนเปิดแอป ---
taps.set(GROUPS[0])
change_group(GROUPS[0])        
main.after(100, update_cart_badge)
main.mainloop()