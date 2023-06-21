import FileOperationClass as FileOP


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
