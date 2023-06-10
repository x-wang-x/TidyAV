import tkinter
import customtkinter
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import os
import time


class ProgressBar(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.progress = customtkinter.CTkProgressBar(
            self, orientation="horizontal", progress_color='lime')
        self.progress.grid(row=0, column=0, padx=0,
                           pady=10, sticky="s")

    def set(self, value):
        self.progress.set(value)

    def get(self):
        return self.progress.get()


class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, image=None):
        label = customtkinter.CTkLabel(
            self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(
            self, text="Command", width=100, height=24)
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        label.grid(row=len(self.label_list),
                   column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return

    def clear(self):
        for label, button in zip(self.label_list, self.button_list):
            label.destroy()
            button.destroy()
        self.label_list = []
        self.button_list = []


class ScanSceneFrame(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.progress_bar = ProgressBar(self)
        self.progress_bar.grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        self.progress_bar.set(0)

        self.button = customtkinter.CTkButton(
            self, text="Start Scan", command=self.scanFile)
        self.button.grid(row=0, column=2, padx=10,
                         pady=10, sticky="w")

        self.scrollable_label_button_frame = ScrollableLabelButtonFrame(
            self, command=self.label_button_frame_event, corner_radius=0)
        self.scrollable_label_button_frame.grid(
            row=0, column=3, padx=10, pady=10, sticky="w")

        self.percentage_txt = customtkinter.CTkLabel(
            self, text="0%", fg_color="transparent")
        self.percentage_txt.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.folder_txt = customtkinter.CTkLabel(
            self, text="Current working on : -", fg_color="transparent", wraplength=200)
        self.folder_txt.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    def Update(self, range, idx):
        iter_step = 1/range
        progress_step = idx * iter_step
        percent = progress_step*100
        self.percentage_txt.configure(text=str(int(percent))+"%")
        if (int(percent) % 10 == 0):
            self.progress_bar.set(progress_step)
            self.update_idletasks()
        if (int(percent) >= 100):
            self.progress_bar.set(100)
            self.update_idletasks()
            progress_step = 0

    def scanFile(self, recursive=True):
        self.progress_bar.set(0)
        self.scanFiles = []
        self.scanDir = "F:\\Unsorted"
        self.scrollable_label_button_frame.clear()
        types = ('.mp4', '.mkv', '.ts', '.avi')  # movie format
        idx = 0
        if recursive:
            for r, d, f in os.walk(self.scanDir):
                self.folder_txt.configure(text=f'{r}')
                idx = 0
                for file in f:
                    idx += 1
                    self.Update(len(f), idx)
                    for ext in types:
                        if ext in file:
                            # normalize to path and write to files[]
                            res = os.path.normpath(os.path.join(r, file))
                            self.scanFiles.append(res)
                            self.scrollable_label_button_frame.add_item(res)

        else:
            lis = os.listdir(self.scanDir)
            self.folder_txt.configure(text=f'{self.scanDir}')
            for file in lis:
                idx += 1
                # self.UpdateProgress(len(lis), idx)
                self.Update(len(lis), idx)
                if os.path.isfile(os.path.join(self.scanDir, file)):
                    for ext in types:
                        if file.endswith(ext):
                            res = os.path.join(self.scanDir, file)
                            self.scanFiles.append(res)
                            self.scrollable_label_button_frame.add_item(res)
        # return self.scanFiles
        self.folder_txt.configure(text="Done")

    def label_button_frame_event(self, item):
        print(f"label button frame clicked: {item}")


class BrowseFrame(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        placeholder = "None"
        self.box = customtkinter.CTkEntry(self, placeholder_text=placeholder)
        self.box.grid(row=0, column=0, padx=10,
                      pady=10, sticky="w")
        self.button = customtkinter.CTkButton(
            self, text="Browse", command=self.find)
        self.button.grid(row=0, column=1, padx=10,
                         pady=10, sticky="w")

    def find(self):
        print('x')


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("my app")
        self.geometry("1280x720")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.browse_frame = BrowseFrame(self)
        self.browse_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.a = ScanSceneFrame(self)
        self.a.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsw")

        # # create scrollable label and button frame
        # current_dir = os.path.dirname(os.path.abspath(__file__))


app = App()
app.mainloop()
