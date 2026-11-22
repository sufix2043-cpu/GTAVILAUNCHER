import pygame, ctypes, time, sys, os
import tkinter as tk
from tkinter import messagebox
from ffpyplayer.player import MediaPlayer
from PIL import Image, ImageTk, ImageDraw

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("rockstar.gta6.1")
except Exception:
    pass

def res(p):
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), p)

def make_dummies():
    base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    g = os.path.join(base, "Grand Theft Auto VI")
    for d in ["x64/audio", "x64/data", "x64/levels/leonida", "update", "Redistributables", "Profiles"]:
        os.makedirs(os.path.join(g, d), exist_ok=True)
    for f in ["GTA6.exe", "PlayGTA6.exe", "bink2w64.dll", "D3D12Core.dll", "common.rpf", "x64a.rpf", "x64b.rpf", "update/update.rpf", "x64/levels/leonida/vice_city.rpf"]:
        open(os.path.join(g, f), "a").close()

def play_vid(name, max_t=None, freeze=0):
    path = res(name)
    if not os.path.exists(path): return
    pygame.init()
    pygame.display.set_caption("Grand Theft Auto VI")
    if os.path.exists(res("icon.png")):
        pygame.display.set_icon(pygame.image.load(res("icon.png")))
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    scr = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    player = MediaPlayer(path)
    t0 = time.time()
    while True:
        if any(e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE) for e in pygame.event.get()):
            freeze = 0; break
        if max_t and time.time() - t0 >= max_t: break
        frame, val = player.get_frame()
        if val == 'eof': break
        if frame:
            img, _ = frame
            raw = img.to_bytearray()[0]
            surf = pygame.image.frombuffer(raw, img.get_size(), "RGB")
            scr.blit(pygame.transform.smoothscale(surf, (sw, sh)), (0, 0))
            pygame.display.flip()
        time.sleep(0.01)
    player.close_player()
    t1 = time.time()
    while time.time() - t1 < freeze:
        if any(e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE for e in pygame.event.get()): break
        time.sleep(0.05)
    pygame.quit()

play_vid("Pervoe.mp4")

root = tk.Tk()
root.title("Grand Theft Auto VI")
root.attributes("-fullscreen", True)
root.configure(bg="black")
try: root.iconphoto(True, ImageTk.PhotoImage(file=res("icon.png")))
except Exception: pass

sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
cv = tk.Canvas(root, width=sw, height=sh, bg="black", highlightthickness=0)
cv.pack(fill="both", expand=True)

tabs = ["ONLINE", "GTA+", "STORY"]
cur = 2
data = {
    "ONLINE": ("GRAND THEFT AUTO ONLINE", "Explore the dynamic world of Leonida with friends and build your empire.", "Play Grand Theft Auto Online.", "Join Online"),
    "GTA+": ("GTA+ MEMBERSHIP", "Unlock exclusive monthly benefits, bonus cash, and special vehicles in Vice City.", "Learn more about GTA+ Membership.", "View Benefits"),
    "STORY": ("GRAND THEFT AUTO VI STORY MODE", "Enter the sun-soaked state of Leonida and experience the story of Lucia and Jason.", "Play Grand Theft Auto VI's Story Mode.", "Resume Story")
}

ax, ay, aw, ah = int(sw*0.06), int(sh*0.11), int(sw*0.88), int(sh*0.76)
try:
    im = Image.open(res("gta6_art.png")).convert("RGBA").resize((aw, ah))
    gr = Image.new("RGBA", (aw, ah), (0,0,0,0))
    dr = ImageDraw.Draw(gr)
    for y in range(int(ah*0.5), ah):
        dr.line([(0,y),(aw,y)], fill=(0,0,0, int(190*((y-ah*0.5)/(ah*0.5)))))
    bg = ImageTk.PhotoImage(Image.alpha_composite(im, gr))
except Exception: bg = None

go_load = False
def start(e=None):
    global go_load; make_dummies(); go_load = True; root.quit()
def step(d):
    global cur; cur = (cur + d) % 3; draw()
def key(x, y, t):
    w = max(24, len(t)*9 + 16)
    cv.create_rectangle(x, y, x+w, y+24, fill="white", outline="white")
    cv.create_text(x+w//2, y+12, text=t, fill="black", font=("Arial", 10, "bold"))
    return w

def draw():
    cv.delete("all")
    tx, ty = ax, int(sh*0.045)
    for i, name in enumerate(tabs):
        w = len(name)*12 + 30
        if i == cur:
            cv.create_rectangle(tx, ty, tx+w, ty+30, fill="white", outline="white")
            cv.create_text(tx+w//2, ty+15, text=name, fill="black", font=("Arial", 11, "bold"))
        else:
            cv.create_text(tx+w//2, ty+15, text=name, fill="#ccc", font=("Arial", 11, "bold"))
        tx += w + 15
    if bg: cv.create_image(ax, ay, anchor="nw", image=bg)
    title, desc, foot, act = data[tabs[cur]]
    cv.create_text(ax+35, ay+ah-110, anchor="nw", text=title, fill="white", font=("Impact", 26))
    cv.create_text(ax+35, ay+ah-70, anchor="nw", text=desc, fill="#e6e6e6", font=("Arial", 12))
    fy = ay + ah + int(sh*0.04)
    cv.create_text(ax, fy+12, anchor="w", text=foot, fill="#ccc", font=("Arial", 11))
    cx = ax + aw
    cx -= key(cx-28, fy, "↵") + 10
    cv.create_text(cx, fy+12, anchor="e", text=act, fill="white", font=("Arial", 11))
    cx -= len(act)*8 + 25
    cx -= key(cx-24, fy, "E") + 5
    cx -= key(cx-24, fy, "Q") + 10
    cv.create_text(cx, fy+12, anchor="e", text="Move Tab", fill="white", font=("Arial", 11))
    cx -= 85
    cx -= key(cx-24, fy, "P") + 10
    cv.create_text(cx, fy+12, anchor="e", text="Settings", fill="white", font=("Arial", 11))
    cx -= 80
    cx -= key(cx-38, fy, "Esc") + 10
    cv.create_text(cx, fy+12, anchor="e", text="Quit", fill="white", font=("Arial", 11))

for k in ["<Return>", "<space>"]: root.bind(k, start)
root.bind("<Escape>", lambda e: root.quit())
for k in ["<q>", "<Q>", "<Left>"]: root.bind(k, lambda e: step(-1))
for k in ["<e>", "<E>", "<Right>"]: root.bind(k, lambda e: step(1))
cv.bind("<Button-1>", start)

draw()
root.mainloop()
root.destroy()

if go_load:
    play_vid("Loading.mp4", max_t=10, freeze=10)
    er = tk.Tk(); er.title("Grand Theft Auto VI")
    try: er.iconphoto(True, ImageTk.PhotoImage(file=res("icon.png")))
    except Exception: pass
    er.withdraw()
    messagebox.showerror("Grand Theft Auto VI - Fatal Error", "ERR_GFX_D3D_INIT: Failed initialization. Please reboot and restart the game.\n\nException code: 0xc0000005\nFaulting module: D3D12Core.dll")
    er.destroy()

