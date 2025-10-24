import customtkinter as ctk
from tkinter import*
from tkinter import messagebox
from PIL import Image
import subprocess
import sys
import os,sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "Userdata.db")
DB_PATH = os.path.abspath(DB_PATH)

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


main.mainloop()

