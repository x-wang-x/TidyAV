from tkinter import messagebox


def show(type, message_txt):
    return messagebox.showinfo(type, message_txt)


def error(type, message_txt):
    return messagebox.showerror(type, message_txt)


def question(type, message_txt):
    return messagebox.askquestion(type, message_txt)


def warning(type, message_txt):
    return messagebox.showwarning(type, message_txt)
