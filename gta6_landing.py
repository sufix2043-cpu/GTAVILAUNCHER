import pygame
from ffpyplayer.player import MediaPlayer
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import time
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- СОЗДАНИЕ ПАПКИ С ФАЙЛАМИ-ПУСТЫШКАМИ GTA 6 ---
def create_fake_game_folder():
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.abspath(".")

    game_dir = os.path.join(current_dir, "Grand Theft Auto VI")
    subfolders = [
        "x64", os.path.join("x64", "audio"), os.path.join("x64", "data"),
        os.path.join("x64", "levels", "leonida"), "update", "Redistributables", "Profiles"
    ]
    dummy_files = [
        "GTA6.exe", "PlayGTA6.exe", "GTAVILauncher.exe", "bink2w64.dll",
        "D3D12Core.dll", "GFSDK_ShadowLib.win64.dll", "steam_api64.dll",
        "common.rpf", "x64a.rpf", "x64b.rpf", "x64c.rpf", "x64d.rpf",
        "x64e.rpf", "x64w.rpf", os.path.join("update", "update.rpf"),
        os.path.join("x64", "levels", "leonida", "vice_city.rpf"), "commandline.txt"
    ]
    try:
        os.makedirs(game_dir, exist_ok=True)
        for folder in subfolders:
            os.makedirs(os.path.join(game_dir, folder), exist_ok=True)
        for file_rel_path in dummy_files:
            full_path = os.path.join(game_dir, file_rel_path)
            if not os.path.exists(full_path):
                with open(full_path, "w"):
                    pass
    except Exception:
        pass

# --- ВОСПРОИЗВЕДЕНИЕ ВИДЕО (С ОПЦИЕЙ ЗАВИСАНИЯ В КОНЦЕ) ---
def play_fullscreen_video(filename, max_duration=None, freeze_duration=0):
    video_path = resource_path(filename)
    if not os.path.exists(video_path):
        return

    pygame.init()
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    player = MediaPlayer(video_path)
    start_time = time.time()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                freeze_duration = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                freeze_duration = 0

        if max_duration and (time.time() - start_time >= max_duration):
            break

        frame, val = player.get_frame()
        if val == 'eof':
            break
        if frame is not None:
            img, t = frame
            w, h = img.get_size()
            surf = pygame.image.frombuffer(img.to_bytearray(), (w, h), "RGB")
            surf = pygame.transform.smoothscale(surf, (screen_w, screen_h))
            screen.blit(surf, (0, 0))
            pygame.display.flip()

        time.sleep(0.01)

    # Останавливаем плеер, но НЕ закрываем окно — последний кадр остается "висеть" на экране
    player.close_player()

    if freeze_duration > 0:
        freeze_start = time.time()
        while time.time() - freeze_start < freeze_duration:
            for event in pygame.event.get():
                # Нажатие ESC все еще позволяет прервать зависание при тесте
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    freeze_duration = 0
            time.sleep(0.05)

    pygame.quit()

# --- ЭТАП 1: ВСТУПИТЕЛЬНОЕ ВИДЕО (Pervoe.mp4) ---
play_fullscreen_video("Pervoe.mp4")

# --- ЭТАП 2: ГЛАВНОЕ МЕНЮ В СТИЛЕ GTA (НА АНГЛИЙСКОМ) ---
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="black")

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

tabs = ["ONLINE", "GTA+", "STORY"]
current_tab_index = 2

tab_content = {
    "ONLINE": {
        "title": "GRAND THEFT AUTO ONLINE",
        "desc": "Explore the dynamic world of Leonida with friends, build your criminal empire,\nand take part in high-stakes heists across Vice City.",
        "footer": "Play Grand Theft Auto Online.",
        "action": "Join Online"
    },
    "GTA+": {
        "title": "GTA+ MEMBERSHIP",
        "desc": "Unlock exclusive monthly benefits in Grand Theft Auto Online including\nbonus cash, special vehicles, properties, and classic Rockstar titles.",
        "footer": "Learn more about GTA+ Membership.",
        "action": "View Benefits"
    },
    "STORY": {
        "title": "GRAND THEFT AUTO VI STORY MODE",
        "desc": "Enter the sun-soaked state of Leonida and experience the story\nof Lucia and Jason.",
        "footer": "Play Grand Theft Auto VI's Story Mode.",
        "action": "Resume Story"
    }
}

art_x = int(screen_w * 0.06)
art_y = int(screen_h * 0.11)
art_w = int(screen_w * 0.88)
art_h = int(screen_h * 0.76)

