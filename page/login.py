import customtkinter as ctk
from tkinter import messagebox, BooleanVar
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
import subprocess, sys, os, sqlite3

# ---------- DB ----------
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db"))

# ---------- Theme ----------
ctk.set_appearance_mode("light")
# ตั้งโหมดสีของ CustomTkinter ให้อยู่ในโหมด light
ctk.set_default_color_theme("blue")
# ตั้งธีมสีหลักของ CustomTkinter เป็น blue
PURPLE_PRIMARY = "#7B66E3"
# สร้างค่าคงที่สีม่วงหลักสำหรับใช้ใน UI
PURPLE_ACCENT  = "#B388FF"
# สร้างค่าคงที่สีม่วงรองสำหรับปุ่มและองค์ประกอบอื่น
BG_SOFT        = "#F7F5FF"
# สร้างค่าคงที่สีพื้นหลังอ่อนให้องค์ประกอบหลัก
TEXT_DARK      = "#2F2A44"
# สร้างค่าคงที่สีข้อความเข้มสำหรับตัวหนังสือ

# ---- Perf tuning ----
RESIZE_DELAY = 60        # ms (60-120 กำลังดี)
# ตั้งค่าดีเลย์หน่วงการ resize ของ layout เป็น 60 มิลลิวินาที
PANEL_SUPERSAMPLE = 2      # เดิม 4 -> 2 เร็วขึ้นมาก
# ตั้งค่าการทำ supersample ของภาพ panel เพื่อลดรอยหยัก
SIZE_STEP = 2              # ปัดขนาดให้เป็น step ช่วย cache ติดง่ายขึ้น
# กำหนด step ของการปัดขนาดเพื่อลดจำนวนรูปใน cache

_pending_job = None
# สร้างตัวแปรเก็บงาน callback ที่ตั้งไว้เพื่อยกเลิกได้
_last_bg_size = (0, 0)
# เก็บขนาดพื้นหลังล่าสุดที่เรนเดอร์ไว้เพื่อหลีกเลี่ยงการทำงานซ้ำ
_last_panel_size = (0, 0)
# เก็บขนาด panel ล่าสุดที่ใช้เพื่อหลีกเลี่ยงการคำนวณซ้ำ

_bg_cache = {}             # {(w,h): PhotoImage}
# สร้างดิกแคชสำหรับเก็บ PhotoImage ของพื้นหลังตามขนาด
_panel_cache = {}          # {(w,h): PhotoImage}
# สร้างดิกแคชสำหรับเก็บ PhotoImage ของ panel ตามขนาด

# ---------- Window ----------
Login = ctk.CTk()
# สร้างหน้าต่างหลักของ CustomTkinter และเก็บไว้ในตัวแปร Login
Login.title("Purple Album — เข้าสู่ระบบ")
# ตั้งชื่อหน้าต่างเป็น Purple Album (ข้อความมีอักขระเพี้ยน)
Login.geometry("900x600")
# กำหนดขนาดเริ่มต้นของหน้าต่างเป็น 900x600 พิกเซล
Login.minsize(800, 520)
# ตั้งค่าขนาดขั้นต่ำของหน้าต่างไว้ที่ 800x520
Login.configure(fg_color=BG_SOFT)
# ตั้งค่าโทนสีพื้นของหน้าต่างให้ตรงกับ BG_SOFT

# ---------- Canvas + BG ----------
canvas = tk.Canvas(Login, highlightthickness=0, bd=0)
# สร้างวิดเจ็ต Canvas ของ Tkinter เพื่อวาดพื้นหลัง
canvas.pack(fill="both", expand=True)
# วาง Canvas ให้ขยายเต็มหน้าต่างทั้งกว้างและสูง

BG_PATH = r"C:\Python\project\\bgstore.png"
# กำหนดพาธไฟล์ภาพพื้นหลังแบบ raw string
bg_raw = Image.open(BG_PATH)
# เปิดไฟล์ภาพพื้นหลังด้วย Pillow และเก็บในตัวแปร bg_raw
bg_img = ImageTk.PhotoImage(bg_raw.resize((900, 600)))
# สร้าง PhotoImage จากภาพหลัง resize เป็น 900x600
bg_id  = canvas.create_image(0, 0, image=bg_img, anchor="nw")
# วางภาพพื้นหลังลงบน Canvas ที่มุมซ้ายบน

