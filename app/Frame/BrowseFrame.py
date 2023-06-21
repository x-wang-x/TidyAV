import customtkinter
import app.Operation.FileOperationClass as FileOP
from tkinter import filedialog as fd


class Display(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.path = FileOP.readConfig("scan")
        # create entry box
        self.box = customtkinter.CTkEntry(self, placeholder_text=self.path)
        self.box.grid(row=0, column=0, padx=10,
                      pady=10, sticky="w")
        # create browse button
        self.button = customtkinter.CTkButton(
            self, text="Browse", command=self.find, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.button.grid(row=0, column=1, padx=10,
                         pady=10, sticky="w")

    def find(self):
        # Open folder dialog
        path = fd.askdirectory()
        # Delete entry from 0 to end
        self.box.delete(0, "end")
        # Insert path to entry
        self.box.insert(0, path)
        # Write path to config file
        FileOP.writeConfig("scan", self.box.get())
