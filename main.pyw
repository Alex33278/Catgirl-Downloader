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
VERSION = "1.4"

# Dates are in MM/DD/YYYY format
# Ver 1.0 - General Release - 10/10/2025
# Ver 1.1 - Allow for downloading images - 10/10/2025
# Ver 1.2 - Made downloads async - 10/11/2025
# Ver 1.3 - Added prefrences saving - 10/11/2025
# Ver 1.4 - Added option to show all images, about art window, save session, caching & bug fixes - 10/23/2025

import argparse
import sys
import os

# Hacky way to set active dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.argv[0] = __file__

def relaunch():
    os.execv(sys.executable, ['python3'] + sys.argv)

parser = argparse.ArgumentParser(prog=f"Catgirl Downloader V{VERSION}", description="Little python script to display some catgirls!")
parser.add_argument("--reinstall", action="store_true", help="Force reinstalls all packages.")
parser.add_argument("--flush_cache", action="store_true", help="Flushes the cache.")

args = parser.parse_args()

try:
    if args.reinstall:
        raise ImportError

    import tkinter
    import tkinter.filedialog
    import requests
    import queue
    import webbrowser
    import threading
    import base64
    import random
    import io
    from PIL import Image, ImageTk

    try:
        import orjson as json
    except:
        import json # Don't force user to install orjson (still would if possible)

    try:
        import requests_cache
    except:
        pass
except ImportError:
    import importlib
    import tkinter.messagebox

    if tkinter.messagebox.askyesno("Catgirl Downloader", "Missing imports! Would you like to download them now?"):
        os.system("pip install pillow")
        os.system("pip install requests")
        os.system("pip install orjson")
        os.system("pip install requests_cache")
        importlib.invalidate_caches()
        if args.reinstall:
            print("Reinstall successful, you can re-run the program now.")
            sys.exit(0)
        relaunch()
    sys.exit(0)

root = tkinter.Tk()
root.wm_title(f"Catgirl Downloader V{VERSION}")
root.wm_geometry("800x800")
root.wm_minsize(300, 350)

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

    def open_image(self, img):
        self.delete_previous_image()
        self.source_image = Image.open(img)
        self.image = ImageTk.PhotoImage(self.source_image)
        self.extension = None

        try:
            self.extension = self.source_image.format
        except:
            print("Failed to identify img extension")

        self.resize_image()
        self.paste_image()

    def open_image_bytes(self, bytes) -> None:
        self.open_image(io.BytesIO(bytes))

nsfw = tkinter.StringVar(value="Block")
saveSession = tkinter.BooleanVar(value=True)
info = None
running = True
refreshInProgress = False
imageBytes = None
results = queue.Queue()
cacheAllowed = "requests_cache" in sys.modules
cacheEnabled = tkinter.BooleanVar(value=False)
session = None

def newCache():
    global session
    global cacheAllowed
    if cacheAllowed:
        session = requests_cache.CachedSession("CGD_IMG_CACHE", expire_after=86400)

def closeCache():
    if cacheAllowed and session:
        session.close()

def flushCache():
    if os.path.exists("CGD_IMG_CACHE.sqlite"):
        closeCache()
        os.remove("CGD_IMG_CACHE.sqlite")
        print("Cache flushed successfully")
        newCache()
    else:
        print("No cache found - did nothing")

newCache()

def GetImgIDRand(nsfw = False):
    try:
        r = requests.get(f"https://nekos.moe/api/v1/random/image?nsfw={str(nsfw).lower()}&count=1", timeout=10)
        if r.status_code == 200:
            return r.text
        else:
            return None
    except Exception as e:
        print(e)
        return None

def GetImgURLFromID(response):
    if response:
        global info
        data = json.loads(response)
        info = data
        return f"https://nekos.moe/image/{data["images"][0]['id']}"
    return None

def GetNeko(nsfw=False):
    return GetImgURLFromID(GetImgIDRand(nsfw))

def GetImage(url, cache):
    if url:
        r = None
        if cache and cacheAllowed:
            r = session.get(url, timeout=20)
        else:
            r = requests.get(url, timeout=20)
        return r.content
    return None

def DownloadImage(results, nsfw, cache):
    global imageBytes
    global refreshInProgress
    try:
        imageBytes = GetImage(GetNeko(nsfw), cache)
        if imageBytes:
            results.put(imageBytes)
        else:
            results.put("FAILED")
    except Exception as e:
        print(f"Failed to display image! {e}")
        menubar.entryconfigure("Refresh", state="normal")
        refreshInProgress = False

def DownloadImageWrapper():
    global refreshInProgress

    if refreshInProgress:
        return

    menubar.entryconfigure("Refresh", state="disabled")
    refreshInProgress = True
    b_nsfw = False

    if nsfw.get() == "Only":
        b_nsfw = True

    if nsfw.get() == "Everything":
        b_nsfw = random.random() > 0.5

    threading.Thread(target=DownloadImage, args=(results, b_nsfw, cacheEnabled.get()), daemon=True).start()

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

    window.grab_set()
    window.transient(root)

def CreateAboutArtWindow():
    if not info: return

    window = tkinter.Toplevel()
    window.wm_title("About Art")
    window.wm_geometry("300x300")
    window.wm_resizable(False, False)
    content = tkinter.Label(window, text=f"Artist: {info["images"][0]["artist"]}\n\nTags: {(", ").join(info["images"][0]["tags"])}", wraplength=300)
    content.pack()

    window.grab_set()
    window.transient(root)

