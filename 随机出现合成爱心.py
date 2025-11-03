import tkinter as tk
import random
import math
import ctypes
import time

WINDOW_W = 160
WINDOW_H = 38
NUM_WINDOWS = 96
MOVE_STEP = 50

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)

def generate_heart_points(num_points, window_width, window_height):
    t_list = [2 * math.pi * i / num_points for i in range(num_points)]
    raw = [
        (16 * math.sin(t) ** 3, 13 * math.cos(t) - 5 * math.cos(2 * t)
         - 2 * math.cos(3 * t) - math.cos(4 * t)) for t in t_list
    ]
    xs = [p[0] for p in raw]
    ys = [p[1] for p in raw]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    usable_w = SCREEN_W - window_width
    usable_h = SCREEN_H - window_height
    scale = min(usable_w / (max_x - min_x + 0.7), usable_h / (max_y - min_y + 0.8))
    heart_w = (max_x - min_x) * scale
    heart_h = (max_y - min_y) * scale
    base_x = (SCREEN_W - heart_w) // 2
    base_y = (SCREEN_H - heart_h) // 2
    mapped = []
    for x0, y0 in raw:
        nx = (x0 - min_x)
        ny = (y0 - min_y)
        px = int(base_x + nx * scale)
        py = int(base_y + heart_h - ny * scale)
        px = max(0, min(px, SCREEN_W-window_width))
        py = max(0, min(py, SCREEN_H-window_height))
        mapped.append((px, py))
    dedup = []
    seen = set()
    for p in mapped:
        if p not in seen:
            seen.add(p)
            dedup.append(p)
    return dedup[:num_points]

tips = ['多喝水哦~', '保持微笑呀', '每天都要元气满满', '记得吃水果', '保持好心情', '好好爱自己', '我想你了',
        '梦想成真', '期待下一次见面', '天冷了，多穿衣服', '愿所有烦恼都消失', '不要熬夜', '爱你哦~']
bg_colors = ['lightpink', 'skyblue', 'lightgreen', 'lavender', 'lightyellow',
            'plum', 'coral', 'bisque', 'aquamarine', 'mistyrose', 'honeydew']

if __name__ == "__main__":
    margin_x = WINDOW_W // 2
    margin_y = WINDOW_H // 2
    points_random = []
    for _ in range(NUM_WINDOWS):
        x = random.randint(margin_x, SCREEN_W - WINDOW_W - margin_x)
        y = random.randint(margin_y, SCREEN_H - WINDOW_H - margin_y)
        points_random.append((x, y))
    points_heart = generate_heart_points(NUM_WINDOWS, WINDOW_W, WINDOW_H)
    if len(points_heart) < NUM_WINDOWS:
        points_heart += [points_heart[-1]] * (NUM_WINDOWS - len(points_heart))

    root = tk.Tk()
    root.withdraw()
    all_windows = []
    for idx, (x, y) in enumerate(points_random):
        win = tk.Toplevel(root)
        win.title('温馨提示')
        win.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")
        win.resizable(False, False)
        win.attributes('-topmost', True)
        tip = random.choice(tips)
        bg = random.choice(bg_colors)
        tk.Label(win, text=tip, bg=bg, font=('微软雅黑', 13), width=22, height=2).pack()
        all_windows.append(win)
        root.update()
        time.sleep(0.015)

    def move_to_heart():
        for step in range(36):
            finished = True
            for i, win in enumerate(all_windows):
                cur_geo = win.geometry()
                cur_pos = cur_geo.split('+')[1:]
                x0, y0 = int(cur_pos[0]), int(cur_pos[1])
                xt, yt = points_heart[i]
                dx = xt - x0
                dy = yt - y0
                dist = math.hypot(dx, dy)
                if dist >= 2:
                    move = min(MOVE_STEP, dist)
                    nx = x0 + int(move * dx / dist)
                    ny = y0 + int(move * dy / dist)
                    win.geometry(f"{WINDOW_W}x{WINDOW_H}+{nx}+{ny}")
                    finished = False
                else:
                    win.geometry(f"{WINDOW_W}x{WINDOW_H}+{xt}+{yt}")
            root.update()
            time.sleep(0.0065)
            if finished:
                for i, win in enumerate(all_windows):
                    xt, yt = points_heart[i]
                    win.geometry(f"{WINDOW_W}x{WINDOW_H}+{xt}+{yt}")
                root.update()
                break
        root.after(4300, close_all)

    def close_all():
        for w in all_windows:
            if w.winfo_exists():
                w.destroy()
        root.quit()

    root.after(900, move_to_heart)
    root.mainloop()