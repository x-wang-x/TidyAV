import customtkinter
import app.Operation.FileOperationClass as FileOP
from datetime import datetime


class Main(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        now = f"Log : {datetime.now()} \n"
        # self.path = FileOP.readFile("scan")
        # create browse button
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.grid(row=0, column=0, padx=10,
                          pady=10, sticky="nsew")
        self.textbox.insert(customtkinter.END, now)

        self.button = customtkinter.CTkButton(
            self, text="Clear", command=self.add_log, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.button.grid(row=1, column=0, padx=10,
                         pady=10, sticky="e")

    def clear(self):
        self.textbox.delete("1.0", customtkinter.END)

    def add_log(self, log="~"):
        self.textbox.insert(customtkinter.END, f"{datetime.now()} : {log}\n")
