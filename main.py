import sys
import threading
from PyQt6.QtWidgets import QApplication

from src.stats_manager import StatsManager
from src.heatmap import KeyboardHeatmap
from src.listeners import start_listeners
from src.icon import generate_keyboard_icon


# 全局保存托盘实例防止被垃圾回收
_tray_instance = None


if __name__ == "__main__":
    generate_keyboard_icon()

    stats = StatsManager()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = KeyboardHeatmap(stats)

    from src.tray import SystemTray
    _tray_instance = SystemTray(window, stats)

    # 禁止最后一个窗口关闭时退出程序（托盘程序需要）
    app.setQuitOnLastWindowClosed(False)

    window.show()

    threading.Timer(0.5, lambda: threading.Thread(target=start_listeners, args=(stats,), daemon=True).start()).start()

    print("✅ 键盘热力图已启动！（已按日期独立保存，每天数据独立）")
    print("   数据保存在 keymouse_stats.json（历史所有日期都在里面）")
    print("   关闭窗口将隐藏到系统托盘，右键托盘图标退出程序")
    sys.exit(app.exec())