def _rounded_size(w, h):
# เริ่มประกาศฟังก์ชัน _rounded_size สำหรับปัดขนาด
    # ปัดขนาดให้เข้า step เพื่อลดจำนวนคีย์ใน cache
    return (max(1, (w // SIZE_STEP) * SIZE_STEP),
    # คืนค่าความกว้างหลังปัดให้หาร SIZE_STEP ลงตัวอย่างน้อย 1
            max(1, (h // SIZE_STEP) * SIZE_STEP))
            # คืนค่าความสูงหลังปัดให้หาร SIZE_STEP ลงตัวอย่างน้อย 1

def resize_bg(w, h, final=False):
# เริ่มประกาศฟังก์ชัน resize_bg สำหรับปรับขนาดพื้นหลัง
    global _last_bg_size
    # ระบุว่าจะใช้ตัวแปร _last_bg_size จากสโคปภายนอก
    w, h = _rounded_size(w, h)
    # ปัดขนาดใหม่ให้ลง step ด้วย _rounded_size
    if (w, h) == _last_bg_size and not final:
    # ถ้าขนาดยังเหมือนเดิมและไม่ได้เรียกแบบ final ให้หยุดทำงาน
        return
        # คืนค่าทันทีเมื่อไม่ต้องอัปเดตภาพพื้นหลัง

    key = (w, h, 'final' if final else 'fast')
    # สร้างคีย์สำหรับแคชโดยรวมขนาดและสถานะ final หรือ fast
    if key in _bg_cache:
    # ถ้าพบภาพในแคชอยู่แล้วให้ใช้ซ้ำทันที
        canvas.itemconfigure(bg_id, image=_bg_cache[key])
        # อัปเดตรูปภาพบน canvas เป็นรูปจากแคช
        canvas.bg_img = _bg_cache[key]
        # เก็บอ้างอิงภาพไว้ที่ canvas เพื่อไม่ให้โดนเก็บจาก GC
    else:
    # ถ้าไม่พบในแคช ให้สร้างภาพใหม่
        # เร็ว: BILINEAR ขณะลาก  |  ชัด: LANCZOS เมื่อปล่อยเมาส์
        resample = Image.LANCZOS if final else Image.BILINEAR
        # เลือกใช้ LANCZOS เมื่อ final และใช้ BILINEAR เมื่อต้องการเร็ว
        resized = bg_raw.resize((w, h), resample=resample)
        # Resize ภาพต้นฉบับตามขนาดที่คำนวณได้
        img = ImageTk.PhotoImage(resized)
        # แปลงภาพที่ปรับขนาดแล้วเป็น PhotoImage
        _bg_cache[key] = img
        # เก็บภาพใหม่ลงในแคชพื้นหลัง
        canvas.itemconfigure(bg_id, image=img)
        # อัปเดตภาพบน canvas ให้เป็นภาพใหม่ที่สร้าง
        canvas.bg_img = img
        # เก็บอ้างอิงภาพไว้บน canvas อีกครั้ง

    _last_bg_size = (w, h)
    # อัปเดตตัวแปร _last_bg_size ให้จำขนาดล่าสุด

# ---------- Rounded panel image (transparent) ----------
def make_panel_img(w, h, radius=28, border=12, outer="#BFAEF7", inner=BG_SOFT):
# ประกาศฟังก์ชัน make_panel_img สำหรับสร้างภาพ panel
    s = PANEL_SUPERSAMPLE
    # กำหนดตัวคูณ supersample เพื่อนำมาใช้เพิ่มความละเอียด
    W, H = w * s, h * s
    # คำนวณความกว้างและความสูงใหม่หลังคูณด้วย supersample
    R, B = radius * s, border * s
    # คำนวณรัศมีและความหนาขอบหลังคูณ supersample

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # สร้างภาพ RGBA โปร่งใสขนาด supersample
    d = ImageDraw.Draw(img)
    # สร้างออบเจ็กต์วาดกราฟิกจาก Pillow
    d.rounded_rectangle([0, 0, W, H], radius=R, fill=outer)
    # วาดสี่เหลี่ยมมุมโค้งด้านนอกสี outer ลงบนภาพ
    d.rounded_rectangle([B, B, W - B, H - B], radius=R, fill=inner)
    # วาดสี่เหลี่ยมมุมโค้งด้านในสี inner ทิ้งกรอบไว้

    return img.resize((w, h), Image.LANCZOS)
    # ย่อภาพกลับสู่ขนาดที่ต้องการด้วย LANCZOS แล้วคืนค่า

panel_img  = ImageTk.PhotoImage(make_panel_img(820, 520))
# สร้าง PhotoImage ของ panel เริ่มต้นขนาด 820x520 พิกเซล
panel_id   = canvas.create_image(0, 0, image=panel_img, anchor="center")
# วางภาพ panel ลงบน canvas โดยยึดกลาง

# ---------- Container on panel ----------
container = ctk.CTkFrame(Login, fg_color="transparent", corner_radius=0)
# สร้างเฟรมโปร่งใสสำหรับเป็น container หลักของ UI
container_win = canvas.create_window(0, 0, window=container, anchor="center")
# นำเฟรมไปวางใน canvas ด้วย create_window ตรงกลาง

# ---------- UI inside container ----------
logoimg = r"C:\Python\project\LOGOproject.png"
# กำหนดพาธรูปโลโก้สำหรับนำมาใช้
logo_ctk = ctk.CTkImage(
# สร้างอ็อบเจ็กต์ CTkImage และเปิดไฟล์สำหรับภาพโหมดสว่าง
    light_image=Image.open(logoimg),
    # ระบุภาพสำหรับโหมดสว่างของ CustomTkinter
    dark_image=Image.open(logoimg),
    # ระบุภาพเดียวกันให้ใช้ตอนโหมดมืด
    size=(100, 100)
    # ตั้งขนาดภาพโลโก้เป็น 100x100 พิกเซล
)
# ปิดวงเล็บและจบการสร้าง CTkImage
ctk.CTkLabel(container, image=logo_ctk, text="").pack(pady=(18, 6))
# สร้าง Label เพื่อแสดงโลโก้และแพ็กด้วย padding

ctk.CTkLabel(container, text="เข้าสู่ระบบ",
# สร้าง Label ข้อความหัวเรื่อง (ข้อความเพี้ยนเพราะ encoding)
             font=ctk.CTkFont(family="JasmineUPC", size=30, weight="bold"),
             # กำหนดฟอนต์ Segoe UI ขนาด 22 และน้ำหนัก bold
             text_color=PURPLE_PRIMARY).pack(pady=(0, 8))
             # ตั้งสีข้อความของหัวเรื่องเป็น PURPLE_PRIMARY แล้ว pack

form = ctk.CTkFrame(container, fg_color="transparent")
# สร้างเฟรม form โปร่งใสสำหรับจัดวางช่องกรอก
form.pack(padx=28, pady=10, fill="x")
# วาง form ด้วย padding และให้ขยายตามแนวนอน
form.grid_columnconfigure(0, weight=1)
# กำหนดให้คอลัมน์ 0 ของ form สามารถขยายได้
form.grid_columnconfigure(1, weight=0)
# กำหนดให้คอลัมน์ 1 ของ form ไม่มีการขยายเพิ่ม

username_label = ctk.CTkLabel(form, text="Username", anchor="w",
                              font=ctk.CTkFont(size=16), text_color=TEXT_DARK)
# สร้าง Label ของช่อง Username พร้อมฟอนต์ขนาด 16 และสีข้อความโทนเข้ม
username_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=(0, 6), pady=(4, 4))
# วาง Label Username ไว้แถว 0 คอลัมน์ 0-1 ติดซ้ายและเว้นระยะเล็กน้อย


user_row = ctk.CTkFrame(form, fg_color="transparent")
# สร้างเฟรม user_row เพื่อวางไอคอนและช่อง username
user_row.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))
# วาง user_row ใน grid แถว 1 ให้ขยายตามแนวนอน
user_row.grid_columnconfigure(1, weight=1)
# ตั้งคอลัมน์ที่ 1 ใน user_row ให้ขยายเต็มที่
ctk.CTkLabel(user_row, text="👤", width=26).grid(row=0, column=0, padx=(0, 8))
# สร้าง Label ขนาดคงที่สำหรับไอคอน (อักขระเพี้ยน)
user_entry = ctk.CTkEntry(user_row, placeholder_text="กรอกชื่อผู้ใช้", height=40)
# สร้างช่องกรอก user_entry พร้อม placeholder (ข้อความเพี้ยน)
user_entry.grid(row=0, column=1, sticky="we")
# จัดวางช่องกรอก username ให้ยืดเต็มคอลัมน์

password_label = ctk.CTkLabel(form, text="Password", anchor="w",
                              font=ctk.CTkFont(size=16), text_color=TEXT_DARK)
# สร้าง Label ของช่อง Password พร้อมฟอนต์เดียวกันและชิดซ้าย
password_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=(0, 6), pady=(6, 4))
# วาง Label Password ที่แถว 2 เหนือช่องรหัสผ่าน


pwd_row = ctk.CTkFrame(form, fg_color="transparent")
# สร้างเฟรม pwd_row สำหรับส่วนรหัสผ่าน
pwd_row.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 8))
# วาง pwd_row ไว้แถว 3 ให้ขยายตามแนวนอน
pwd_row.grid_columnconfigure(1, weight=1)
# ตั้งคอลัมน์ที่ 1 ของ pwd_row ให้ขยายได้
ctk.CTkLabel(pwd_row, text="🔒", width=26).grid(row=0, column=0, padx=(0, 8))
# สร้าง Label สำหรับไอคอนรหัสผ่าน (อักขระเพี้ยน)
pwd_entry = ctk.CTkEntry(pwd_row, placeholder_text="กรอกรหัสผ่าน", height=40)
# สร้างช่องกรอก pwd_entry พร้อม placeholder (ข้อความเพี้ยน)
pwd_entry.grid(row=0, column=1, sticky="we", padx=(0, 8))
# จัดวางช่องกรอก password พร้อม padding ด้านขวา

