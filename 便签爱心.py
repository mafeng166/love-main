import tkinter as tk
import random
import threading
import time
import math
import ctypes

close_event = threading.Event()
SCREEN_W, SCREEN_H = 0, 0


def show_warn_tip(x, y, window_width=250, window_height=60):
    # 创建窗口
    window = tk.Tk()
    
    # 设置窗口标题和大小位置
    window.title('温馨提示')
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 提示文字列表
    tips = ['多喝水哦~', '保持微笑呀', '每天都要元气满满', '记得吃水果', '保持好心情', '好好爱自己', '我想你了', 
            '梦想成真', '期待下一次见面', '天冷了，多穿衣服', '愿所有烦恼都消失', '保持微笑呀', '别熬夜','爱你哦~']
    
    tip = random.choice(tips)
    
    # 多样的背景颜色
    bg_colors = ['lightpink', 'skyblue', 'lightgreen', 'lavender', 'lightyellow', 'plum', 'coral', 'bisque', 
                 'aquamarine', 'mistyrose', 'honeydew']
    bg = random.choice(bg_colors)
    
    # 创建标签并显示文字
    tk.Label(window, text=tip, bg=bg, font=('微软雅黑', 16), width=30, height=3).pack()
    
    # 窗口置顶显示
    window.attributes('-topmost', True)
    
    # 仅监听统一关闭事件，不做位置更新
    def poll_close():
        if close_event.is_set():
            window.destroy()
            return
        window.after(200, poll_close)

    window.after(200, poll_close)
    
    window.mainloop()


def get_screen_size():
    # 使用 Win32 API 获取屏幕尺寸，避免在子线程里依赖 Tk
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


def generate_heart_points(num_points, window_width, window_height):
    # 经典爱心参数方程（笛卡尔心形曲线）
    # x = 16 sin^3 t
    # y = 13 cos t - 5 cos 2t - 2 cos 3t - cos 4t
    # 先生成标准心形，再缩放平移到屏幕中居中显示
    screen_w, screen_h = get_screen_size()

    # 预留边距，确保窗口完全可见
    margin_x = max(20, window_width // 2)
    margin_y = max(20, window_height // 2)
    usable_w = max(1, screen_w - 2 * margin_x - window_width)
    usable_h = max(1, screen_h - 2 * margin_y - window_height)

    # 采样参数 t
    points = []
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        x0 = 16 * math.sin(t) ** 3
        y0 = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        points.append((x0, y0))

    # 归一化到 [0,1] 再映射到屏幕可用区域
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(1e-6, max_x - min_x)
    span_y = max(1e-6, max_y - min_y)

    mapped = []
    for x0, y0 in points:
        nx = (x0 - min_x) / span_x
        ny = (y0 - min_y) / span_y
        # y 轴屏幕向下为正，曲线向上为正，故需翻转 y
        px = int(margin_x + nx * usable_w)
        py = int(margin_y + (1 - ny) * usable_h)
        # 左上角坐标需减去半个窗口以更贴合轮廓中心
        px = max(0, min(px, screen_w - window_width))
        py = max(0, min(py, screen_h - window_height))
        mapped.append((px, py))

    # 去重（防止整数化后重叠过多）
    dedup = []
    seen = set()
    for p in mapped:
        if p not in seen:
            seen.add(p)
            dedup.append(p)
    return dedup

if __name__ == "__main__":
    # 统一窗口尺寸
    WINDOW_W = 250
    WINDOW_H = 60

    # 生成爱心上的坐标点
    # 初始化屏幕尺寸（供移动边界使用）
    SCREEN_W, SCREEN_H = get_screen_size()

    desired_points = 160  # 略减点数，便于阅读
    points = generate_heart_points(desired_points, WINDOW_W, WINDOW_H)

    # 去除所有动效，不启动任何位移/缩放线程

    # 创建线程列表
    threads = []
    for (x, y) in points:
        t = threading.Thread(target=show_warn_tip, args=(x, y, WINDOW_W, WINDOW_H))
        threads.append(t)
        t.start()
        time.sleep(0.12)  # 放慢节奏，确保能看清文字

    # 所有弹窗都已创建，等待一段时间供阅读后统一关闭
    hold_seconds = 12  # 可调：全部出现后再停留的秒数
    time.sleep(hold_seconds)
    close_event.set()