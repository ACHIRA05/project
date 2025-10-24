import customtkinter as ctk
from tkinter import*
from tkinter import messagebox
from PIL import Image, ImageOps, ImageDraw ,ImageFilter
import subprocess
import sys
import os,sqlite3
import io

#database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db"))

# ฟังก์ชันเพื่อดึงรูปโปรไฟล์จากฐานข้อมูลตามชื่อผู้ใช้
def get_profile_image_by_username(username):
    conn = sqlite3.connect(DB_PATH)  # ✅ ใช้ path นี้แทน connect เดิม
    cursor = conn.cursor()
    cursor.execute("SELECT profile_image FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else None

# ฟังก์ชันแปลง BLOB เป็นรูปภาพ PIL
def convert_blob_to_image(blob_data):
    try:
        image = Image.open(io.BytesIO(blob_data))
        return image
    except:
        return None

# ---------- รับ username จาก login.py ----------    
#if len( sys.argv ) > 1:
    login_username = sys.argv[1]
#else:
    login_username = None
    
#ทดสอบใส่username เอง
login_username = "achira"
# ---------- ธีม & ค่าสี ----------
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")  

PURPLE_PRIMARY = "#7B66E3" 
PURPLE_ACCENT  = "#B388FF"  
BG_SOFT        = "#F7F5FF"   
TEXT_DARK      = "#2F2A44"

# ---- Perf tuning ---
RESIZE_DELAY = 60    
PANEL_SUPERSAMPLE = 2     
SIZE_STEP = 2              

_bg_cache = {}             # {(w,h): PhotoImage}
_panel_cache = {}  
# ---------- หน้าต่างหลัก ----------
main = ctk.CTk()
main.title("Purple Album — ร้านค้า")
main.geometry("900x600+3500")
main.minsize(800, 520)
main.configure(fg_color=BG_SOFT)

ARTISTS = ["BTS","BLACKPINK","SEVENTEEN","AESPA","ENHYPEN","TWICE"]

#ส่วนเฟรมหัว
hearder = ctk.CTkFrame(main,fg_color="#b868e6",height=70)
hearder.pack(fill="x")

logoimg = r"C:\Python\project\LOGOproject.png"
# กำหนดพาธรูปโลโก้สำหรับนำมาใช้
logo_ctk = ctk.CTkImage(
    # สร้างอ็อบเจ็กต์ CTkImage และเปิดไฟล์สำหรับภาพโหมดสว่าง
    light_image=Image.open(logoimg),
    # ระบุภาพสำหรับโหมดสว่างของ CustomTkinter
    dark_image=Image.open(logoimg),
    # ระบุภาพเดียวกันให้ใช้ตอนโหมดมืด
    size=(85, 85)
    # ตั้งขนาดภาพโลโก้เป็น 100x100 พิกเซล
)
logo = ctk.CTkLabel(hearder,image=logo_ctk,text="")
logo.pack(side=LEFT,padx=(0,5))

home=ctk.CTkButton(hearder,text="หน้าหลัก",fg_color="#b868e6",hover_color="#9a79f7",font=("JasmineUPC_Bold",20),command=lambda:subprocess.Popen([sys.executable, r"C:\Python\project\page\main.py"]) and main.destroy())
home.pack(side=LEFT)

artist = ctk.CTkButton(hearder,text="ศิลปิน",fg_color="#b868e6",hover_color="#9a79f7",font=("JasmineUPC_Bold",20),command=lambda:subprocess.Popen(main.destroy()))
artist.pack(side=LEFT)

about = ctk.CTkButton(hearder,text="เกี่ยวกับเรา",fg_color="#b868e6",hover_color="#9a79f7",font=("JasmineUPC_Bold",20),command=lambda:subprocess.Popen(main.destroy()))
about.pack(side=LEFT)

#---- ฟังก์ชันครอปรูปเป็นวงกลม ---- 
def blob_to_pil(blob: bytes):
    return Image.open(io.BytesIO(blob)).convert("RGBA")

def remove_black_bg(im: Image.Image, threshold=28, feather=1.5) -> Image.Image:
    """
    ลบพื้นหลัง 'สีดำ' ออกให้โปร่งใส:
    - threshold: 0–255 (ยิ่งมากยิ่งตัดกว้าง เสี่ยงกินผม/เงา)
    - feather: ทำขอบฟุ้งนุ่มๆ เพื่อลดรอยหยัก (พิกเซล)
    """
    im = im.convert("RGBA")
    pixels = im.getdata()
    new_pixels = []

    t = max(0, min(254, threshold))
    for r, g, b, a in pixels:
        m = max(r, g, b)        # วัดความ "สว่าง" ของพิกเซล (ยิ่งใกล้ดำ ยิ่งต่ำ)
        if m <= t:
            new_pixels.append((r, g, b, 0))   # ดำ/ใกล้ดำ -> โปร่งใส
        else:
            # ทำขอบนุ่ม: ยิ่งใกล้ threshold ยิ่งโปร่งขึ้น
            alpha = int(a * (m - t) / (255 - t))
            if alpha < 0: alpha = 0
            if alpha > 255: alpha = 255
            new_pixels.append((r, g, b, alpha))

    im.putdata(new_pixels)

    # feather (เบลอนิดเพื่อลดขอบคม)
    if feather and feather > 0:
        r, g, b, a = im.split()
        a = a.filter(ImageFilter.GaussianBlur(feather))
        im = Image.merge("RGBA", (r, g, b, a))
    return im

def circle_crop(im: Image.Image, size=(40, 40)) -> Image.Image:
    im = ImageOps.fit(im, size, method=Image.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size[0], size[1]), fill=255)
    im.putalpha(mask)
    return im

# ---- โหลดรูปโปรไฟล์จาก DB ----
blob = get_profile_image_by_username(login_username)
if blob:
    img = Image.open(io.BytesIO(blob)).convert("RGBA")
else:
    img = Image.open(r"C:\Python\project\default_user.png").convert("RGBA")  # รูป default

img = circle_crop(img, (40,40))
profile_img = ctk.CTkImage(light_image=img, dark_image=img, size=(40,40))

# ---- ใส่ใน CTkButton ----
def open_profile():
    print("กดโปรไฟล์แล้ว")  # จะเปลี่ยนเป็นหน้าโปรไฟล์ทีหลังได้

profile_btn = ctk.CTkButton(
    hearder,
    image=profile_img,
    text="",
    fg_color="#b868e6",
    hover_color="#9a79f7",
    width=45,
    height=45,
    corner_radius=22,
    command=open_profile
)
profile_btn.pack(side=RIGHT, padx=10)
profile_btn.image = profile_img
search = ctk.CTkEntry(hearder,placeholder_text="ค้นหา",width=200,height=30,fg_color="white",font=("JasmineUPC_Bold",14))
search.pack(side=RIGHT)








main.mainloop()

