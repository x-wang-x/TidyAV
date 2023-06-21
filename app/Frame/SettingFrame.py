import customtkinter
import os
from tkinter import filedialog as fd
import app.Operation.FileOperationClass as FileOP
from . import BoxFrame
from . import DatabaseFrame


class Display(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        my_font = customtkinter.CTkFont(weight="bold", size=15)
        self.label = customtkinter.CTkLabel(
            self, text="Setting", fg_color=("lightgrey", "#242424"), corner_radius=10, font=my_font)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self, values=["System", "Dark", "Light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(
            row=1, column=0, padx=10, pady=10)
        self.masterBtn = customtkinter.CTkButton(self, text="Master Folder",
                                                 command=self.masterBtn, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.masterBtn.grid(row=2, column=0, padx=10, pady=10)

        self.databaseBtn = customtkinter.CTkButton(self, text="Database",
                                                   command=self.databaseBtn, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.databaseBtn.grid(row=3, column=0, padx=10, pady=10)
        self.db_windows = None

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def addLog(self, log):
        self.master.log.add_log(log)

    def masterBtn(self):
        # Open folder dialog
        path = fd.askdirectory()
        if (os.path.isdir(path)):
            FileOP.writeConfig("master", path)
            self.addLog(f"Master folder has been set to {path}")
            BoxFrame.show("Success", "Master folder has been set")
        else:
            self.addLog(f"Invalid folder path {path}")
            BoxFrame.show("Error", "Invalid folder path")

    def databaseBtn(self):
        self.master.withdraw()
        if self.db_windows is None or not self.db_windows.winfo_exists():
            # create window if its None or destroyed
            self.db_windows = DatabaseFrame.Main(self)
            self.db_windows.focus()  # focus on window
        else:
            self.db_windows.focus()  # if window exists focus it

        self.db_windows.wait_window()  # wait for window to be destroyed
        self.db_windows.destroy
        self.master.deiconify()
