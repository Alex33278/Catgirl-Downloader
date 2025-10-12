# main.pyw
#
# Copyright 2025 Gigapixel Entertainment LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later


# Catgirl Downloader
# Windows version of https://github.com/NyarchLinux/CatgirlDownloader
# Ver 1.3

# Ver 1.0 - General Release
# Ver 1.1 - Allow for downloading images
# Ver 1.2 - Made downloads async
# Ver 1.3 - Added prefrences saving

VERSION = "1.3"

import sys
import os
def relaunch():
    os.execv(sys.executable, ['python3'] + sys.argv)

try:
    import tkinter
    import tkinter.filedialog
    import requests
    import queue
    import webbrowser
    import threading
    import json
    import io
    from PIL import Image, ImageTk
except ImportError:
    import importlib
    import tkinter.messagebox

    if tkinter.messagebox.askyesno("Catgirl Downloader", "Missing imports! Would you like to download them now?"):
        os.system("pip install pillow")
        os.system("pip install requests")
        os.system("pip install webbrowser")
        importlib.invalidate_caches()
        relaunch()
    sys.exit(0)

root = tkinter.Tk()
root.wm_title("Catgirl Downloader")
root.wm_geometry("800x800")

nsfw = tkinter.StringVar(value="Block")
info = None
running = True
imageBytes = None
results = queue.Queue()

RANDOM_URL = "https://nekos.moe/api/v1/random/image?nsfw="
IMAGE_URL = "https://nekos.moe/image/"

def GetPage(nsfw = False):
    try:
        r = requests.get(RANDOM_URL + str(nsfw).lower(), timeout=10)
        if r.status_code == 200:
            return r.text
        else:
            return None
    except Exception as e:
        print(e)
        return None

def GetPageURL(response):
    global info
    data = json.loads(response)
    info = data
    return IMAGE_URL + data["images"][0]['id']

def GetNeko(nsfw=False):
    return GetPageURL(GetPage(nsfw))

def GetImage(url):
    r = requests.get(url, timeout=20)
    return r.content

def DownloadImage(results, nsfw):
    global imageBytes
    try:
        imageBytes = GetImage(GetNeko(nsfw))
        results.put(imageBytes)
    except Exception as e:
        print(f"Failed to display image! {e}")

def DownloadImageWrapper(nsfw):
    threading.Thread(target=DownloadImage, args=(results, True if nsfw == "Only" else False), daemon=True).start()

def CreateAboutWindow():
    window = tkinter.Toplevel()
    window.wm_title("About")
    window.wm_geometry("300x300")
    window.wm_resizable(False, False)

    title = tkinter.Label(window, text="Catgirl Downloader", font=("Arial", 24))
    title.pack()

    version = tkinter.Label(window, text=f"Version {VERSION}")
    version.pack()

    content = tkinter.Text(window, wrap=tkinter.WORD, width=40)
    content.pack()
    content.insert(tkinter.END, "All images are from ")
    content.insert(tkinter.END, "https://nekos.moe", "hyperlink")
    content.insert(tkinter.END, ". Licensed under the GNU GENERAL PUBLIC LICENSE V3")

    content.tag_configure("hyperlink", foreground="blue", underline=1)
    content.tag_bind("hyperlink", "<Button-1>", lambda e: webbrowser.open_new_tab("https://nekos.moe"))
    content.tag_bind("hyperlink", "<Enter>", lambda e: content.configure(cursor="hand2"))
    content.tag_bind("hyperlink", "<Leave>", lambda e: content.configure(cursor=""))

    content.configure(
        state="disabled",
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        bg=window.cget('bg'),
        font=("Arial", 10)
    )

def SaveImg():
    if not imageBytes: return
    if not (filename := tkinter.filedialog.asksaveasfilename(title="Save Img as", filetypes=[("JPG files", "*.jpg"), ('All files', '*.*')], defaultextension=".jpg")): return
    with open(filename, "wb") as file:
        file.write(imageBytes)
        file.close()