try:
    raw_img = Image.open(resource_path("gta6_art.png")).convert("RGBA")
    raw_img = raw_img.resize((art_w, art_h), Image.Resampling.LANCZOS)
    
    gradient = Image.new("RGBA", (art_w, art_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    for y in range(int(art_h * 0.5), art_h):
        alpha = int(190 * ((y - art_h * 0.5) / (art_h * 0.5)))
        draw.line([(0, y), (art_w, y)], fill=(0, 0, 0, alpha))
    
    combined = Image.alpha_composite(raw_img, gradient)
    bg_photo = ImageTk.PhotoImage(combined)
except Exception:
    bg_photo = None

start_loading_video = False

def launch_game(event=None):
    global start_loading_video
    create_fake_game_folder()
    start_loading_video = True
    root.quit()

def quit_app(event=None):
    root.quit()

def switch_tab(delta):
    global current_tab_index
    current_tab_index = (current_tab_index + delta) % len(tabs)
    draw_ui()

def draw_keycap(x, y, text):
    pad_x = 8
    box_w = max(24, len(text) * 9 + pad_x * 2)
    box_h = 24
    canvas.create_rectangle(x, y, x + box_w, y + box_h, fill="white", outline="white")
    canvas.create_text(x + box_w // 2, y + box_h // 2, text=text, fill="black", font=("Arial", 10, "bold"))
    return box_w

def draw_ui():
    canvas.delete("all")
    
    tab_x = art_x
    tab_y = int(screen_h * 0.045)
    for idx, name in enumerate(tabs):
        is_selected = (idx == current_tab_index)
        w = len(name) * 12 + 30
        h = 30
        if is_selected:
            canvas.create_rectangle(tab_x, tab_y, tab_x + w, tab_y + h, fill="white", outline="white")
            canvas.create_text(tab_x + w // 2, tab_y + h // 2, text=name, fill="black", font=("Arial", 11, "bold"))
        else:
            canvas.create_text(tab_x + w // 2, tab_y + h // 2, text=name, fill="#cccccc", font=("Arial", 11, "bold"))
        tab_x += w + 15

    if bg_photo:
        canvas.create_image(art_x, art_y, anchor="nw", image=bg_photo)
    else:
        canvas.create_rectangle(art_x, art_y, art_x + art_w, art_y + art_h, fill="#1a1a1a", outline="#333333")

    info = tab_content[tabs[current_tab_index]]
    text_x = art_x + 35
    title_y = art_y + art_h - 115
    desc_y = art_y + art_h - 75

    canvas.create_text(text_x, title_y, anchor="nw", text=info["title"], fill="white", font=("Impact", 26))
    canvas.create_text(text_x, desc_y, anchor="nw", text=info["desc"], fill="#e6e6e6", font=("Arial", 12))

    footer_y = art_y + art_h + int(screen_h * 0.04)
    canvas.create_text(art_x, footer_y + 12, anchor="w", text=info["footer"], fill="#cccccc", font=("Arial", 11))

    cur_x = art_x + art_w

    kw = draw_keycap(cur_x - 28, footer_y, "↵")
    cur_x -= (kw + 10)
    action_id = canvas.create_text(cur_x, footer_y + 12, anchor="e", text=info["action"], fill="white", font=("Arial", 11))
    canvas.tag_bind(action_id, "<Button-1>", launch_game)
    cur_x -= (len(info["action"]) * 8 + 25)

    kw_e = draw_keycap(cur_x - 24, footer_y, "E")
    cur_x -= (kw_e + 5)
    kw_q = draw_keycap(cur_x - 24, footer_y, "Q")
    cur_x -= (kw_q + 10)
    canvas.create_text(cur_x, footer_y + 12, anchor="e", text="Move Tab", fill="white", font=("Arial", 11))
    cur_x -= 85

    kw_p = draw_keycap(cur_x - 24, footer_y, "P")
    cur_x -= (kw_p + 10)
    canvas.create_text(cur_x, footer_y + 12, anchor="e", text="Settings", fill="white", font=("Arial", 11))
    cur_x -= 80

    kw_esc = draw_keycap(cur_x - 38, footer_y, "Esc")
    cur_x -= (kw_esc + 10)
    quit_id = canvas.create_text(cur_x, footer_y + 12, anchor="e", text="Quit", fill="white", font=("Arial", 11))
    canvas.tag_bind(quit_id, "<Button-1>", quit_app)

root.bind("<Return>", launch_game)
root.bind("<space>", launch_game)
root.bind("<Escape>", quit_app)
root.bind("<q>", lambda e: switch_tab(-1))
root.bind("<Q>", lambda e: switch_tab(-1))
root.bind("<e>", lambda e: switch_tab(1))
root.bind("<E>", lambda e: switch_tab(1))
root.bind("<Left>", lambda e: switch_tab(-1))
root.bind("<Right>", lambda e: switch_tab(1))
canvas.bind("<Button-1>", launch_game)

draw_ui()
root.mainloop()
root.destroy()

# --- ЭТАП 3: 10 СЕКУНД ЗАГРУЗКИ + 10 СЕКУНД ЗАВИСАНИЯ + ВЫЛЕТ ---
if start_loading_video:
    play_fullscreen_video("Loading.mp4", max_duration=10, freeze_duration=10)
    
    err_root = tk.Tk()
    err_root.withdraw()
    messagebox.showerror(
        "Grand Theft Auto VI - Fatal Error",
        "ERR_GFX_D3D_INIT: Failed initialization. Please reboot and restart the game.\n\n"
        "Exception code: 0xc0000005 (EXCEPTION_ACCESS_VIOLATION)\n"
        "Faulting module: D3D12Core.dll"
    )
    err_root.destroy()