def SaveImg():
    if not imageBytes: return

    extension = "JPEG"

    if canvasImg.extension: 
        extension = canvasImg.extension
    
    if not (filename := tkinter.filedialog.asksaveasfilename(title="Save Image As", filetypes=[(f"{extension} files", f"*.{extension.lower()}"), ('All files', '*.*')], defaultextension=f".{extension.lower()}", initialfile="catgirl")): return
    with open(filename, "wb") as file:
        file.write(imageBytes)
        file.close()

def resetPreferences():
    if os.path.isfile("preferences.cgd.json"):
        os.remove("preferences.cgd.json")
        relaunch()

menubar = tkinter.Menu(root, tearoff=0)

preferencesMenu = tkinter.Menu(menubar, tearoff=0)
nsfwMenu = tkinter.Menu(preferencesMenu, tearoff=0)
nsfwMenu.add_radiobutton(label="Block", variable=nsfw)
nsfwMenu.add_radiobutton(label="Only", variable=nsfw)
nsfwMenu.add_radiobutton(label="Everything", variable=nsfw)
preferencesMenu.add_cascade(label="NSFW Settings", menu=nsfwMenu)
preferencesMenu.add_checkbutton(label="Save Session", variable=saveSession)
preferencesMenu.add_checkbutton(label="Cache Enabled", variable=cacheEnabled, state=("normal" if cacheAllowed else "disabled"))
preferencesMenu.add_separator()
preferencesMenu.add_command(label="Reset Preferences", command=resetPreferences)
preferencesMenu.add_command(label="Flush Cache", command=flushCache)
menubar.add_cascade(label="Preferences", menu=preferencesMenu)

helpMenu = tkinter.Menu(menubar, tearoff=0)
helpMenu.add_command(label="About Art", command=CreateAboutArtWindow, state="disabled")
helpMenu.add_command(label="About Catgirl Downloader", command=CreateAboutWindow)
menubar.add_cascade(label="Help", menu=helpMenu)

menubar.add_command(label="Save", command=SaveImg, state="disabled")
menubar.add_command(label="Refresh", command=DownloadImageWrapper)

root.config(menu=menubar)

def showMessage(msg):
    msgLabel = tkinter.Label(root, text=msg, background="#1F1F1F", foreground="white")
    msgLabel.place(x=root.winfo_width()/2-200, y=50, width=400, height=50)
    root.after(5000, msgLabel.destroy)

def SavePreferences():
    maximized = root.wm_state() == "zoomed"
    root.wm_state("normal")

    save = {
        "NSFW": nsfw.get(),
        "WIN_SIZE": root.geometry().split("+")[0],
        "MAX": maximized,
        "CE": cacheEnabled.get(),
        "SS": saveSession.get()
    }

    if save["SS"]:
        save["SS_IMG_INFO"] = info
        save["SS_IMG"] = base64.b85encode(imageBytes).decode("utf-8")

    saveSTR = json.dumps(save)
    if isinstance(saveSTR, str):
        saveSTR = saveSTR.encode("utf-8")

    with open("preferences.cgd.json", "wb") as file:
        file.write(saveSTR)
        file.close()

def LoadPreferences():
    global imageBytes
    global info
    if os.path.isfile("preferences.cgd.json"):
        try:
            preferences = None
            with open("preferences.cgd.json", "r") as file:
                preferences = json.loads(file.read())
        
            if "NSFW" in preferences:
                nsfw.set(preferences["NSFW"])
            if "WIN_SIZE" in preferences:
                root.wm_geometry(preferences["WIN_SIZE"].split("+")[0])
            if "MAX" in preferences and preferences["MAX"]:
                root.wm_state("zoomed")
            if "CE" in preferences and cacheAllowed:
                cacheEnabled.set(preferences["CE"])
            if "SS" in preferences:
                saveSession.set(preferences["SS"])
                if "SS_IMG_INFO" in preferences:
                    info = preferences["SS_IMG_INFO"]
                    helpMenu.entryconfigure("About Art", state="normal")
                if "SS_IMG" in preferences:
                    imageBytes = base64.b85decode(preferences["SS_IMG"])
                    canvasImg.open_image_bytes(imageBytes)
                    menubar.entryconfigure("Save", state="normal")
        except Exception as e:
            print(f"Error loading preferences! {e}")
            showMessage("Error loading preferences")
            return

def onClose():
    global running
    running = False
    closeCache()
    SavePreferences()
    root.destroy()

canvasImg = CanvasImage(root)
canvasImg.pack(expand=True, fill="both")

root.update()

canvasImg.update_values()

LoadPreferences()

if not (saveSession.get() and os.path.exists("preferences.cgd.json")):
    DownloadImageWrapper()

root.protocol("WM_DELETE_WINDOW", onClose)
root.bind("<space>", lambda e: DownloadImageWrapper())

while running:
    root.update()

    try:
        res = results.get_nowait()
        if res and res != "FAILED":
            imageBytes = res
            canvasImg.open_image_bytes(imageBytes)
            menubar.entryconfigure("Save", state="normal")
            helpMenu.entryconfigure("About Art", state="normal")
        else:
            print("FAILED TO GET IMAGE")
            showMessage("Error occured fetching image")
        menubar.entryconfigure("Refresh", state="normal")
        refreshInProgress = False
    except queue.Empty:
        pass
    except Exception as e:
        print("Unexpected exception occured! " + e)
        showMessage("Unexpected exception occured")