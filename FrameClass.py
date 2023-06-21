import os
import json
from tkinter import filedialog as fd
from tkinter import messagebox
import time
import re
from DataClass import LoadData as LoadData
import customtkinter
import FileOperationClass as FileOP


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


class ScanSceneFrame(customtkinter.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.list = []
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.progress_bar = customtkinter.CTkProgressBar(
            self, orientation="horizontal")
        self.progress_bar.grid(
            row=1, column=3, padx=10, pady=10, sticky="w")
        self.progress_bar.set(0)

        self.button = customtkinter.CTkButton(
            self, text="Start Scan", command=self.Scan, height=10)
        self.button.grid(row=0, column=0, padx=10,
                         pady=10, sticky="nsew", rowspan=2)

        self.percentage_txt = customtkinter.CTkLabel(
            self, text="0%")
        self.percentage_txt.grid(
            row=1, column=2, padx=10, pady=10, sticky="w")

        self.folder_txt = customtkinter.CTkLabel(
            self, text="Current working on : -")
        self.folder_txt.grid(row=0, column=2, padx=10,
                             pady=10, sticky="w", columnspan=2)

        self.isRecursiveSwitchVar = customtkinter.StringVar(value="off")
        self.isRecursiveSwitch = customtkinter.CTkSwitch(self, text="Recursive Search",
                                                         variable=self.isRecursiveSwitchVar, onvalue="on", offvalue="off")
        self.isRecursiveSwitch.grid(
            row=2, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)

    def Scan(self):
        self.list = []
        FileOP.deleteFile("d_list")
        path = FileOP.readConfig("scan")
        msg_box = BoxFrame.question(
            "Confirmation", f"Scan all files in folder {path}?")
        if msg_box == 'yes':
            if (path != None and os.path.isdir(path)):
                if self.isRecursiveSwitchVar.get() == "on":
                    print("Rec")
                    FileOP.ScanFile(path, True, self.Update,
                                    self.Add)
                else:
                    FileOP.ScanFile(path, False, self.Update,
                                    self.Add)
                self.folder_txt.configure(text="Trying to detect AV Movies...")
                self.update_idletasks()
                time.sleep(0.5)
                self.Detector()
                time.sleep(0.5)
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
        folder = f"{folder[:15]}..."
        self.folder_txt.configure(text="Working on : "+folder)
        # the maximum value of progress bar is 1 so divide to maximum range
        iter_step = 0
        if range != 0:
            iter_step = 1/range

        # calculate progress step
        progress_step = idx * iter_step
        # calculate percentage
        percent = progress_step*100
        self.percentage_txt.configure(text=f"{int(percent)}%")
        # update progress bar each 10%
        if (int(percent) % 10 == 0):
            self.progress_bar.set(progress_step)
            self.update_idletasks()
        # set progress bar to max to 100%
        if (int(percent) >= 100):
            self.progress_bar.set(100)
            self.update_idletasks()

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


class DataFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, edit=None, delete=None, **kwargs):
        super().__init__(master, **kwargs)

        self.edit = edit
        self.delete = delete
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []
        self.items = []

    def edit_item(self, id, item):
        # loop the data then search by id, if found then update by id
        for d in self.items:
            if int(d.get("ID")) == id:
                d.update(item)

                # info
                print(f"Editing ( ID : {self.searchBy(id)} ) to {item}")

                self.update_list(self.searchBy(id), item)
                return

    def update_list(self, id, item):
        try:
            for x, y in zip(self.label_list[id], item.values()):
                x.configure(text=y)
        except Exception as e:
            # info
            print(e)

    def add_item(self, item, image=None):

        code = item.get("Code")
        id = item.get("ID")
        studio = item.get("Studio_Name")
        amateur = item.get("Amateur")

        label = customtkinter.CTkLabel(
            self, text=id, image=image, compound="left", padx=5, anchor="w")
        label2 = customtkinter.CTkLabel(
            self, text=code, image=image, compound="left", padx=5, anchor="w")
        label3 = customtkinter.CTkLabel(
            self, text=studio, image=image, compound="left", padx=5, anchor="w")
        label4 = customtkinter.CTkLabel(
            self, text=amateur, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(
            self, text="update", fg_color="green")
        button2 = customtkinter.CTkButton(
            self, text="delete", fg_color="red")
        if self.edit is not None and self.edit is not None:
            button.configure(command=lambda: self.edit(item))
            button2.configure(command=lambda: self.delete(item))
        label.grid(row=len(self.label_list),
                   column=0, pady=(0, 10), sticky="w")
        label2.grid(row=len(self.label_list),
                    column=1, pady=(0, 10), sticky="w")
        label3.grid(row=len(self.label_list),
                    column=2, pady=(0, 10), sticky="w")
        label4.grid(row=len(self.label_list),
                    column=3, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list),
                    column=4, pady=(0, 10), padx=5)
        button2.grid(row=len(self.button_list),
                     column=5, pady=(0, 10), padx=5)

        self.label_list.append([label, label2, label3, label4])
        self.button_list.append([button, button2])
        self.items.append(item)

    def searchBy(self, id):
        idx = 0
        for labels in self.label_list:
            if (int(labels[0].cget("text")) == id):
                return int(idx)
            idx += 1
        return None

    def delete_list(self, id):
        for x in self.label_list[id]:
            x.destroy()
        for y in self.button_list[id]:
            y.destroy()
        self.label_list.pop(id)
        self.button_list.pop(id)
        self.items.pop(id)

    def get_all(self):
        return self.label_list, self.button_list, self.items

    def get(self, id):
        return self.label_list[id], self.button_list[id], self.items[id]

    def last_item(self):
        if len(self.items) == 0:
            return {}
        return self.items[-1]

    def clear(self):
        for labels in self.label_list:
            for label in labels:
                label.destroy()
        for buttons in self.button_list:
            for button in buttons:
                button.destroy()
        self.label_list = []
        self.button_list = []
        self.items = []
        self.update_idletasks()


