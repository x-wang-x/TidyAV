import tkinter
import customtkinter
from tkinter import filedialog as fd
from tkinter import messagebox
import os
import time
import json


class FileOP:
    def OpenFolder():
        return fd.askdirectory()

    def readConfig(key):
        try:
            with open('config.txt') as f:
                config = json.load(f)
                return config[key]
        except:
            print(f'Something wrong with config.txt {key}')
            return None

    def writeConfig(key, value):
        try:
            config = {key: value}
            with open('config.txt', 'w') as f:
                json.dump(config, f)
        except:
            print('Error writing config.txt')

    def ScanFile(dir, recursive, updateFunc, addListFunc):
        types = ('.mp4', '.mkv', '.ts', '.avi')
        idx = 0
        if recursive:
            for r, d, f in os.walk(dir):
                idx = 0
                time.sleep(0.5)
                for file in f:
                    idx += 1
                    # send Update Progress Callback
                    updateFunc(len(f), idx, folder=r)
                    for ext in types:
                        if ext in file:
                            # normalize to path and write to res
                            res = os.path.normpath(os.path.join(r, file))
                            addListFunc(res)
        else:
            lis = os.listdir(dir)
            for file in lis:
                idx += 1
                # send Update Progress Callback
                updateFunc(len(lis), idx, folder=dir)
                if os.path.isfile(os.path.join(dir, file)):
                    for ext in types:
                        if file.endswith(ext):
                            # normalize to path and write to res
                            res = os.path.normpath(os.path.join(dir, file))
                            addListFunc(res)

        updateFunc(0, 0, "Done")


class ProgressBar(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.progress = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
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
            self, text="V", width=100, height=24)
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
            self, text="Start Scan", command=self.Scan)
        self.button.grid(row=0, column=2, padx=10,
                         pady=10, sticky="w")

        self.percentage_txt = customtkinter.CTkLabel(
            self, text="0%", fg_color="transparent")
        self.percentage_txt.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.folder_txt = customtkinter.CTkLabel(
            self, text="Current working on : -", fg_color="transparent", wraplength=200)
        self.folder_txt.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.scrollable_label_button_frame = ScrollableLabelButtonFrame(
            master=self, width=300, command=self.label_button_frame_event, corner_radius=0)
        self.scrollable_label_button_frame.grid(
            row=2, column=0, padx=0, pady=0, sticky="nsew")

    def Scan(self):
        path = FileOP.readConfig("scan")
        msg_box = messagebox.askquestion('Scan folder', f'Start scanning {path} ?',
                                         icon='warning')
        if msg_box == 'yes':
            self.scrollable_label_button_frame.clear()
            if (path != None and os.path.isdir(path)):
                FileOP.ScanFile(path, True, self.Update,
                                self.Add)
            else:
                messagebox.showerror("Error", "Path not valid")

    def Update(self, range, idx, folder):
        # update folder text
        self.folder_txt.configure(text="Current working on : "+folder)
        # the maximum value of progress bar is 1 so divide to maximum range
        iter_step = 0
        if range != 0:
            iter_step = 1/range

        # calculate progress step
        progress_step = idx * iter_step
        # calculate percentage
        percent = progress_step*100
        self.percentage_txt.configure(text=str(int(percent))+"%")
        # update progress bar each 15%
        if (int(percent) % 15 == 0):
            self.progress_bar.set(progress_step)
            self.update_idletasks()
        # set progress bar to max to 100%
        if (int(percent) >= 100):
            self.progress_bar.set(100)
            self.update_idletasks()
            progress_step = 0

    def Add(self, value):
        self.scrollable_label_button_frame.add_item(value)

    def label_button_frame_event(self, item):
        print(f"label button frame clicked: {item}")


class BrowseFrame(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.path = FileOP.readConfig("scan")
        # create entry box
        self.box = customtkinter.CTkEntry(self, placeholder_text=self.path)
        self.box.grid(row=0, column=0, padx=10,
                      pady=10, sticky="w")
        # create browse button
        self.button = customtkinter.CTkButton(
            self, text="Browse", command=self.find)
        self.button.grid(row=0, column=1, padx=10,
                         pady=10, sticky="w")

    def find(self):
        # Open folder dialog
        path = FileOP.OpenFolder()
        # Delete entry from 0 to end
        self.box.delete(0, "end")
        # Insert path to entry
        self.box.insert(0, path)
        # Write path to config file
        FileOP.writeConfig("scan", self.box.get())


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("my app")
        self.geometry("1280x720")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.browse_frame = BrowseFrame(self)
        self.browse_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.a = ScanSceneFrame(self)
        self.a.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsw")

        # self.scrollable_label_button_frame = ScrollableLabelButtonFrame(self)
        # self.scrollable_label_button_frame.grid(
        #     row=3, column=0, padx=10, pady=10, sticky="nsw")

        # # create scrollable label and button frame
        # current_dir = os.path.dirname(os.path.abspath(__file__))


app = App()
app.mainloop()
