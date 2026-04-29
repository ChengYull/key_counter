from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os
import sys


def get_asset_path(filename):
    """获取资源文件路径，支持打包后的 exe"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, 'assets', filename)


# 键盘布局 - 优化宽度，填充右侧空白，调整鼠标和按钮位置
KEYBOARD_LAYOUT = [
    # 功能键行
    ("esc", 20, 20, 48, 42, "Esc"), ("f1", 85, 20, 42, 42, "F1"), ("f2", 130, 20, 42, 42, "F2"),
    ("f3", 175, 20, 42, 42, "F3"), ("f4", 220, 20, 42, 42, "F4"), ("f5", 275, 20, 42, 42, "F5"),
    ("f6", 320, 20, 42, 42, "F6"), ("f7", 365, 20, 42, 42, "F7"), ("f8", 410, 20, 42, 42, "F8"),
    ("f9", 465, 20, 42, 42, "F9"), ("f10", 510, 20, 42, 42, "F10"), ("f11", 555, 20, 42, 42, "F11"),
    ("f12", 600, 20, 42, 42, "F12"), ("delete", 655, 20, 42, 42, "Del"),
    # 数字行
    ("`", 20, 75, 42, 42, "`"), ("1", 68, 75, 42, 42, "1"), ("2", 115, 75, 42, 42, "2"),
    ("3", 162, 75, 42, 42, "3"), ("4", 209, 75, 42, 42, "4"), ("5", 256, 75, 42, 42, "5"),
    ("6", 303, 75, 42, 42, "6"), ("7", 350, 75, 42, 42, "7"), ("8", 397, 75, 42, 42, "8"),
    ("9", 444, 75, 42, 42, "9"), ("0", 491, 75, 42, 42, "0"), ("-", 538, 75, 42, 42, "-"),
    ("=", 585, 75, 42, 42, "="), ("backspace", 632, 75, 65, 42, "←"),
    # QWER行
    ("tab", 20, 125, 62, 42, "Tab"), ("q", 88, 125, 42, 42, "Q"), ("w", 135, 125, 42, 42, "W"),
    ("e", 182, 125, 42, 42, "E"), ("r", 229, 125, 42, 42, "R"), ("t", 276, 125, 42, 42, "T"),
    ("y", 323, 125, 42, 42, "Y"), ("u", 370, 125, 42, 42, "U"), ("i", 417, 125, 42, 42, "I"),
    ("o", 464, 125, 42, 42, "O"), ("p", 511, 125, 42, 42, "P"), ("[", 558, 125, 42, 42, "["),
    ("]", 605, 125, 42, 42, "]"), ("\\", 652, 125, 45, 42, "\\"),
    # ASDF行
    ("caps_lock", 20, 175, 72, 42, "Caps"), ("a", 98, 175, 42, 42, "A"), ("s", 145, 175, 42, 42, "S"),
    ("d", 192, 175, 42, 42, "D"), ("f", 242, 175, 42, 42, "F"),("g", 290, 175, 42, 42, "G"),
    ("h", 338, 175, 42, 42, "H"),("j", 385, 175, 42, 42, "J"),("k", 432, 175, 42, 42, "K"),
    ("l", 479, 175, 42, 42, "L"),(";", 526, 175, 42, 42, ";"),("'", 526, 175, 42, 42, "'"),
    ("enter", 573, 175, 115, 42, "Enter"),
    # ZXCV行 - 拉宽右 Shift，调整方向键位置
    ("shift", 20, 225, 72, 42, "Shift"), ("z", 98, 225, 42, 42, "Z"), ("x", 145, 225, 42, 42, "X"),
    ("c", 192, 225, 42, 42, "C"), ("v", 239, 225, 42, 42, "V"), ("b", 286, 225, 42, 42, "B"),
    ("n", 333, 225, 42, 42, "N"), ("m", 380, 225, 42, 42, "M"), (",", 428, 225, 42, 42, ","),
    (".", 472, 225, 42, 42, "."), ("/", 517, 225, 42, 42, "/"), ("shift_r", 561, 225, 79, 42, "Shift"),
    # 方向键 - 倒 T 型，右移避免重叠
    ("up", 645, 225, 42, 42, "↑"),
    # 底部行 - 加宽空格，调整右侧控制键和方向键
    ("ctrl_l", 20, 275, 55, 42, "Ctrl"), ("cmd", 80, 275, 55, 42, "Win"),
    ("alt_l", 140, 275, 55, 42, "Alt"), ("space", 200, 275, 226, 42, "空格"),
    ("alt_gr", 430, 275, 55, 42, "Alt"), ("ctrl_r", 492, 275, 55, 42, "Ctrl"),
    ("left", 555, 275, 42, 42, "←"), ("down", 600, 275, 42, 42, "↓"), ("right", 645, 275, 42, 42, "→"),
]


class KeyboardHeatmap(QWidget):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats
        self.scale_factor = 1.0
        self.base_width = 850
        self.base_height = 350
        self.is_pinned = False
        self.chart_window = None

        self.setWindowTitle(f"键盘热力图 - {self.stats.current_date}")

        icon_path = get_asset_path('keyboard.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setFixedSize(int(self.base_width * self.scale_factor), int(self.base_height * self.scale_factor))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(200)

        self.setup_buttons()
        self.update_button_positions()

    def setup_buttons(self):
        style = """
            QPushButton {
                background: rgba(255,255,255,70);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover { background: rgba(255,70,70,200); }
        """

        self.pin_btn = QPushButton("📍", self)
        self.pin_btn.setToolTip("钉在桌面（切换置顶）")
        self.pin_btn.setStyleSheet(style)
        self.pin_btn.clicked.connect(self.toggle_pin)

        self.close_btn = QPushButton("×", self)
        self.close_btn.setToolTip("关闭")
        self.close_btn.setStyleSheet(style + "QPushButton:hover { background: #e81123; }")
        self.close_btn.clicked.connect(self.close)

        self.chart_btn = QPushButton("📊", self)
        self.chart_btn.setToolTip("统计图表")
        self.chart_btn.setStyleSheet(style)
        self.chart_btn.clicked.connect(self.open_chart)

    def update_button_positions(self):
        btn_size = int(38 * self.scale_factor)
        btn_y = int(12 * self.scale_factor)
        spacing = int(4 * self.scale_factor)

        self.pin_btn.setFixedSize(btn_size, btn_size)
        self.close_btn.setFixedSize(btn_size, btn_size)
        self.chart_btn.setFixedSize(btn_size, btn_size)

        w = self.width()
        self.close_btn.move(w - btn_size - spacing, btn_y)
        self.pin_btn.move(w - btn_size * 2 - spacing * 2, btn_y)
        self.chart_btn.move(w - btn_size * 3 - spacing * 3, btn_y)

    def open_chart(self):
        if self.chart_window is None or not self.chart_window.isVisible():
            from src.stats_chart import StatsChartWindow
            self.chart_window = StatsChartWindow(self.stats)
        self.chart_window.show()
        self.chart_window.activateWindow()

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.is_pinned)
        self.pin_btn.setText("📌" if self.is_pinned else "📍")
        self.show()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        old_scale = self.scale_factor
        if delta > 0:
            self.scale_factor = min(2.0, self.scale_factor + 0.12)
        else:
            self.scale_factor = max(0.65, self.scale_factor - 0.12)

        if abs(self.scale_factor - old_scale) > 0.01:
            new_w = int(self.base_width * self.scale_factor)
            new_h = int(self.base_height * self.scale_factor)
            self.setFixedSize(new_w, new_h)
            self.update_button_positions()
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not (self.pin_btn.geometry().contains(event.pos()) or
                    self.close_btn.geometry().contains(event.pos()) or
                    self.chart_btn.geometry().contains(event.pos())):
                self.dragging = True
                self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragging') and self.dragging:
            self.move(self.mapToGlobal(event.position().toPoint() - self.offset))

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(15, 15, 25, 215))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 16, 16)

        painter.save()
        painter.scale(self.scale_factor, self.scale_factor)

        # 绘制键盘热力图
        self._paint_keyboard(painter)

        # 绘制鼠标热力图
        self._paint_mouse(painter)

        painter.restore()

        # 底部统计信息
        keyboard_total = sum(self.stats.keyboard_counts.values())
        mouse_click_total = sum(v for k, v in self.stats.mouse_counts.items() if k != "move_distance")
        move_distance = self.stats.get_total_move_distance()
        move_meters = move_distance * 26 / 100000  # 1000px ≈ 26cm = 0.026m
        font_size = max(9, int(12 * self.scale_factor))
        painter.setPen(QColor(230, 230, 230))
        painter.setFont(QFont("Microsoft YaHei", font_size))
        painter.drawText(35, self.height() - 12,
            f"{self.stats.current_date}  |  键盘: {keyboard_total:,}  鼠标: {mouse_click_total:,}  移动: {move_distance:,}px ({move_meters:.2f}m)  |  {self.scale_factor:.1f}x")

    def _paint_keyboard(self, painter):
        max_count = max(self.stats.keyboard_counts.values(), default=1)

        for key_name, x, y, w, h, label in KEYBOARD_LAYOUT:
            count = self.stats.keyboard_counts.get(key_name.lower(), 0)
            if count == 0:
                color = QColor(255, 255, 255)
            else:
                intensity = min(count / max_count, 1.0)
                gb = int(255 * (1 - intensity * 0.93))
                color = QColor(255, gb, gb)

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(50, 50, 50), 2))
            painter.drawRoundedRect(x, y, w, h, 8, 8)

            text_color = QColor(255, 255, 255) if count > max_count * 0.4 else QColor(30, 30, 30)
            painter.setPen(text_color)
            font_size = max(8, int(9 * self.scale_factor))
            painter.setFont(QFont("Microsoft YaHei", font_size, QFont.Weight.Bold))
            painter.drawText(QRect(x, y, w, h), Qt.AlignmentFlag.AlignCenter, label)

            if count > 0:
                count_font_size = max(7, int(8 * self.scale_factor))
                painter.setPen(QColor(255, 255, 100))
                painter.setFont(QFont("Microsoft YaHei", count_font_size))
                painter.drawText(x + 6, y + 15, str(count))

    def _paint_mouse(self, painter):
        """绘制鼠标热力图 - 放在键盘右侧，与操作栏对齐"""
        mouse_counts = self.stats.mouse_counts
        max_count = max(mouse_counts.values(), default=1)

        # 鼠标起始位置（根据新的宽度调整，为右侧按钮留出空间）
        start_x = 720
        start_y = 150

        # 鼠标外壳
        body_w, body_h = 100, 150
        painter.setBrush(QColor(50, 50, 60, 200))
        painter.setPen(QPen(QColor(90, 90, 100), 2))
        painter.drawRoundedRect(start_x, start_y, body_w, body_h, 12, 12)

        # 滚轮
        wheel_x = start_x + 48
        wheel_y = start_y + 15
        wheel_w, wheel_h = 4, 30

        painter.drawRoundedRect(wheel_x, wheel_y, wheel_w, wheel_h, 2, 2)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Microsoft YaHei", 7, QFont.Weight.Bold))
        painter.drawText(QRect(wheel_x, wheel_y, wheel_w, wheel_h), Qt.AlignmentFlag.AlignCenter, "M")

        # 左键
        left_x = start_x + 5
        left_y = start_y + 5
        left_w, left_h = 40, 55
        count = mouse_counts.get("left", 0)
        if count == 0:
            color = QColor(70, 70, 80)
        else:
            intensity = min(count / max_count, 1.0)
            gb = int(90 * (1 - intensity * 0.8))
            color = QColor(255, gb, gb)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(40, 40, 50), 1))
        painter.drawRoundedRect(left_x, left_y, left_w, left_h, 2, 2)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Microsoft YaHei", 7, QFont.Weight.Bold))
        painter.drawText(QRect(left_x, left_y, left_w, left_h), Qt.AlignmentFlag.AlignCenter, "L")
        if count > 0:
            painter.setPen(QColor(255, 255, 100))
            painter.drawText(left_x + 1, left_y + 10, str(count))

        # 右键
        right_x = start_x + 55
        right_y = start_y + 5
        right_w, right_h = 40, 55
        count = mouse_counts.get("right", 0)
        if count == 0:
            color = QColor(70, 70, 80)
        else:
            intensity = min(count / max_count, 1.0)
            gb = int(90 * (1 - intensity * 0.8))
            color = QColor(255, gb, gb)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(40, 40, 50), 1))
        painter.drawRoundedRect(right_x, right_y, right_w, right_h, 2, 2)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Microsoft YaHei", 7, QFont.Weight.Bold))
        painter.drawText(QRect(right_x, right_y, right_w, right_h), Qt.AlignmentFlag.AlignCenter, "R")
        if count > 0:
            painter.setPen(QColor(255, 255, 100))
            painter.drawText(right_x + 1, right_y + 10, str(count))