import customtkinter
import app.Operation.FileOperationClass as FileOP
from datetime import datetime


class Main(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.now = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        # self.path = FileOP.readFile("scan")
        # create browse button
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self)
        self.textbox.grid(row=0, column=0, padx=10,
                          pady=10, sticky="nsew")
        self.textbox.insert(customtkinter.END, self.now+"\n")

        self.button = customtkinter.CTkButton(
            self, text="Clear", command=self.clear, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.button.grid(row=1, column=0, padx=10,
                         pady=10, sticky="e")

    def clear(self):
        self.textbox.delete("1.0", customtkinter.END)

    def add_log(self, log="~"):
        data = f"{datetime.now().strftime('%H:%M:%S')} : {log} \n"
        self.textbox.insert(customtkinter.END, data)
        self.save_log(data)

    def save_log(self, data):
        FileOP.writeFile(
            f"data/log/log_{self.now}.log", data, "a")