masked = BooleanVar(value=True)
# สร้างตัวแปร BooleanVar ชื่อ masked เริ่มต้นเป็น True
def _apply_mask(*_):
# ประกาศฟังก์ชัน _apply_mask สำหรับกำหนดการซ่อนรหัสผ่าน
    pwd_entry.configure(show="*" if masked.get() and pwd_entry.get() else "")
    # ถ้าเลือกซ่อนและมีข้อความให้ใช้ show="*" มิฉะนั้นปล่อยว่าง
def _toggle():
# ประกาศฟังก์ชัน _toggle สำหรับสลับสถานะการซ่อนรหัสผ่าน
    masked.set(not masked.get())
    # กลับค่าของ masked เป็นตรงข้ามเมื่อผู้ใช้กดปุ่ม
    toggle_btn.configure(text="ซ่อน" if not masked.get() else "แสดง")
    # ปรับข้อความบนปุ่ม toggle ให้ตรงกับสถานะปัจจุบัน (ข้อความเพี้ยน)
    _apply_mask()
    # เรียก _apply_mask เพื่อรีเฟรชการซ่อนรหัสทันที
pwd_entry.bind("<KeyRelease>", _apply_mask)
# ผูกเหตุการณ์ KeyRelease กับ _apply_mask เพื่ออัปเดตแบบเรียลไทม์
pwd_entry.bind("<FocusOut>", _apply_mask)
# ผูกเหตุการณ์ FocusOut กับ _apply_mask เพื่อรีเซ็ตเมื่อออกจากช่อง

