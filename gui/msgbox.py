import ctypes

def ask_yes_no(title: str, message: str) -> bool:
    style  = 4 | 64 | 65536
    return ctypes.windll.user32.MessageBoxW(0, message, title, style)==6

def show_message(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0)