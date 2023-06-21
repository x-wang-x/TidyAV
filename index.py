import customtkinter
import FileOperationClass as FileOP
from FrameClass import *


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("TidyAV")
        self.wm_iconbitmap("icon.ico")
        # create center window
        screen_height = self.winfo_screenheight()
        screen_width = self.winfo_screenwidth()

        widget_height = 720
        widget_width = 1080

        pos_height = int(screen_height // 2 - widget_height // 2)
        pos_width = int(screen_width // 2 - widget_width // 2)

        self.geometry(
            f"{widget_width}x{widget_height}+{pos_width}+{pos_height}")

        self.grid_columnconfigure((1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.btn = customtkinter.CTkButton(
            self, text="Setting", command=self.setting, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.masterVal = FileOP.readConfig("master")
        self.masterLabel = customtkinter.CTkLabel(
            self, text=self.masterVal, fg_color=("lightgrey", "#242424"))
        self.masterLabel.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.browse_frame = BrowseFrame(self)
        self.browse_frame.grid(
            row=2, column=1, padx=10, pady=10, sticky="nsw")

        self.scanScene = ScanSceneFrame(self)
        self.scanScene.grid(
            row=3, column=1, padx=10, pady=10, sticky="nsw")

        self.listx = ListFrame(self)
        self.listx.grid(
            row=4, column=1, padx=10, pady=10, sticky="nsw")

        self.setting_frame = SettingFrame(master=self)

    def setting(self):
        if self.setting_frame.grid_info() == {}:
            self.setting_frame.grid(row=1, column=0, padx=(10, 0),
                                    pady=10, sticky="nsw", rowspan=3)
        else:
            self.setting_frame.grid_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()

# def test():
#     fromx = r"C:\Users\fjriw\Videos\Ashi Garcia.zip"
#     tox = r"D:\Yoi"
#     start_t = time.time()
#     FileOP.Mover2(fromx, tox, callback=xx)
#     stop_t = time.time()
#     delta_t = stop_t - start_t
#     print(f"Done in {delta_t:.3f} seconds.")


# def xx(added, total_added, full):
#     percent = total_added / full * 100
#     # print(f"{percent:.2f}%")


# if __name__ == "__main__":
#     test()
