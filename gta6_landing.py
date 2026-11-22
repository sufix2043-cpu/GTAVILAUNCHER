import pygame, ctypes, time, sys, os
from ffpyplayer.player import MediaPlayer
from PIL import Image, ImageDraw

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("rockstar.gta6.single.v5")
except Exception:
    pass

def res(p):
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), p)

def set_win_icon(hwnd):
    ico = res("icon.ico")
    if os.path.exists(ico):
        try:
            hicon = ctypes.windll.user32.LoadImageW(0, ico, 1, 0, 0, 0x00000010 | 0x00008000)
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)
        except Exception:
            pass

def make_dummies():
    base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    g = os.path.join(base, "Grand Theft Auto VI")
    for d in ["x64/audio", "x64/data", "x64/levels/leonida", "update", "Redistributables", "Profiles"]:
        os.makedirs(os.path.join(g, d), exist_ok=True)
    for f in ["GTA6.exe", "PlayGTA6.exe", "bink2w64.dll", "D3D12Core.dll", "common.rpf", "x64a.rpf", "x64b.rpf", "update/update.rpf", "x64/levels/leonida/vice_city.rpf"]:
        open(os.path.join(g, f), "a").close()

# --- СОЗДАЕМ ОДНО ОБЩЕЕ ОКНО НА ВСЁ ВРЕМЯ РАБОТЫ ---
pygame.init()
pygame.display.set_caption("Grand Theft Auto VI")
if os.path.exists(res("icon.png")):
    pygame.display.set_icon(pygame.image.load(res("icon.png")))

info = pygame.display.Info()
sw, sh = info.current_w, info.current_h
scr = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)
set_win_icon(pygame.display.get_wm_info()["window"])
pygame.mouse.set_visible(False)

def play_vid(name, max_t=None, freeze=0):
    path = res(name)
    if not os.path.exists(path): return
    player = MediaPlayer(path)
    t0 = time.time()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                player.close_player()
                return False
        if max_t and time.time() - t0 >= max_t:
            break
        frame, val = player.get_frame()
        if val == 'eof':
            break
        if frame:
            img, _ = frame
            surf = pygame.image.frombuffer(img.to_bytearray(), img.get_size(), "RGB")
            scr.blit(pygame.transform.smoothscale(surf, (sw, sh)), (0, 0))
            pygame.display.flip()
        time.sleep(0.01)
    player.close_player()
    t1 = time.time()
    while time.time() - t1 < freeze:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return False
        time.sleep(0.05)
    return True

# --- ЭТАП 1: ВСТУПИТЕЛЬНОЕ ВИДЕО ---
play_vid("Pervoe.mp4")

# --- ЭТАП 2: МЕНЮ В ТОМ ЖЕ ОКНЕ (ТОЛЬКО STORY) ---
ax, ay, aw, ah = int(sw * 0.06), int(sh * 0.11), int(sw * 0.88), int(sh * 0.76)
bg_surf = None
if os.path.exists(res("gta6_art.png")):
    try:
        im = Image.open(res("gta6_art.png")).convert("RGBA").resize((aw, ah))
        gr = Image.new("RGBA", (aw, ah), (0, 0, 0, 0))
        dr = ImageDraw.Draw(gr)
        for y in range(int(ah * 0.5), ah):
            dr.line([(0, y), (aw, y)], fill=(0, 0, 0, int(195 * ((y - ah * 0.5) / (ah * 0.5)))))
        comb = Image.alpha_composite(im, gr)
        bg_surf = pygame.image.fromstring(comb.tobytes(), comb.size, comb.mode)
    except Exception:
        pass

f_tab = pygame.font.SysFont("Arial", 16, bold=True)
f_title = pygame.font.SysFont("Impact", 36)
f_desc = pygame.font.SysFont("Arial", 18)
f_foot = pygame.font.SysFont("Arial", 16)
f_key = pygame.font.SysFont("Arial", 14, bold=True)

def draw_key(x, y, text):
    w = max(28, len(text) * 11 + 14)
    pygame.draw.rect(scr, (255, 255, 255), (x, y, w, 26))
    t_surf = f_key.render(text, True, (0, 0, 0))
    scr.blit(t_surf, (x + (w - t_surf.get_width()) // 2, y + 5))
    return w

def draw_menu():
    scr.fill((0, 0, 0))
    # Верхняя вкладка (только STORY)
    tx, ty = ax, int(sh * 0.045)
    w = len("STORY") * 14 + 34
    pygame.draw.rect(scr, (255, 255, 255), (tx, ty, w, 32))
    t_s = f_tab.render("STORY", True, (0, 0, 0))
    scr.blit(t_s, (tx + (w - t_s.get_width()) // 2, ty + 7))

    # Центральный арт
    if bg_surf:
        scr.blit(bg_surf, (ax, ay))
    else:
        pygame.draw.rect(scr, (25, 25, 25), (ax, ay, aw, ah))

    # Текст поверх арта
    scr.blit(f_title.render("GRAND THEFT AUTO VI STORY MODE", True, (255, 255, 255)), (ax + 35, ay + ah - 115))
    scr.blit(f_desc.render("Enter the sun-soaked state of Leonida and experience the story of Lucia and Jason.", True, (230, 230, 230)), (ax + 35, ay + ah - 68))

    # Нижняя панель с кнопками
    fy = ay + ah + int(sh * 0.035)
    scr.blit(f_foot.render("Play Grand Theft Auto VI's Story Mode.", True, (200, 200, 200)), (ax, fy + 4))

    cx = ax + aw
    cx -= draw_key(cx - 52, fy, "Enter") + 10
    act_s = f_foot.render("Resume Story", True, (255, 255, 255))
    scr.blit(act_s, (cx - act_s.get_width(), fy + 4))
    cx -= act_s.get_width() + 28

    cx -= draw_key(cx - 26, fy, "P") + 10
    st_s = f_foot.render("Settings", True, (255, 255, 255))
    scr.blit(st_s, (cx - st_s.get_width(), fy + 4))
    cx -= st_s.get_width() + 28

    cx -= draw_key(cx - 38, fy, "Esc") + 10
    qt_s = f_foot.render("Quit", True, (255, 255, 255))
    scr.blit(qt_s, (cx - qt_s.get_width(), fy + 4))

    pygame.display.flip()

go_load = False
in_menu = True
draw_menu()

while in_menu:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            in_menu = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                in_menu = False
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                make_dummies()
                go_load = True
                in_menu = False
    time.sleep(0.02)

# --- ЭТАП 3: ЗАГРУЗКА (10 СЕК) + ЗАВИСАНИЕ (20 СЕК) + ВЫЛЕТ ---
if go_load:
    play_vid("Loading.mp4", max_t=10, freeze=20)
    pygame.quit()
    ctypes.windll.user32.MessageBoxW(
        0,
        "ERR_GFX_D3D_INIT: Failed initialization. Please reboot and restart the game.\n\nException code: 0xc0000005\nFaulting module: D3D12Core.dll",
        "Grand Theft Auto VI - Fatal Error",
        0x10
    )
else:
    pygame.quit()

