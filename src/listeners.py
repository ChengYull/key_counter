from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse


def start_listeners(stats):
    currently_pressed = set()

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
        on_click=on_click
    )

    keyboard_listener.start()
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()