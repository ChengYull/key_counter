from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


KEYBOARD_LAYOUT = [
    ("esc", 20, 20, 48, 42, "Esc"), ("f1", 85, 20, 42, 42, "F1"), ("f2", 130, 20, 42, 42, "F2"),
    ("f3", 175, 20, 42, 42, "F3"), ("f4", 220, 20, 42, 42, "F4"), ("f5", 275, 20, 42, 42, "F5"),
    ("f6", 320, 20, 42, 42, "F6"), ("f7", 365, 20, 42, 42, "F7"), ("f8", 410, 20, 42, 42, "F8"),
    ("f9", 465, 20, 42, 42, "F9"), ("f10", 510, 20, 42, 42, "F10"), ("f11", 555, 20, 42, 42, "F11"),
    ("f12", 600, 20, 42, 42, "F12"), ("delete", 655, 20, 55, 42, "Del"),
    ("`", 20, 75, 42, 42, "`"), ("1", 68, 75, 42, 42, "1"), ("2", 115, 75, 42, 42, "2"),
    ("3", 162, 75, 42, 42, "3"), ("4", 209, 75, 42, 42, "4"), ("5", 256, 75, 42, 42, "5"),
    ("6", 303, 75, 42, 42, "6"), ("7", 350, 75, 42, 42, "7"), ("8", 397, 75, 42, 42, "8"),
    ("9", 444, 75, 42, 42, "9"), ("0", 491, 75, 42, 42, "0"), ("-", 538, 75, 42, 42, "-"),
    ("=", 585, 75, 42, 42, "="), ("backspace", 632, 75, 78, 42, "←"),
    ("tab", 20, 125, 62, 42, "Tab"), ("q", 88, 125, 42, 42, "Q"), ("w", 135, 125, 42, 42, "W"),
    ("e", 182, 125, 42, 42, "E"), ("r", 229, 125, 42, 42, "R"), ("t", 276, 125, 42, 42, "T"),
    ("y", 323, 125, 42, 42, "Y"), ("u", 370, 125, 42, 42, "U"), ("i", 417, 125, 42, 42, "I"),
    ("o", 464, 125, 42, 42, "O"), ("p", 511, 125, 42, 42, "P"), ("[", 558, 125, 42, 42, "["),
    ("]", 605, 125, 42, 42, "]"), ("\\", 652, 125, 58, 42, "\\"),
    ("caps_lock", 20, 175, 72, 42, "Caps"), ("a", 98, 175, 42, 42, "A"), ("s", 145, 175, 42, 42, "S"),
    ("d", 192, 175, 42, 42, "D"), ("f", 239, 175, 42, 42, "F"), ("g", 286, 175, 42, 42, "G"),
    ("h", 333, 175, 42, 42, "H"), ("j", 380, 175, 42, 42, "J"), ("k", 427, 175, 42, 42, "K"),
    ("l", 474, 175, 42, 42, "L"), (";", 521, 175, 42, 42, ";"), ("'", 568, 175, 42, 42, "'"),
    ("enter", 615, 175, 95, 42, "Enter"),
    ("shift", 20, 225, 92, 42, "Shift"), ("z", 118, 225, 42, 42, "Z"), ("x", 165, 225, 42, 42, "X"),
    ("c", 212, 225, 42, 42, "C"), ("v", 259, 225, 42, 42, "V"), ("b", 306, 225, 42, 42, "B"),
    ("n", 353, 225, 42, 42, "N"), ("m", 400, 225, 42, 42, "M"), (",", 447, 225, 42, 42, ","),
    (".", 494, 225, 42, 42, "."), ("/", 541, 225, 42, 42, "/"), ("shift_r", 588, 225, 122, 42, "Shift"),
    ("ctrl_l", 20, 275, 55, 42, "Ctrl"), ("cmd", 80, 275, 55, 42, "Win"),
    ("alt_l", 140, 275, 55, 42, "Alt"), ("space", 200, 275, 220, 42, "空格"),
    ("alt_gr", 425, 275, 55, 42, "Alt"), ("ctrl_r", 485, 275, 55, 42, "Ctrl"),
    ("left", 555, 275, 42, 42, "←"), ("up", 602, 275, 42, 42, "↑"),
    ("down", 602, 320, 42, 42, "↓"), ("right", 649, 275, 42, 42, "→"),
]


class KeyboardHeatmap(QWidget):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats
        self.scale_factor = 1.0
        self.base_width = 840
        self.base_height = 400
        self.is_pinned = True

        self.setWindowTitle(f"键盘热力图 - {self.stats.current_date}")
        self.setFixedSize(int(self.base_width * self.scale_factor), int(self.base_height * self.scale_factor))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
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

        self.pin_btn = QPushButton("📌", self)
        self.pin_btn.setToolTip("钉在桌面（切换置顶）")
        self.pin_btn.setStyleSheet(style)
        self.pin_btn.clicked.connect(self.toggle_pin)

        self.close_btn = QPushButton("×", self)
        self.close_btn.setToolTip("关闭")
        self.close_btn.setStyleSheet(style + "QPushButton:hover { background: #e81123; }")
        self.close_btn.clicked.connect(self.close)

    def update_button_positions(self):
        btn_size = int(38 * self.scale_factor)
        btn_y = int(12 * self.scale_factor)
        spacing = int(4 * self.scale_factor)

        self.pin_btn.setFixedSize(btn_size, btn_size)
        self.close_btn.setFixedSize(btn_size, btn_size)

        w = self.width()
        self.close_btn.move(w - btn_size - spacing, btn_y)
        self.pin_btn.move(w - btn_size * 2 - spacing * 2, btn_y)

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
                    self.close_btn.geometry().contains(event.pos())):
                self.dragging = True
                self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragging') and self.dragging:
            self.move(self.mapToGlobal(event.position().toPoint() - self.offset))

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(15, 15, 25, 215))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 16, 16)

        painter.save()
        painter.scale(self.scale_factor, self.scale_factor)

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
            painter.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
            painter.drawText(QRect(x, y, w, h), Qt.AlignmentFlag.AlignCenter, label)

            if count > 0:
                painter.setPen(QColor(255, 255, 100))
                painter.setFont(QFont("Microsoft YaHei", 8))
                painter.drawText(x + 6, y + 15, str(count))

        painter.restore()

        total = sum(self.stats.keyboard_counts.values())
        painter.setPen(QColor(230, 230, 230))
        painter.setFont(QFont("Microsoft YaHei", 12))
        painter.drawText(35, self.height() - 25,
            f"{self.stats.current_date}  |  总按键次数：{total:,} 次   |   缩放 {self.scale_factor:.1f}x")