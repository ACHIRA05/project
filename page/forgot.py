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
forgot = ctk.CTk()
forgot.title("Purple Album — ลืมรหัสผ่าน")
forgot.geometry("900x600+3500")      
forgot.minsize(800, 520)
forgot.configure(fg_color=BG_SOFT)

# คอนเทนเนอร์
container = ctk.CTkFrame(forgot, corner_radius=20, fg_color="#F7F5FF")
container.pack(fill="both", expand=True, padx=24, pady=24)


# รูปโลโก้ (ใช้ raw string ป้องกัน \P)
logo_img = ctk.CTkImage(
    light_image=Image.open(r"C:\Python\project\LOGOproject.png"),
    dark_image=Image.open(r"C:\Python\project\LOGOproject.png"),
    size=(100, 100)
)
logo_label = ctk.CTkLabel(container, image=logo_img, text="")
logo_label.pack(pady=(8,6))

# หัวข้อ
title = ctk.CTkLabel(
    container, text="ลืมรหัสผ่าน",
    font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
    text_color=PURPLE_PRIMARY
)
title.pack(pady=4)

form = ctk.CTkFrame(container, fg_color="transparent")
form.pack(padx=28, pady=5, fill="x")

forgot.mainloop()