import os
import sys
import winreg
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt


def get_asset_path(filename):
    """获取资源文件路径，支持打包后的 exe"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, 'assets', filename)


def get_exe_path():
    """获取程序路径"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))


def is_auto_start_enabled():
    """检查是否已开启开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "KeyCounter")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def set_auto_start(enable: bool):
    """设置开机自启"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_WRITE)
        if enable:
            winreg.SetValueEx(key, "KeyCounter", 0, winreg.REG_SZ, get_exe_path())
            print(f"[DEBUG] 已开启开机自启: {get_exe_path()}")
        else:
            try:
                winreg.DeleteValue(key, "KeyCounter")
                print("[DEBUG] 已关闭开机自启")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[DEBUG] 设置开机自启失败: {e}")
        return False


class SystemTray:
    def __init__(self, window, stats):
        self.window = window
        self.stats = stats

        icon_path = get_asset_path('keyboard.ico')
        print(f"[DEBUG] 托盘图标路径: {icon_path}")
        print(f"[DEBUG] 图标是否存在: {os.path.exists(icon_path)}")

        if os.path.exists(icon_path):
            self.icon = QIcon(icon_path)
            print(f"[DEBUG] 图标加载成功")
        else:
            print(f"[DEBUG] 图标不存在，使用默认图标")
            self.icon = self.window.style().standardIcon(
                self.window.style().StandardPixmap.SP_ComputerIcon
            )

        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip("键盘热力图 - 按键统计")

        self.setup_menu()
        self.tray.show()
        self.tray.setVisible(True)
        print(f"[DEBUG] 托盘已显示, isSystemTrayAvailable: {QSystemTrayIcon.isSystemTrayAvailable()}, supportsMessages: {self.tray.supportsMessages()}")

        # 左键点击切换显示/隐藏
        self.tray.activated.connect(self.on_tray_activated)

    def setup_menu(self):
        self.menu = QMenu()

        # 所有action都保持为实例变量引用
        self.action_toggle_visible = QAction("隐藏窗口" if self.window.isVisible() else "显示窗口")
        self.action_toggle_visible.triggered.connect(self.toggle_visible)
        self.menu.addAction(self.action_toggle_visible)

        self.action_toggle_pin = QAction("取消置顶" if self.window.is_pinned else "置顶窗口")
        self.action_toggle_pin.triggered.connect(self.toggle_pin)
        self.menu.addAction(self.action_toggle_pin)

        self.menu.addSeparator()

        self.action_stats = QAction("今日统计")
        self.action_stats.triggered.connect(self.show_stats)
        self.menu.addAction(self.action_stats)

        self.menu.addSeparator()

        # 开机自启菜单项
        auto_start_enabled = is_auto_start_enabled()
        self.action_auto_start = QAction("开机自启: 开启" if auto_start_enabled else "开机自启: 关闭")
        self.action_auto_start.triggered.connect(self.toggle_auto_start)
        self.menu.addAction(self.action_auto_start)

        self.menu.addSeparator()

        self.action_quit = QAction("退出")
        self.action_quit.triggered.connect(self.quit)
        self.menu.addAction(self.action_quit)

        print(f"[DEBUG] 菜单项数量: {len(self.menu.actions())}")
        for i, a in enumerate(self.menu.actions()):
            print(f"[DEBUG] 菜单项{i}: {a.text()}")

        self.tray.setContextMenu(self.menu)

    def update_menu_texts(self):
        self.action_toggle_visible.setText("隐藏窗口" if self.window.isVisible() else "显示窗口")
        self.action_toggle_pin.setText("取消置顶" if self.window.is_pinned else "置顶窗口")
        self.action_auto_start.setText("开机自启: 开启" if is_auto_start_enabled() else "开机自启: 关闭")

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visible()

    def toggle_visible(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()
        self.update_menu_texts()

    def toggle_pin(self):
        self.window.toggle_pin()
        self.update_menu_texts()

    def toggle_auto_start(self):
        current = is_auto_start_enabled()
        if set_auto_start(not current):
            self.action_auto_start.setText("开机自启: 开启" if not current else "开机自启: 关闭")
            print(f"[DEBUG] 开机自启已切换为: {'开启' if not current else '关闭'}")

    def show_stats(self):
        total = sum(self.stats.keyboard_counts.values())
        top_keys = sorted(self.stats.keyboard_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        msg = f"📊 {self.stats.current_date} 统计\n\n总按键次数: {total:,}\n\nTop 5 按键:\n"
        for key, count in top_keys:
            msg += f"  {key}: {count:,}\n"

        print(f"[DEBUG] show_stats 被调用，消息: {msg}")
        # 使用 window 作为父窗口，避免关闭弹窗时程序退出
        msg_box = QMessageBox(self.window)
        msg_box.setWindowTitle("键盘热力图 - 今日统计")
        msg_box.setText(msg.strip())
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def quit(self):
        self.window.show()  # 先显示窗口以便正常关闭
        self.window.close()
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().quit()