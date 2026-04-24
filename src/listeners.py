from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse
import math


def start_listeners(stats):
    currently_pressed = set()
    last_mouse_pos = None
    move_sample_counter = 0
    MOVE_SAMPLE_RATE = 5  # 每5次移动事件采样一次，减少开销

    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char:
                kname = key.char.lower()
            else:
                kname = str(key).replace("Key.", "").lower()

            if kname not in currently_pressed:
                currently_pressed.add(kname)
                print(f"按下 → {kname}")

        except Exception as e:
            print("on_press error:", e)

    def on_release(key):
        try:
            if hasattr(key, 'char') and key.char:
                kname = key.char.lower()
            else:
                kname = str(key).replace("Key.", "").lower()

            if kname in currently_pressed:
                currently_pressed.remove(kname)
                print(f"释放 → {kname}  计次+1")
                stats.increment_key(kname)

        except Exception as e:
            print("on_release error:", e)

    def on_move(x, y):
        """鼠标移动事件，使用采样减少开销"""
        nonlocal last_mouse_pos, move_sample_counter
        try:
            if last_mouse_pos is None:
                last_mouse_pos = (x, y)
                return

            # 计算移动距离
            dx = x - last_mouse_pos[0]
            dy = y - last_mouse_pos[1]
            distance = int(math.sqrt(dx * dx + dy * dy))

            # 采样记录，避免过于频繁
            move_sample_counter += 1
            if move_sample_counter >= MOVE_SAMPLE_RATE and distance > 0:
                stats.increment_move_distance(distance)
                move_sample_counter = 0

            last_mouse_pos = (x, y)
        except Exception as e:
            print("on_move error:", e)

    def on_click(x, y, button, pressed):
        if pressed:
            btn_name = str(button).split('.')[-1]
            print(f"鼠标按下: {btn_name}")
            stats.increment_mouse(button)

    keyboard_listener = pynput_keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )

    mouse_listener = pynput_mouse.Listener(
        on_click=on_click,
        on_move=on_move
    )

    keyboard_listener.start()
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()