toggle_btn = ctk.CTkButton(pwd_row, text="แสดง", width=64, height=34,
# สร้างปุ่ม toggle_btn สำหรับซ่อน/แสดงรหัสผ่าน
                           fg_color=PURPLE_ACCENT, hover_color=PURPLE_PRIMARY,
                           # ตั้งสีพื้นและสี hover ของปุ่ม toggle ให้เข้ากับธีม
                           command=_toggle)
                           # ผูกคำสั่งของปุ่ม toggle ให้เรียก _toggle
toggle_btn.grid(row=0, column=2)
# จัดวางปุ่ม toggle ในคอลัมน์ 2 ของแถวรหัสผ่าน

links = ctk.CTkFrame(container, fg_color="transparent")
# สร้างเฟรม links สำหรับปุ่มสมัครและลืมรหัสผ่าน
links.pack(fill="x", padx=28, pady=(8, 0))
# วาง links ด้วย padding และให้เต็มความกว้าง

def _go_register():
# ประกาศฟังก์ชัน _go_register สำหรับไปหน้า register.py
    args = [sys.executable, r"C:\Python\project\page\register.py"]
    # เตรียมลิสต์คำสั่งเรียก Python กับไฟล์ register.py
    if not _fullscreen_state["value"]:
    # ถ้าไม่ได้อยู่โหมดเต็มจอให้เพิ่มอาร์กิวเมนต์ --windowed
        args.append("--windowed")
        # เพิ่มอาร์กิวเมนต์ --windowed เพื่อบังคับเปิดแบบหน้าต่าง
    Login.destroy()
    # ทำลายหน้าต่าง Login ปัจจุบันก่อนเปิดหน้าต่างใหม่
    subprocess.Popen(args)
    # เปิดโปรแกรม register.py ด้วย subprocess.Popen
