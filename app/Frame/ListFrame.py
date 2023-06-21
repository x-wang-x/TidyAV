import os
import customtkinter
import app.Operation.FileOperationClass as FileOP
from . import BoxFrame
import re
import time


class Display(customtkinter.CTkFrame):
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
        self.scrollable_checkbox_frame = ScrollFrame(
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

    def addLog(self, log):
        self.master.log.add_log(log)

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
                idx = 0
                for x in range(total_changes):
                    idx += 1
                    self.master.scanScene.folder_txt.configure(
                        text="Moving {} of {}".format(idx, total_changes))
                    self.update()
                    self.addLog(
                        f"Moving {_do[x][0]} to {_do[x][1]}")
                    FileOP.Mover2(_do[x][0], _do[x][1],
                                  callback=self.callbackMove)
                time.sleep(0.5)
                self.master.scanScene.folder_txt.configure(
                    text="Done")
                BoxFrame.show("Success", "Changes applied")
                # clear list box
                self.disableBtn(True)
                self.scrollable_checkbox_frame.clear()

        else:
            BoxFrame.warning("Warning", "No changes detected")

    def callbackMove(self, added=100, total_added=100, full=100):
        percent = total_added / full * 100
        self.master.scanScene.progress_bar.set(percent/100)
        self.master.scanScene.percentage_txt.configure(text=f"{int(percent)}%")
        self.update_idletasks()

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


class ScrollFrame(customtkinter.CTkScrollableFrame):
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


class LoadData():
    def __init__(self):
        self.data = []
        for i in FileOP.readFile("d_list"):
            self.data.append(i)

    def add(self, item):
        self.data.append(item)

    def get(self):
        return self.data

    def get_names(self):
        return [x[1] for x in self.data]

    def get_codes(self):
        return [x[0] for x in self.data]

    def clear(self):
        self.data = []

    def remove(self, item):
        self.data.remove(item)
