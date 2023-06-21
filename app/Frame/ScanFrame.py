import customtkinter
import app.Operation.FileOperationClass as FileOP
import os
import json
from . import BoxFrame
import time
from . import LogFrame


class Display(customtkinter.CTkFrame):

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
                         pady=10, sticky="wns", rowspan=2)

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

    def addLog(self, log):
        self.master.log.add_log(log)

    def Scan(self):
        self.list = []
        FileOP.deleteFile("d_list")
        path = FileOP.readConfig("scan")
        msg_box = BoxFrame.question(
            "Confirmation", f"Scan all files in folder {path}?")
        if msg_box == 'yes':
            if (path != None and os.path.isdir(path)):
                if self.isRecursiveSwitchVar.get() == "on":
                    self.addLog("Start recursive scan path : "+path)
                    FileOP.ScanFile(path, True, self.Update,
                                    self.Add)
                else:
                    self.addLog("Start scan path : "+path)
                    FileOP.ScanFile(path, False, self.Update,
                                    self.Add)
                self.folder_txt.configure(text="Trying to detect AV Movies...")
                self.update_idletasks()

                self.addLog("Start detect AV Movies...")

                time.sleep(0.5)
                self.Detector()
                time.sleep(0.5)
                self.folder_txt.configure(text="Done.")

                self.master.listx.Load()

                self.addLog(
                    "Done. \n"+json.dumps(self.master.listx.scrollable_checkbox_frame.get_all_items()))
            else:
                self.addLog("Invalid path : "+path)
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