class Database(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.maker_db = 'data/d_maker.csv'
        self.maker_db = 'data/d_mov.csv'

        # # create center window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        screen_height = self.winfo_screenheight()
        screen_width = self.winfo_screenwidth()

        widget_height = 720
        widget_width = 1080

        pos_height = int(screen_height // 2 - widget_height // 2)
        pos_width = int(screen_width // 2 - widget_width // 2)

        self.geometry(
            f"{widget_width}x{widget_height}+{pos_width}+{pos_height}")
        self.wm_iconbitmap("icon.ico")
        self.title("Database")

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, pady=10)
        self.tabview.add("Maker")
        self.tabview.add("All Movies")
        self.tabview.tab("Maker").grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.tabview.tab("Maker").grid_rowconfigure((0, 1, 2), weight=1)

        self.id = customtkinter.CTkEntry(self.tabview.tab(
            "Maker"), placeholder_text="Id")
        self.id.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        self.id.bind("<KeyRelease>", self.id_event)

        self.code = customtkinter.CTkEntry(self.tabview.tab(
            "Maker"), placeholder_text="Code")
        self.code.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")

        self.studio = customtkinter.CTkEntry(self.tabview.tab(
            "Maker"), placeholder_text="Studio")
        self.studio.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")

        self.amateur = customtkinter.CTkOptionMenu(
            self.tabview.tab(
                "Maker"), values=["Yes", "No", "Unknown"])
        self.amateur.set("Unknown")
        self.amateur.grid(row=0, column=3, pady=5, padx=5, sticky="nsew")

        self.button = customtkinter.CTkButton(
            self.tabview.tab(
                "Maker"), text="Add", command=self.button_event)
        self.button.grid(row=0, column=4, pady=5, padx=5, sticky="nsew")

        self.makerDB = DataFrame(
            self.tabview.tab("Maker"), width=widget_width-(widget_width*0.1), height=widget_height-(widget_height*0.25), corner_radius=0, fg_color="transparent", edit=self.makerBtn, delete=self.delBtn_event)
        self.makerDB.grid(row=1, column=0, padx=10, pady=10, columnspan=5)

        self.moviesDB = DataFrame(
            self.tabview.tab("All Movies"), width=widget_width-(widget_width*0.1), height=widget_height-(widget_height*0.25), corner_radius=0, fg_color="transparent")
        self.moviesDB.grid(
            row=1, column=0, padx=10, pady=10)

        self.applyBtn = customtkinter.CTkButton(
            self.tabview.tab("Maker"), text="Apply", command=self.applyBtn_event)
        self.applyBtn.grid(row=2, column=0, pady=0, padx=0, sticky="nsew")

        self.after(500, self.load)  # load data after 500ms

    def applyBtn_event(self):
        self.save(self.makerDB.get_all()[-1])
        self.load()

    # when id input is changed
    def id_event(self, event):
        id = self.id.get()
        try:
            id = int(id)
            if self.isId(id):
                self.input(self.makerDB.get(id-1)[-1])
                self.button.configure(text="Update")
            else:
                self.button.configure(text="Add")
        except:
            # info
            print("Input number only")

    def newID(self):
        id = self.makerDB.last_item().get("ID")
        if id is None:
            id = 0
        return int(id)+1

    def clear_entry(self):

        self.id.configure(state="normal")
        id = self.newID()
        self.id.delete(0, "end")
        self.id.insert(0, int(id))
        self.code.delete(0, "end")
        self.studio.delete(0, "end")
        self.amateur.set("Unknown")
        self.button.configure(text="Add")
        self.id.configure(state="disabled")

    def sort(self, data, key):
        data.sort(key=lambda x: x.get(key))
        return data

    def save(self, datas):
        # info
        print(f"Saving : (  {self.maker_db} )")
        field = ["ID", "Code", "Studio_Name", "Amateur"]
        FileOP.write_csv(self.maker_db, field, datas)

    def load(self):
        # clear all list
        self.makerDB.clear()
        # set default id
        self.id.delete(0, "end")
        self.id.insert(0, "1")

        # read data from file
        datas = FileOP.read_csv(self.maker_db)
        if datas != None:
            datas = self.sort(datas, "Code")
            for i, x in enumerate(datas):
                if x.get("ID") is not None or "":
                    x.update({"ID": i+1})
                    self.makerDB.add_item(x)
            self.clear_entry()
        else:
            print("No Data")

    def isId(self, id):
        x = self.makerDB.get_all()[2]
        for i in x:
            if int(i.get("ID")) == int(id):
                return True
        return False

    def add(self, datas):
        self.makerDB.add_item(datas)

    def edit(self, datas):
        id = int(self.id.get())
        self.makerDB.edit_item(id, datas)

    def button_event(self):
        datas = {"ID": self.id.get(), "Code": self.code.get(),
                 "Studio_Name": self.studio.get(), "Amateur": self.amateur.get()}

        if self.isId(self.id.get()):
            self.edit(datas)
            self.clear_entry()
            return

        # info
        print(f"Add : (  {datas} )")

        self.add(datas)
        self.clear_entry()

    def input(self, item):
        self.id.configure(state="normal")
        self.id.delete(0, "end")
        self.id.insert(0, item.get("ID"))
        self.id.configure(state="disabled")

        self.code.delete(0, "end")
        self.code.insert(0, item.get("Code"))

        if (item.get("Studio_Name") != ""):
            self.studio.delete(0, "end")
            self.studio.insert(0, item.get("Studio_Name"))
        else:
            self.studio.delete(0, "end")
            self.studio.insert(0, "Unknown")

        self.amateur.set(item.get("Amateur"))

    def makerBtn(self, item):
        self.input(item)
        self.button.configure(text="Update")

    def delBtn_event(self, item):
        # info
        print(f"Delete : (  {item} )")
        self.makerDB.delete_list(self.makerDB.searchBy(int(item.get("ID"))))
        self.clear_entry()


class SettingFrame(customtkinter.CTkFrame):
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

    def masterBtn(self):
        # FileOP.writeConfig("master", dialog.get_input())
        # Open folder dialog
        path = fd.askdirectory()
        if (os.path.isdir(path)):
            FileOP.writeConfig("master", path)
            BoxFrame.show("Success", "Master folder has been set")
        else:
            BoxFrame.show("Error", "Invalid folder path")

    def databaseBtn(self):
        self.master.withdraw()
        if self.db_windows is None or not self.db_windows.winfo_exists():
            # create window if its None or destroyed
            self.db_windows = Database(self)
            self.db_windows.focus()  # focus on window
        else:
            self.db_windows.focus()  # if window exists focus it

        self.db_windows.wait_window()  # wait for window to be destroyed
        self.db_windows.destroy
        self.master.deiconify()


class ListFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((1), weight=1)
        # create select all checkbox
        self.check_var = customtkinter.StringVar(value="off")
        self.checkbox = customtkinter.CTkCheckBox(self, text="Select All", command=self.checkbox_event,
                                                  variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        # create scrollable checkbox frame
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(
            self, width=350, height=250, command=self.checkbox_frame_event)
        self.scrollable_checkbox_frame.grid(
            row=1, column=0, padx=15, pady=0, sticky="nsew", columnspan=3)
        # create rename button
        self.renameBtn = customtkinter.CTkButton(
            self, text="Rename", command=self.rename, state="disabled", fg_color="#242424")
        self.renameBtn.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        # create move button
        self.moveBtn = customtkinter.CTkButton(
            self, text="Spread", command=self.move, state="disabled", fg_color="#242424")
        self.moveBtn.grid(row=0, column=2, padx=15, pady=15, sticky="w")
        # create total text
        self.total_text = customtkinter.CTkLabel(
            self, text="Found : 0 , Changed : 0")
        self.total_text.grid(row=2, column=0, padx=15,
                             pady=15, sticky="w")
        # create apply button
        self.applyBtn = customtkinter.CTkButton(
            self, text="Apply", command=self.apply, state="disabled", fg_color="#242424")
        self.applyBtn.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        # create revert button
        self.revertBtn = customtkinter.CTkButton(
            self, text="Revert", command=self.revert, state="disabled", fg_color="#242424")
        self.revertBtn.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    def revert(self):
        # load from original list
        self.Load()
        # disable revert after click
        self.revertBtn.configure(state="disabled")

    def rename(self):
        self.disableBtn(True)
        leak_worlist = ['leak', 'leaked']
        demosaic_wordlist = ['demosaic', 'demosaiced',
                             'decensored', 'decensor', 'mosaic', 'remove', 'removed']
        subbed_worldlist = ['subbed', 'sub', 'subtitle', 'english']
        try:
            for x in self.scrollable_checkbox_frame.get_checked_items():
                # head for dir and tail for filename
                head, tail = os.path.split(x)
                # lower case for easy compare
                tail = tail.lower()
                code = FileOP.Detector(tail)
                if code is not None:
                    compare = re.search(
                        r"\b({}.\d+)".format(code), tail, re.IGNORECASE)  # parse to code
                    # return filename only from regex
                    filename = tail
                    if compare != None:
                        # to make filename only and uppercase it
                        filename = str(compare.group()).upper()

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
        self.UpdateTotal()
        self.disableBtn(False)

    def dataChanged(self):
        # get all items from list
        _from = LoadData().get_names()
        # changes items from list
        _to = self.scrollable_checkbox_frame.get_all_items()
        _do = []
        for x in range(len(_from)):
            # if something changed
            if _from[x] != _to[x]:
                _do.append([_from[x], _to[x]])
        return _do

    def apply(self):
        total_changes = len(self.dataChanged())
        if (total_changes != 0):
            # show confirmation dialog
            msg_box = BoxFrame.question(
                "Confirmation", f"Apply changes to {total_changes} item(s) ? (Can't be undone)")
            if msg_box == 'yes':
                _do = self.dataChanged()
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
        self.disableBtn(True)
        master_dir = FileOP.readConfig("master")
        _do = []
        try:
            for x in self.scrollable_checkbox_frame.get_checked_items():
                for code in LoadData().get_codes():
                    compare = re.search(
                        r"\b({}.\d+)".format(code), x, re.IGNORECASE)
                    if compare != None:
                        _do.append([x, code, compare.group()])
                        continue

            for x in _do:
                # head for dir and tail for filename
                head, tail = os.path.split(x[0])
                new_path = os.path.normpath(
                    master_dir+"/"+x[1]+"/"+x[2]+"/"+tail)
                self.scrollable_checkbox_frame.edit_item(
                    x[0], new_path)
                self.update_idletasks()
        except Exception as e:
            BoxFrame.error("Error", f"Failed to move file(s) \n {e}")
        self.UpdateTotal()
        self.disableBtn(False)

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
        if (len(self.dataChanged()) == 0):
            self.revertBtn.configure(state="disabled")
        else:
            self.revertBtn.configure(state="normal")
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
        datas = LoadData().get_names()
        for x in datas:
            self.scrollable_checkbox_frame.add_item(x)
        self.UpdateTotal()

    def UpdateTotal(self):
        self.found = len(self.scrollable_checkbox_frame.get_all_items())
        self.changed = len(self.dataChanged())
        self.total_text.configure(
            text=f"Found : {self.found} , Changed : {self.changed}")