def _go_forgot():
# ประกาศฟังก์ชัน _go_forgot สำหรับไปหน้า forgot.py
    Login.destroy()
    # ทำลายหน้าต่าง Login ก่อนเปลี่ยนไป forgot.py
    subprocess.Popen([sys.executable, r"C:\Python\project\page\forgot.py"])
    # เปิด forgot.py ด้วย subprocess.Popen

ctk.CTkButton(links, text="ลงทะเบียน", corner_radius=18,
# สร้างปุ่มไปหน้าสมัครสมาชิก (ข้อความบนปุ่มเพี้ยน)
              fg_color="white", hover_color=BG_SOFT, text_color=PURPLE_PRIMARY,
              # ตั้งสีพื้น สี hover และสีตัวอักษรของปุ่มสมัครให้เป็นโทนม่วง
              border_width=2, border_color=PURPLE_PRIMARY, width=140,
              # ตั้งความกว้างและสีขอบของปุ่มสมัครสมาชิก
              command=_go_register).pack(side="left", padx=(0, 10), pady=6)
              # ผูกคำสั่งของปุ่มสมัครให้เรียก _go_register

ctk.CTkButton(links, text="ลืมรหัสผ่าน", corner_radius=18,
# สร้างปุ่มสำหรับลืมรหัสผ่าน (ข้อความเพี้ยน)
              fg_color="white", hover_color=BG_SOFT, text_color=PURPLE_PRIMARY,
              # ตั้งสี hover และสีตัวอักษรของปุ่มลืมรหัสผ่าน
              border_width=2, border_color=PURPLE_PRIMARY, width=140,
              # กำหนดสีขอบของปุ่มลืมรหัสผ่านเป็น PURPLE_PRIMARY
              command=_go_forgot).pack(side="left", pady=6)
              # ผูกคำสั่งของปุ่มลืมรหัสผ่านให้เรียก _go_forgot

def on_login():
# บรรทัดว่างก่อนฟังก์ชัน on_login
    u = user_entry.get().strip()
    # ประกาศฟังก์ชัน on_login เมื่อผู้ใช้กดปุ่มเข้าสู่ระบบ
    p = pwd_entry.get().strip()
    # อ่านค่า username จากช่องและตัดช่องว่างหัวท้าย
    if not u or not p:
    # อ่านค่า password จากช่องและตัดช่องว่างหัวท้าย
        messagebox.showwarning("กรอกให้ครบ", "กรุณากรอกทั้ง Username และ Password")
        # ถ้า username หรือ password ว่างให้แจ้งเตือนและหยุดทำงาน
        return
        # คืนค่าทันทีเพื่อไม่ไปตรวจฐานข้อมูลเมื่อข้อมูลไม่ครบ
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    # เชื่อมต่อฐานข้อมูล SQLite และสร้าง cursor เพื่อ query
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p))
    # ดึงข้อมูลผู้ใช้ที่ username และ password ตรงกันจากฐานข้อมูล
    row = c.fetchone(); conn.close()
    # อ่านแถวแรกจากผลลัพธ์แล้วปิดการเชื่อมต่อฐานข้อมูล
    if row:
    # ถ้าพบข้อมูลผู้ใช้ให้แจ้งล็อกอินสำเร็จ
        messagebox.showinfo("เข้าสู่ระบบ", f"ยินดีต้อนรับ, {u}")
        # แสดง messagebox แจ้งผลสำเร็จพร้อมระบุชื่อผู้ใช้ (ข้อความเพี้ยน)
        Login.destroy()
        # ปิดหน้าต่าง Login เพื่อเตรียมเปิดหน้าหลัก
        subprocess.Popen([sys.executable, r"C:\Python\project\page\main.py",u])
        # เปิด main.py ผ่าน subprocess เพื่อเข้าสู่หน้าใช้งานหลัก
    else:
    # กรณีไม่พบข้อมูลผู้ใช้ให้เข้าสู่เงื่อนไข else
        messagebox.showwarning("ผิดพลาด", "ไม่มี Username/Password หรือรหัสผ่านไม่ถูกต้อง")
        # แสดง messagebox เตือนว่าชื่อหรือรหัสผ่านไม่ถูกต้อง (ข้อความเพี้ยน)

