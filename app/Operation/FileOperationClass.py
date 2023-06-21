import os
import shutil
import csv
import pathlib
import json
import re
import time

config_file = "config.txt"
csv_file = ""


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
    if os.path.exists(config_file) == False:
        writeFile(config_file, '{}')
    try:
        with open('config.txt') as f:
            config = json.load(f)
            return config[key]
    except Exception as e:
        print(f'Something wrong with config.txt {e}')
        return None


def writeConfig(key, value):
    read = readFile(config_file)
    if key in read:
        read[key] = value
    else:
        read[key] = value
    try:
        with open(config_file, 'w') as f:
            json.dump(read, f)
    except:
        print('Error writing config.txt')


def write_csv(file, fields, datas):
    try:
        if not os.path.exists(file):
            open(file, "w+")
        with open(file, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(datas)
    except Exception as e:
        print(e)


def read_csv(file):
    try:
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file))
            open(file, "w+")
        rows = []
        with open(file, 'r', newline='') as file:
            obj = csv.DictReader(file)
            for row in obj:
                rows.append(row)
        return rows
    except Exception as e:
        print(e)


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
        time.sleep(1)
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
    # updateFunc(0, 0, "Done")


def Detector(file):
    # studio = readFile('d_maker_list')
    studio = read_csv('data/d_mov.csv')
    for i in studio:
        # regex to parse code from file name
        compare = re.search(
            r"\b({}.\d+)\b".format(i.get("Code")), file, re.IGNORECASE)
        if compare:
            # append valid files to array:
            return i.get("Code")
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


def Mover2(_from, _to, callback=None, buffersize=1024*1024):
    _from = pathlib.Path(_from)
    _to = pathlib.Path(_to)
    _to = _to / _from.name if _to.is_dir() else _to

    if not _from.is_file():
        print("File not exist")
        return

    if _to.exists():
        print("File already exist")
        return

    # Create dir if not exist
    if not os.path.exists(os.path.dirname(_to)):
        try:
            os.makedirs(os.path.dirname(_to), exist_ok=True)
        except Exception as error:
            print(error)
            return

    if callback is not None and not callable(callback):
        print("Callback is not callable")
        return

    if (os.stat(_from).st_dev == os.stat(os.path.dirname(_to)).st_dev):
        os.rename(_from, _to)
    else:
        if _from.is_symlink():
            print("File is symlink")
            return
        else:
            print("Moving file")
            size = _from.stat().st_size
            with open(_from, 'rb') as fsrc:
                with open(_to, 'wb') as fdst:
                    MoveObj(fsrc, fdst, callback=callback,
                            total=size, length=buffersize)
            shutil.copymode(str(_from), str(_to))  # copy permission
            print("Deleting file")
            os.remove(_from)
    return str(_to)


def MoveObj(_from, _to, callback, total, length):
    copied = 0
    while True:
        buff = _from.read(length)
        if not buff:
            break
        _to.write(buff)
        copied += len(buff)
        if callback is not None:
            callback(len(buff), copied, total)
