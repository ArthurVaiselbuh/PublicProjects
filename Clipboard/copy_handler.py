# Copy handler
from tkinter import Tk, TclError

r = Tk()
r.withdraw()

def paste():
    try:
        return r.clipboard_get()
    except TclError:
        return ""

def copy(val):
    r.clipboard_clear()
    r.clipboard_append(val)