ctk.CTkButton(container, text="เข้าสู่ระบบ", text_color="white",
# สร้างปุ่มเข้าสู่ระบบบน container (ข้อความเพี้ยน)
              height=46, corner_radius=22,
              # ตั้งความสูงปุ่มและค่ามุมโค้งให้ดูโค้งมน
              fg_color="#B388FF", hover_color="#8D50F7",
              # ตั้งสีพื้นและสี hover ของปุ่มเข้าสู่ระบบ
              command=on_login).pack(pady=18, ipadx=16)
              # ผูกปุ่มเข้าสู่ระบบให้เรียก on_login

# ---------- Layout (ให้ทุกอย่าง "อยู่ในกรอบ") ----------
MARGIN_W = 40   # เว้นข้างซ้าย-ขวาของแผง
# คอมเมนต์หัวข้อส่วนจัดเลย์เอาต์ของ panel
MARGIN_H = 80   # เว้นด้านบน-ล่างของแผง (เผื่อโลโก้/หัวข้อ/ปุ่ม)
# กำหนดระยะกันขอบแนวนอนของเนื้อหาภายใน panel

def layout_panel(final=False):
# บรรทัดว่างก่อนฟังก์ชัน layout_panel
    global _last_panel_size
    # ประกาศฟังก์ชัน layout_panel สำหรับคำนวณขนาด panel

    w = max(Login.winfo_width(),  400)
    # อ่านความกว้างปัจจุบันของหน้าต่างโดยมีขั้นต่ำ 400
    h = max(Login.winfo_height(), 300)
    # อ่านความสูงปัจจุบันของหน้าต่างโดยมีขั้นต่ำ 300

    # BG: เร็ว/ชัดตามโหมด
    resize_bg(w, h, final=final)
    # เรียก resize_bg เพื่ออัปเดตพื้นหลังตามขนาดหน้าต่าง

    container.update_idletasks()
    # เรียก update_idletasks เพื่อให้ Tk ประมวลผลงานค้าง
    need_w = container.winfo_reqwidth()
    # อ่านความกว้างที่ container ต้องใช้จริง
    need_h = container.winfo_reqheight()
    # อ่านความสูงที่ container ต้องใช้จริง

    panel_w = max(min(int(w * 0.86), w - 40), need_w + MARGIN_W)
    # คำนวณความกว้างของ panel โดยจำกัดไม่เกิน 86% และไม่น้อยกว่าเนื้อหา+margin
    panel_h = max(min(int(h * 0.78), h - 40), need_h + MARGIN_H)
    # คำนวณความสูงของ panel โดยจำกัดไม่เกิน 78% และไม่น้อยกว่าเนื้อหา+margin

    # ปัดขนาดช่วย cache
    panel_w, panel_h = _rounded_size(panel_w, panel_h)
    # ปัดความกว้างและความสูงของ panel ให้ลง step
    if (panel_w, panel_h) != _last_panel_size:
    # ถ้าขนาด panel เปลี่ยนจากครั้งล่าสุดจึงคำนวณภาพใหม่
        key = (panel_w, panel_h)
        # สร้างคีย์สำหรับดึงภาพจากแคช panel ตามขนาด
        if key in _panel_cache:
        # ถ้าพบภาพในแคช panel ให้ใช้ซ้ำ
            img = _panel_cache[key]
            # ถ้าไม่พบในแคชให้สร้างภาพ panel ใหม่
        else:
        # สร้าง PhotoImage ใหม่จาก make_panel_img ตามขนาดที่คำนวณ
            img = ImageTk.PhotoImage(make_panel_img(panel_w, panel_h,
            # กำหนดพารามิเตอร์ radius และ border ให้ภาพใหม่
                                                    radius=28, border=12,
                                                    # ระบุสี outer ของ panel สำหรับภาพใหม่
                                                    outer="#BFAEF7", inner=BG_SOFT))
                                                    # ระบุสี inner ของ panel สำหรับภาพใหม่
            _panel_cache[key] = img
            # เก็บภาพ panel ที่สร้างใหม่ลงแคช

        canvas.itemconfigure(panel_id, image=img)
        # อัปเดตภาพของ panel บน canvas ให้ใช้ภาพล่าสุด
        canvas.panel_img = img
        # เก็บอ้างอิงภาพ panel ไว้บน canvas
        _last_panel_size = (panel_w, panel_h)
        # บันทึกขนาด panel ล่าสุดลงตัวแปรสถานะ

    cx, cy = w // 2, h // 2
    # คำนวณตำแหน่งกึ่งกลางของหน้าต่างทั้งกว้างและสูง
    canvas.coords(panel_id, cx, cy)
    # ย้ายภาพ panel ไปไว้ตำแหน่งกึ่งกลางหน้าต่าง

    PADDING_X = 80
    # กำหนดค่า padding แนวนอนภายใน panel
    PADDING_Y = 120
    # กำหนดค่า padding แนวตั้งภายใน panel
    inner_w = max(panel_w - PADDING_X, need_w)
    # คำนวณความกว้างภายในของ container จากขนาด panel
    inner_h = max(panel_h - PADDING_Y, need_h)
    # คำนวณความสูงภายในของ container จากขนาด panel
    canvas.coords(container_win, cx, cy)
    # ย้าย container_win ไปอยู่ตำแหน่งกึ่งกลาง
    canvas.itemconfigure(container_win, width=inner_w, height=inner_h)
    # ตั้งความกว้างและความสูงของหน้าต่างบน canvas ให้เท่ากับพื้นที่ภายใน