def resetPreferences():
    if os.path.isfile("preferences.cgd.json"):
        os.remove("preferences.cgd.json")
        relaunch()

menubar = tkinter.Menu(root)

preferencesMenu = tkinter.Menu(menubar, tearoff=0)
nsfwMenu = tkinter.Menu(preferencesMenu, tearoff=0)
nsfwMenu.add_radiobutton(label="Block", variable=nsfw)
nsfwMenu.add_radiobutton(label="Only", variable=nsfw)
preferencesMenu.add_cascade(label="NSFW Settings", menu=nsfwMenu)
preferencesMenu.add_separator()
preferencesMenu.add_command(label="Reset Preferences", command=resetPreferences)
menubar.add_cascade(label="Preferences", menu=preferencesMenu)

helpMenu = tkinter.Menu(menubar, tearoff=0)
helpMenu.add_command(label="About", command=CreateAboutWindow)
menubar.add_cascade(label="Help", menu=helpMenu)

menubar.add_command(label="Save", command=SaveImg)
menubar.add_command(label="Refresh", command=lambda: DownloadImageWrapper(nsfw.get()))

root.config(menu=menubar)

root.update()
root.update_idletasks()

class CanvasImage(tkinter.Canvas):
    def __init__(self, master: tkinter.Tk, **kwargs):
        super().__init__(master, **kwargs)

        self.source_image = None
        self.image_id = None
        self.image = None

        self.width, self.height = 0, 0
        self.center_x, self.center_y = 0, 0
        self.bind('<Configure>', self.update_values)
    
    def update_values(self, *_) -> None:
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.center_x = self.width//2
        self.center_y = self.height//2

        if self.image is None: return
        self.delete_previous_image()
        self.resize_image()
        self.paste_image()

    def delete_previous_image(self) -> None:
        if self.image is None: return
        self.delete(self.image_id)
        self.image = self.image_id = None

    def resize_image(self) -> None:
        image_width, image_height = self.source_image.size
        width_ratio = self.width / image_width
        height_ratio = self.height / image_height
        ratio = min(width_ratio, height_ratio)

        new_width = int(image_width * ratio)
        new_height = int(image_height * ratio)
        scaled_image = self.source_image.resize((new_width, new_height))
        self.image = ImageTk.PhotoImage(scaled_image)

    def paste_image(self) -> None:
        self.image_id = self.create_image(self.center_x, self.center_y, anchor=tkinter.CENTER, image=self.image)

    def open_image(self, bytes) -> None:
        self.delete_previous_image()
        self.source_image = Image.open(io.BytesIO(bytes))
        self.image = ImageTk.PhotoImage(self.source_image)

        self.resize_image()
        self.paste_image()

def SavePreferences():
    with open("preferences.cgd.json", "w") as file:
        json.dump({"NSFW": nsfw.get(), "WIN_SIZE": root.geometry().split("+")[0]}, file, indent=None)
        file.close()

def LoadPreferences():
    if os.path.isfile("preferences.cgd.json"):
        try:
            preferences = None
            with open("preferences.cgd.json", "r") as file:
                preferences = json.load(file)
        
            if "NSFW" in preferences:
                nsfw.set(preferences["NSFW"])
            if "WIN_SIZE" in preferences:
                root.wm_geometry(preferences["WIN_SIZE"].split("+")[0])
        except Exception as e:
            print(f"Error loading preferences! {e}")
            return

def onClose():
    global running
    running = False
    SavePreferences()
    root.destroy()

canvasImg = CanvasImage(root)
canvasImg.pack(expand=True, fill="both")

LoadPreferences()

DownloadImageWrapper(nsfw.get())
root.protocol("WM_DELETE_WINDOW", onClose)

while running:
    root.update()
    root.update_idletasks()

    try:
        res = results.get_nowait()
        imageBytes = res
        canvasImg.open_image(imageBytes)
    except queue.Empty:
        pass