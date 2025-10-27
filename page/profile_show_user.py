import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
import os, sqlite3
from io import BytesIO

# -------- CONFIG --------
LOGIN_USERNAME = "achira"
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH   = os.path.join(BASE_DIR, "database", "Userdata.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DEFAULT_PROFILE_IMAGE = os.path.join(ASSETS_DIR, "default_user.png")

# -------- THEME --------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
PURPLE = "#7B66E3"
BG = "#F7F5FF"
TEXT = "#2F2A44"

# -------- DATABASE --------
def db_conn():
    return sqlite3.connect(DB_PATH)

def get_user(username):
    con = db_conn(); cur = con.cursor()
    cur.execute("""
        SELECT username, first_name, last_name, gender, birth_date, email, phone, profile_image
        FROM users WHERE username=?
    """, (username,))
    row = cur.fetchone()
    con.close()
    return row if row else None

# -------- IMAGE --------
def pil_circle(img, size=180):
    img = img.convert("RGBA"); img.thumbnail((size,size))
    mask = Image.new("L", img.size); draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,img.size[0],img.size[1]), fill=255)
    output = Image.new("RGBA", img.size); output.paste(img, (0,0), mask)
    return output

def blob_to_img(blob):
    from PIL import Image as PIL
    if blob:
        try: img = PIL.open(BytesIO(blob))
        except: img = PIL.open(DEFAULT_PROFILE_IMAGE)
    else:
        img = PIL.open(DEFAULT_PROFILE_IMAGE)
    return ctk.CTkImage(pil_circle(img), size=(180,180))

# -------- UI --------
app = ctk.CTk()
app.title("โปรไฟล์ผู้ใช้")
app.geometry("900x600")
app.configure(fg_color=PURPLE)

# ภายนอก
frame = ctk.CTkFrame(app, fg_color=BG, corner_radius=20)
frame.pack(fill="both", expand=True, padx=40, pady=40)

# หัวข้อ
ctk.CTkLabel(frame, text="โปรไฟล์ผู้ใช้", font=("Mitr", 30, "bold"), text_color=TEXT).pack(pady=10)

# โหลดข้อมูล
user = get_user(LOGIN_USERNAME)
if not user:
    messagebox.showerror("Error", "ไม่พบข้อมูลผู้ใช้")
    app.destroy()

# INNER FRAME (จัดกลาง)
inside = ctk.CTkFrame(frame, fg_color="white", corner_radius=15)
inside.pack(pady=20, ipadx=20, ipady=20)

# รูปโปรไฟล์
avatar = blob_to_img(user[7])
ctk.CTkLabel(inside, image=avatar, text="").pack(pady=10)

# ฟังก์ชันสร้างแถวข้อมูล
def add_row(title, value):
    row = ctk.CTkFrame(inside, fg_color="white")
    row.pack(pady=4)
    ctk.CTkLabel(row, text=f"{title}:", font=("Mitr",18), width=150, anchor="e").pack(side="left")
    ctk.CTkLabel(row, text=value if value else "-", font=("Mitr",18), text_color="#555").pack(side="left", padx=10)

# รายการข้อมูล
add_row("Username", user[0])
add_row("ชื่อ", user[1])
add_row("นามสกุล", user[2])
add_row("เพศ", user[3])
add_row("วันเกิด", user[4])
add_row("อีเมล", user[5])
add_row("เบอร์โทร", user[6])

# ปุ่มด้านล่าง
btns = ctk.CTkFrame(frame, fg_color=BG)
btns.pack()
ctk.CTkButton(btns, text="กลับ", fg_color="#888", width=120).pack(side="left", padx=10, pady=10)
ctk.CTkButton(btns, text="แก้ไขข้อมูล", fg_color=PURPLE, width=160).pack(side="left", padx=10, pady=10)

app.mainloop()
