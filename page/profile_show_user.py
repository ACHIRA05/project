import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageDraw
import os, sqlite3,sys ,subprocess
from io import BytesIO

# -------- CONFIG --------
#รับ username จาก login.py
if len( sys.argv ) > 1: 
    username = sys.argv[1] 
else: 
    username = None
#LOGIN_USERNAME = "achira"
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
profile_show_user = ctk.CTk()
profile_show_user.title("โปรไฟล์ผู้ใช้")
profile_show_user.geometry("900x600")
profile_show_user.configure(fg_color=PURPLE)

# ภายนอก
frame = ctk.CTkFrame(profile_show_user, fg_color=BG, corner_radius=20)
frame.pack(fill="both", expand=True, padx=40, pady=40)

# หัวข้อ
ctk.CTkLabel(frame, text="โปรไฟล์ผู้ใช้", font=("Mitr", 40, "bold"), text_color=TEXT).pack(pady=(30,10))

# โหลดข้อมูล
user = get_user(username)
if not user:
    messagebox.showerror("Error", "ไม่พบข้อมูลผู้ใช้")
    profile_show_user.destroy()

# INNER FRAME (จัดกลาง)
inside = ctk.CTkFrame(frame, fg_color="white", corner_radius=15)
inside.pack(pady=20, padx=80, ipadx=20, ipady=20, fill="x")

# รูปโปรไฟล์
avatar = blob_to_img(user[7])
ctk.CTkLabel(inside, image=avatar, text="").pack(pady=10)

# ฟังก์ชันสร้างแถวข้อมูล
def add_row(title, value):
    row = ctk.CTkFrame(inside, fg_color="white")
    row.pack(pady=4, padx=40, fill="x")
    ctk.CTkLabel(row, text=f"{title}:", font=("Mitr",25), anchor="e").pack(
        side="left", padx=(0, 12), fill="x", expand=True
    )
    ctk.CTkLabel(
        row,
        text=value if value else "-",
        font=("Mitr",25),
        text_color="#555",
        anchor="w",
    ).pack(side="left", padx=(12, 0), fill="x", expand=True)

# รายการข้อมูล
add_row("Username", user[0])
add_row("ชื่อ", user[1])
add_row("นามสกุล", user[2])
add_row("เพศ", user[3])
add_row("วันเกิด", user[4])
add_row("อีเมล", user[5])
add_row("เบอร์โทร", user[6])

def back_page():
    if not username:
        profile_show_user.after(0, profile_show_user.destroy)
        return
    args = [sys.executable, os.path.join(BASE_DIR, "page", "main.py"), username]
    subprocess.Popen(args)
    profile_show_user.after(800, profile_show_user.destroy)
    
# ปุ่มด้านล่าง
btns = ctk.CTkFrame(frame, fg_color=BG)
btns.pack()
def go_edit_page():
    if not username:
        messagebox.showerror("โปรไฟล์", "ไม่พบผู้ใช้สำหรับแก้ไข")
        return
    args = [sys.executable, os.path.join(BASE_DIR, "page", "profile_edit_user.py"), username]
    subprocess.Popen(args)
    profile_show_user.after(800, profile_show_user.destroy)

ctk.CTkButton(btns, text="กลับ", fg_color="#888", width=200,font=ctk.CTkFont(family="Mitr"),command=back_page).pack(side="left", padx=10, pady=10)
ctk.CTkButton(btns, text="แก้ไขข้อมูล", fg_color=PURPLE, width=200,font=ctk.CTkFont(family="Mitr"),command=go_edit_page).pack(side="left", padx=10, pady=10)

# ตัวแปรเก็บขนาด panel
MARGIN_W = 40
MARGIN_H = 80

# จัดวาง panel
def layout_panel(final=False):
    global _last_panel_size
    w = max(profile_show_user.winfo_width(),  400)
    h = max(profile_show_user.winfo_height(), 300)
    frame.update_idletasks()
    need_w = frame.winfo_reqwidth()
    need_h = frame.winfo_reqheight()
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
    profile_show_user.after(20, lambda: layout_panel(final=True))
    
def _enter_fullscreen():
    if _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = True
    _fullscreen_state["geometry"] = profile_show_user.winfo_geometry()
    try:
        profile_show_user.state("zoomed")
    except tk.TclError:
        pass
    profile_show_user.attributes("-fullscreen", True)
    profile_show_user.geometry(f"{profile_show_user.winfo_screenwidth()}x{profile_show_user.winfo_screenheight()}+0+0")
    _apply_layout_later()

def _leave_fullscreen():
    if not _fullscreen_state["value"]:
        return
    _fullscreen_state["value"] = False
    profile_show_user.attributes("-fullscreen", False)
    try:
        profile_show_user.state("normal")
    except tk.TclError:
        pass
    if _fullscreen_state["geometry"]:
        profile_show_user.geometry("1000x600")
    _apply_layout_later()

def _toggle_fullscreen(event=None):
    if _fullscreen_state["value"]:
        _leave_fullscreen()
    else:
        _enter_fullscreen()
    return "break"

def _on_escape_quit(event=None):
    # ปิดแอปทั้งโปรแกรม
    try:
        profile_show_user.destroy()
    except Exception:
        profile_show_user.quit()
    return "break"
profile_show_user.bind("<F11>", _toggle_fullscreen)
profile_show_user.bind("<Escape>", _on_escape_quit)

# เริ่มในโหมด fullscreen 
_force_full = "--start-fullscreen" in sys.argv
_want_windowed = "--windowed" in sys.argv
if _force_full or not _want_windowed:
    profile_show_user.after(0, _enter_fullscreen) 
    
profile_show_user.mainloop()
