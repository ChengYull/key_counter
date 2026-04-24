import os
from PIL import Image, ImageDraw


def generate_keyboard_icon():
    """生成键盘图标并保存为 .ico 文件（仅当不存在时）"""
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'keyboard.ico')
    icon_path = os.path.abspath(icon_path)

    if os.path.exists(icon_path):
        print(f"图标已存在: {icon_path}")
        return icon_path

    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 键盘底板 - 深灰圆角矩形
    padding = 20
    corner_radius = 30
    draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding],
        radius=corner_radius,
        fill=(40, 40, 50, 255)
    )

    # 按键布局 - 简化的键盘样式
    key_color = (80, 80, 100, 255)
    key_highlight = (100, 100, 120, 255)

    # 第一行功能键
    keys_row1 = [(40, 35, 70, 55), (80, 35, 110, 55), (120, 35, 150, 55), (160, 35, 190, 55)]

    # 第二行数字键
    keys_row2 = [(40, 65, 70, 95), (80, 65, 110, 95), (120, 65, 150, 95), (160, 65, 190, 95),
                 (200, 65, 230, 95)]

    # 第三行字母键
    keys_row3 = [(40, 95, 70, 125), (80, 95, 110, 125), (120, 95, 150, 125), (160, 95, 190, 125),
                 (200, 95, 230, 125)]

    # 第四行 - 空格键
    space_key = [(80, 155, 180, 175)]

    all_keys = keys_row1 + keys_row2 + keys_row3 + space_key

    for key in all_keys:
        draw.rounded_rectangle(key, radius=6, fill=key_color)
        draw.rounded_rectangle([key[0], key[1], key[2], key[1] + 8], radius=6, fill=key_highlight)

    # 创建多个尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    icons = []
    for s in sizes:
        resized = img.resize((s, s), Image.LANCZOS)
        icons.append(resized)

    # 保存 .ico 文件
    img.save(icon_path, format='ICO', sizes=[(i.size[0], i.size[1]) for i in icons])
    print(f"图标已生成: {icon_path}")
    return icon_path


if __name__ == "__main__":
    generate_keyboard_icon()