# ---------- Fullscreen toggle (F11 / ESC) ----------
_fullscreen_state = {"value": False, "geometry": None}
# สร้างดิกเก็บสถานะ fullscreen ว่ากำลังเปิดและ geometry เดิม

def _apply_layout_later():
# ประกาศฟังก์ชัน _apply_layout_later เพื่อเรียก layout_panel ทีหลัง
    # re-run panel layout after switching fullscreen state
    Login.after(20, lambda: layout_panel(final=True))
    # ตั้ง timer 20 มิลลิวินาทีเพื่อเรียก layout_panel แบบ final

def _enter_fullscreen():
# ประกาศฟังก์ชัน _enter_fullscreen เพื่อเข้าโหมดเต็มหน้าจอ
    if _fullscreen_state["value"]:
    # ถ้าอยู่ fullscreen อยู่แล้วให้หยุดทำงานทันที
        return
        # คืนค่าทันทีเพื่อไม่ทำงานต่อเมื่ออยู่ fullscreen แล้ว
    _fullscreen_state["value"] = True
    # ตั้งค่าคีย์ value ในสถานะให้เป็น True ว่ากำลัง fullscreen
    _fullscreen_state["geometry"] = Login.winfo_geometry()
    # เก็บ geometry ปัจจุบันไว้เพื่อกลับมาใช้ภายหลัง
    try:
    # พยายามตั้งสถานะหน้าต่างให้เป็น zoomed (ขยายเต็มจอแบบหน้าต่าง)
        Login.state("zoomed")
        # ถ้าคำสั่ง state("zoomed") ใช้ไม่ได้จะเกิดข้อผิดพลาด
    except tk.TclError:
    # จับข้อผิดพลาด TclError แล้วปล่อยผ่าน
        pass
        # ใช้ pass เพื่อไม่ทำอะไรต่อในบล็อก except
    Login.attributes("-fullscreen", True)
    # ตั้ง attribute ให้ Tk อยู่ในโหมด fullscreen จริง
    Login.geometry(f"{Login.winfo_screenwidth()}x{Login.winfo_screenheight()}+0+0")
    # ตั้ง geometry เป็นขนาดเต็มหน้าจอพร้อมเลื่อนตำแหน่งที่มุมซ้ายบน
    _apply_layout_later()
    # เรียก _apply_layout_later เพื่อจัด layout หลังเข้า fullscreen

def _leave_fullscreen():
# ประกาศฟังก์ชัน _leave_fullscreen สำหรับออกจากโหมดเต็มจอ
    if not _fullscreen_state["value"]:
    # ถ้าไม่อยู่ fullscreen ให้หยุดทำงาน
        return
        # คืนค่าทันทีเพื่อไม่ทำงานต่อเมื่อตอนนี้ไม่ fullscreen
    _fullscreen_state["value"] = False
    # ตั้งสถานะ value ให้เป็น False เพื่อบอกว่าออกจาก fullscreen แล้ว
    Login.attributes("-fullscreen", False)
    # ปิด attribute fullscreen บนหน้าต่าง
    try:
    # พยายามตั้ง state กลับเป็น normal
        Login.state("normal")
        # หากการตั้ง state ล้มเหลวจะเกิด TclError
    except tk.TclError:
    # จับ TclError เพื่อไม่ให้โปรแกรมหยุด
        pass
        # ใช้ pass เพื่อข้ามเมื่อจับข้อผิดพลาดแล้ว
    if _fullscreen_state["geometry"]:
    # ถ้ามี geometry เดิมเก็บไว้ให้ใช้คืนค่า
        Login.geometry(_fullscreen_state["geometry"])
        # กำหนด geometry กลับเป็นค่าที่เก็บไว้ก่อนเข้า fullscreen
    _apply_layout_later()
    # เรียก _apply_layout_later เพื่อจัด layout หลังออก fullscreen

