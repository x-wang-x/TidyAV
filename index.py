import tkinter
import customtkinter
from tkinter import filedialog as fd
from tkinter import messagebox
import os
import time
import json
import re
import shutil


class FileOP:
    def OpenFolder():
        return fd.askdirectory()

    def writeFile(file, data):
        try:
            with open(file, 'w') as f:
                f.write(data)
        except Exception as e:
            print('Error writing file : ', e)

    def readFile(file):
        if not os.path.isfile(file):
            return []
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print('Error reading file : ', e)

    def deleteFile(file):
        if not os.path.isfile(file):
            return
        try:
            os.remove(file)
        except Exception as e:
            print('Error deleting file : ', e)

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

    def Detector(file):
        studio = FileOP.readFile('d_maker_list')
        for i in studio:
            # regex to parse code from file name
            compare = re.search(
                r"\b({}.\d*)\b".format(i[1]), file, re.IGNORECASE)
            if compare:
                # append valid files to array:
                return i[1]
            # print(i[1])
        return None

    def Mover(_from, _to):
        # Create dir if not exist
        if not os.path.exists(os.path.dirname(_to)):
            try:
                os.makedirs(os.path.dirname(_to), exist_ok=True)
            except Exception as error:
                print(error)
        try:
            shutil.move(_from, _to)  # moving
            # os.rename(from_, to_) #do rename / move (only in same disk)
        except Exception as e:
            print(e)


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


class ScrollableCheckBoxFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.checkbox_list = []

    def add_item(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        if self.command is not None:
            checkbox.configure(command=self.command)
        checkbox.grid(row=len(self.checkbox_list),
                      column=0, pady=(0, 10), sticky="w")
        self.checkbox_list.append(checkbox)

    def remove_item(self, item):
        for checkbox in self.checkbox_list:
            if item == checkbox.cget("text"):
                checkbox.destroy()
                self.checkbox_list.remove(checkbox)
                return

    def edit_item(self, item, new_item):
        for checkbox in self.checkbox_list:
            if item == checkbox.cget("text"):
                checkbox.configure(text=new_item)
                return

    def select_all(self):
        for checkbox in self.checkbox_list:
            checkbox.select()

    def deselect_all(self):
        for checkbox in self.checkbox_list:
            checkbox.deselect()

    def clear(self):
        for checkbox in self.checkbox_list:
            checkbox.destroy()
        self.checkbox_list = []

    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]

    def get_all_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list]


class BoxFrame():

    def show(type, message_txt):
        return messagebox.showinfo(type, message_txt)

    def error(type, message_txt):
        return messagebox.showerror(type, message_txt)

    def question(type, message_txt):
        return messagebox.askquestion(type, message_txt)

    def warning(type, message_txt):
        return messagebox.showwarning(type, message_txt)


class ListFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        # create select all checkbox
        self.check_var = customtkinter.StringVar(value="off")
        self.checkbox = customtkinter.CTkCheckBox(self, text="Select All", command=self.checkbox_event,
                                                  variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        # create scrollable checkbox frame
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(
            self, width=350, height=400, command=self.checkbox_frame_event)
        self.scrollable_checkbox_frame.grid(
            row=1, column=0, padx=15, pady=0, sticky="nsew", columnspan=3)
        # create rename button
        self.renameBtn = customtkinter.CTkButton(
            self, text="Rename", command=self.rename, state="disabled")
        self.renameBtn.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        # create move button
        self.moveBtn = customtkinter.CTkButton(
            self, text="Move", command=self.move, state="disabled")
        self.moveBtn.grid(row=0, column=2, padx=15, pady=15, sticky="w")
        # create apply button
        self.applyBtn = customtkinter.CTkButton(
            self, text="Apply", command=self.apply, state="disabled")
        self.applyBtn.grid(row=2, column=2, padx=15, pady=15, sticky="w")

    def rename(self):
        self.disableBtn(True)
        leak_worlist = ['Leak', 'Leaked']
        demosaic_wordlist = ['Demosaic', 'Demosaiced',
                             'Decensored', 'Decensor', 'Mosaic', 'Remove', 'Removed']
        subbed_worldlist = ['Subbed', 'Sub', 'Subtitle', 'Subtitle', 'English']
        try:
            for x in self.scrollable_checkbox_frame.get_checked_items():
                # head for dir and tail for filename
                head, tail = os.path.split(x)
                code = FileOP.Detector(tail)
                if code is not None:
                    compare = re.search(
                        r"\b({}.\d+)".format(code), tail, re.IGNORECASE)  # parse to code
                    # return filename only from regex
                    filename = tail
                    if compare != None:
                        filename = str(compare.group())
                    ext = os.path.splitext(x)[1]
                    # check if file have another tag
                    # part tag
                    parted = re.search(r"part.(\d)|part(\d)",
                                       tail, re.IGNORECASE)
                    if (parted != None):
                        part = str(parted.group())
                        part = re.search(r"\d+", part)
                        part = "[Part "+str(part.group())+"]"
                    else:
                        part = ""

                    # leaked tag
                    if any(ele in tail for ele in leak_worlist):
                        leaked = '[Leaked]'
                    elif any(ele in tail for ele in demosaic_wordlist):
                        leaked = '[Decensored]'
                    else:
                        leaked = ''
                    # subbed tag
                    if any(ele in tail for ele in subbed_worldlist):
                        subbed = "[Subbed]"
                    else:
                        subbed = ''
                    ori_path = os.path.normpath(x)
                    new_path = os.path.normpath(
                        head+"/["+filename+']'+part+leaked+subbed+ext)
                    # print([ori_path, new_path])
                    self.scrollable_checkbox_frame.edit_item(
                        x, new_path)
                    self.update_idletasks()

        except Exception as e:
            print(e)
        self.disableBtn(False)

    def apply(self):

        # get all items from list
        _from = LoadData().get()
        # changes items from list
        _to = self.scrollable_checkbox_frame.get_all_items()
        _do = []
        for x in range(len(_from)):
            # if something changed
            if _from[x] != _to[x]:
                _do.append([_from[x], _to[x]])
        # clear list box
        total_changes = len(_do)
        if (total_changes != 0):
            # show confirmation dialog
            msg_box = BoxFrame.question(
                "Confirmation", f"Apply changes to {total_changes} item(s) ? (Can't be undone)")
            if msg_box == 'yes':
                for x in range(total_changes):
                    FileOP.Mover(_do[x][0], _do[x][1])
                time.sleep(0.5)
                BoxFrame.show("Success", "Changes applied")
                # clear list box
                self.disableBtn(True)
                self.scrollable_checkbox_frame.clear()

        else:
            BoxFrame.warning("Warning", "No changes detected")

    def move(self):
        pass

    def checkbox_event(self):
        # check if select all is checked, if so select all items
        if (self.check_var.get() == "on"):
            self.scrollable_checkbox_frame.select_all()
            # check if list is empty, if so disable buttons
            if (len(self.scrollable_checkbox_frame.get_checked_items()) == 0):
                self.disableBtn(True)
                return
            self.disableBtn(False)
        # check if select all is unchecked, if so deselect all items
        else:
            self.scrollable_checkbox_frame.deselect_all()
            self.disableBtn(True)

    def disableBtn(self, btn):
        # disable buttons if True, enable if False
        if btn:
            self.renameBtn.configure(state="disabled")
            self.moveBtn.configure(state="disabled")
            self.applyBtn.configure(state="disabled")
        else:
            self.renameBtn.configure(state="normal")
            self.moveBtn.configure(state="normal")
            self.applyBtn.configure(state="normal")

    def checkbox_frame_event(self):
        # check if list is empty, if so disable buttons and deselect select all checkbox
        if (len(self.scrollable_checkbox_frame.get_checked_items()) == 0):
            self.checkbox.deselect()
            self.disableBtn(True)
        else:
            self.disableBtn(False)

    def clear(self):
        self.scrollable_checkbox_frame.clear()

    def Load(self):
        self.clear()
        for x in LoadData().get():
            self.scrollable_checkbox_frame.add_item(x)


class LoadData():
    def __init__(self):
        self.data = []
        for i in FileOP.readFile("d_list"):
            self.data.append(i[1])

    def add(self, item):
        self.data.append(item)

    def get(self):
        return self.data

    def clear(self):
        self.data = []

    def remove(self, item):
        self.data.remove(item)


class ScanSceneFrame(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.list = []

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

    def Scan(self):
        self.list = []
        FileOP.deleteFile("d_list")
        path = FileOP.readConfig("scan")
        msg_box = BoxFrame.question(
            "Confirmation", f"Scan all files in folder {path}?")
        if msg_box == 'yes':
            if (path != None and os.path.isdir(path)):
                FileOP.ScanFile(path, False, self.Update,
                                self.Add)
                self.folder_txt.configure(text="Trying to detect AV Movies...")
                self.update_idletasks()
                time.sleep(1)
                self.Detector()
                self.folder_txt.configure(text="Done.")
                self.master.listx.Load()
            else:
                BoxFrame.error("Error", "Invalid path")
                return

    def Detector(self):
        self.result = []
        item = FileOP.readFile("d_list")
        for x in item:
            code = FileOP.Detector(x)
            if code != None:
                self.result.append([code, x])
        FileOP.writeFile('d_list', json.dumps(self.result))

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
        self.list.append(value)
        FileOP.writeFile('d_list', json.dumps(self.list))


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
        # self.grid_rowconfigure(1, weight=1)

        self.browse_frame = BrowseFrame(self)
        self.browse_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsw")

        self.scanScene = ScanSceneFrame(self)
        self.scanScene.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsw")

        self.listx = ListFrame(self)
        self.listx.grid(
            row=2, column=0, padx=10, pady=10, sticky="nsw")


app = App()
app.mainloop()
