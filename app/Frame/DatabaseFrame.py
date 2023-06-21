import customtkinter
import app.Operation.FileOperationClass as FileOP


class Main(customtkinter.CTkToplevel):
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
        self.update()
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
        self.update()