def _toggle_fullscreen(event=None):
# ประกาศฟังก์ชัน _toggle_fullscreen สำหรับสลับสถานะ fullscreen
    if _fullscreen_state["value"]:
    # ถ้าอยู่ fullscreen อยู่ให้เรียก _leave_fullscreen
        _leave_fullscreen()
        # ถ้าไม่อยู่ fullscreen ให้เรียก _enter_fullscreen
    else:
    # แสดงว่ากำลังออก fullscreen ผ่านการเรียก _leave_fullscreen
        _enter_fullscreen()
        # แสดงว่ากำลังเข้า fullscreen ผ่านการเรียก _enter_fullscreen
    return "break"
    # คืนค่า "break" เพื่อหยุดการส่งอีเวนต์ต่อ

def _exit_fullscreen(event=None):
# ประกาศฟังก์ชัน _exit_fullscreen เพื่อตอบสนองปุ่ม Escape
    _leave_fullscreen()
    # เรียก _leave_fullscreen เพื่อออก fullscreen เมื่อกด ESC
    return "break"
    # คืน "break" เพื่อป้องกันอีเวนต์ไปถึง handler อื่น

Login.bind("<F11>", _toggle_fullscreen)
# ผูกปุ่ม F11 ให้เรียก _toggle_fullscreen เมื่อกด
Login.bind("<Escape>", _exit_fullscreen)
# ผูกปุ่ม Escape ให้เรียก _exit_fullscreen

_force_full = "--start-fullscreen" in sys.argv
# ตรวจว่าอาร์กิวเมนต์ --start-fullscreen ถูกส่งมาหรือไม่
_want_windowed = "--windowed" in sys.argv
# ตรวจว่าอาร์กิวเมนต์ --windowed ถูกส่งมาหรือไม่
if _force_full or not _want_windowed:
# ถ้าต้องบังคับ fullscreen หรือไม่ได้ขอ windowed ให้เข้า fullscreen ทันที
    Login.after(0, _enter_fullscreen)
    # ตั้ง callback ให้เรียก _enter_fullscreen ทันทีที่ mainloop เริ่ม

# ---------- Resize Optimization (Debounce + Cache) ----------

def _on_configure(_event):
# ประกาศฟังก์ชัน _on_configure เพื่อจัดการอีเวนต์ Resize
    # แสดงพรีวิวเร็วขณะลาก/ย่อหน้าต่าง
    layout_panel(final=False)
    # เรียก layout_panel(final=False) เพื่ออัปเดตพื้นผิวแบบด่วน

    # ถ้าผู้ใช้หยุดลากสักพัก ค่อยเรนเดอร์คมชัดและ cache ไว้
    global _pending_job
    # ระบุตัวแปร _pending_job ว่าใช้ภายนอก
    if _pending_job is not None:
    # ถ้ามีงานที่ตั้งไว้แล้วให้ยกเลิกก่อน
        Login.after_cancel(_pending_job)
        # ตั้งงานใหม่ด้วย Login.after เพื่อนับเวลา RESIZE_DELAY
    _pending_job = Login.after(RESIZE_DELAY, lambda: layout_panel(final=True))
    # เมื่อครบเวลาให้เรียก layout_panel(final=True) จาก lambda

# ผูกอีเวนต์เมื่อขนาดหน้าต่างเปลี่ยน
Login.bind("<Configure>", _on_configure)
# ผูกอีเวนต์ <Configure> ของหน้าต่างให้เรียก _on_configure

# เรียกครั้งแรกตอนเปิดหน้าต่าง
Login.update_idletasks()
# เรียก layout_panel(final=True) หนึ่งครั้งก่อนเข้า mainloop
layout_panel(final=True)
# บรรทัดว่างก่อนเข้า mainloop

Login.mainloop()
