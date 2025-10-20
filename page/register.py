import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
from PIL import Image
import subprocess
import sys
import os,sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db")
DB_PATH = os.path.abspath(DB_PATH)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PURPLE_PRIMARY = "#7B66E3"
PURPLE_ACCENT  = "#B388FF"
BG_SOFT        = "#F7F5FF"
TEXT_DARK      = "#2F2A44"

# หน้าต่าง
register = ctk.CTk()
register.title("Purple Album — ลงทะเบียน")
register.geometry("900x600+3500")      
register.minsize(800, 520)
register.configure(fg_color=BG_SOFT)

# คอนเทนเนอร์
container = ctk.CTkFrame(register, corner_radius=20, fg_color="#F7F5FF")
container.pack(fill="both", expand=True, padx=24, pady=24)


# รูปโลโก้ (ใช้ raw string ป้องกัน \P)
logo = r"C:\Python\project\LOGOproject.png"
logo_img = ctk.CTkImage(
    light_image=Image.open(logo),
    dark_image=Image.open(logo),
    size=(100, 100)
)
logo_label = ctk.CTkLabel(container, image=logo_img, text="")
logo_label.pack(pady=(8,6))

# หัวข้อ
title = ctk.CTkLabel(
    container, text="ลงทะเบียน",
    font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
    text_color=PURPLE_PRIMARY
)
title.pack(pady=4)

form = ctk.CTkFrame(container, fg_color="transparent")
form.pack(padx=28, pady=5, fill="x")

# ฟิลด์ Username
userlabel = ctk.CTkLabel(form, text="Username", anchor="w",
                         font=ctk.CTkFont(size=16), text_color=TEXT_DARK)
userlabel.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=(0, 4))

userentry = ctk.CTkEntry(form, placeholder_text="กรอกชื่อผู้ใช้", height=40)
userentry.grid(row=1, column=0, sticky="we", pady=(0, 12))

form.grid_columnconfigure(0, weight=1)

# ฟิลด์ Password
passlabel = ctk.CTkLabel(form, text="Password", anchor="w",
                         font=ctk.CTkFont(size=16), text_color=TEXT_DARK)
passlabel.grid(row=2, column=0, sticky="w", padx=(0, 0), pady=(0, 4))

pass_entry = ctk.CTkEntry(form, placeholder_text="กรอกรหัสผ่าน", height=40)
pass_entry.grid(row=3, column=0, sticky="we", pady=(0, 12))

# ฟิลด์ยืนยันPassword
pass2label = ctk.CTkLabel(form, text="Password", anchor="w",
                         font=ctk.CTkFont(size=16), text_color=TEXT_DARK)
pass2label.grid(row=4, column=0, sticky="w", padx=(0, 0), pady=(0, 4))

pass2_entry = ctk.CTkEntry(form, placeholder_text="กรอกรหัสผ่านอีกครั้งเพื่อยืนยัน", height=40)
pass2_entry.grid(row=5, column=0, sticky="we", pady=(0, 12))

links_frame = ctk.CTkFrame(container, fg_color="transparent")
links_frame.pack(fill="x", padx=28, pady=(20))
links_frame.grid_columnconfigure((0,1), weight=1)

#ตรวจสอบ

def check ():
    u = userentry.get().strip()
    p1 = pass_entry.get().strip()
    p2 = pass2_entry.get().strip()
    if not u or not p1 or not p2:
        messagebox.showwarning("กรอกให้ครบ", "กรุณากรอกทั้ง Username และ Password")
        return
    
    if p1 == p2:
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        try :
            c.execute('''INSERT INTO users (username,password) VALUES(?,?)''',(u,p1))
            conn.commit()
            c.close()
            conn.commit()
            messagebox.showinfo("ลงทะเบียนสำเร็จ","สมัคสมาชิกเรียบร้อย\nกำลังนำท่านไปหน้าเข้าสู่ระบบ")
            register.destroy()
            subprocess.Popen([sys.executable,r"C:\\Python\\.vscode\\project\\page\\login.py"])
            userentry.delete(0,"end")
            pass_entry.delete(0,"end")
            pass2_entry.delete(0,"end")
        except sqlite3.IntegrityError:
            messagebox.showwarning("ผิดพลาด","Username นี้ถูกใช้แล้ว")
        finally :
            conn.close()
    else:
        messagebox.showwarning("ข้อมูลไม่ครบ","กรุณากรอกรหัสให้ครบ")      
    
def backtolog():
    register.destroy()
    subprocess.Popen([sys.executable,r"C:\Python\project\page\login.py"])
    return

# ฟิลด์ย้อนกลับ
back_login = ctk.CTkButton(
    links_frame, text="ย้อนกลับ",text_color="white", height=46, corner_radius=22,
    fg_color="#B388FF", hover_color="#8D50F7",command=backtolog)
back_login.grid(row=0, column=0, padx=2)


# ฟิลด์สมัครสมาชิก
  
login_btn = ctk.CTkButton(
    links_frame, text="สมัครสมาชิก",text_color="white", height=46, corner_radius=22,
    fg_color="#B388FF", hover_color="#8D50F7",command=check)
login_btn.grid(row=0, column=1, padx=2)
register.mainloop()
