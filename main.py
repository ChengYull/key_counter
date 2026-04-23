import sys
import threading
from PyQt6.QtWidgets import QApplication

from src.stats_manager import StatsManager
from src.heatmap import KeyboardHeatmap
from src.listeners import start_listeners


if __name__ == "__main__":
    stats = StatsManager()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = KeyboardHeatmap(stats)
    window.show()

    threading.Timer(0.5, lambda: threading.Thread(target=start_listeners, args=(stats,), daemon=True).start()).start()

    print("✅ 键盘热力图已启动！（已按日期独立保存，每天数据独立）")
    print("   数据保存在 keymouse_stats.json（历史所有日期都在里面）")
    sys.exit(app.exec())