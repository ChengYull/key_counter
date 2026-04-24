import datetime
import os
from io import StringIO
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
    matplotlib.rcParams['axes.unicode_minus'] = False
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class StatsChartWindow(QWidget):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats
        self.setWindowTitle("键盘热力图 - 统计图表")
        self.setFixedSize(1000, 600)
        self._init_ui()
        self._init_chart()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar = QHBoxLayout()

        # 图表类型选择
        self.chart_type_label = QLabel("图表类型:")
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["分时统计", "每日统计", "移动统计"])
        self.chart_type_combo.currentIndexChanged.connect(self.on_chart_type_changed)
        self.current_tab = "hourly"

        toolbar.addWidget(self.chart_type_label)
        toolbar.addWidget(self.chart_type_combo)
        toolbar.addStretch()

        # 时间范围选择（分时统计用）
        self.time_range_widget = QWidget()
        time_range_layout = QHBoxLayout(self.time_range_widget)
        time_range_layout.setContentsMargins(0, 0, 0, 0)
        time_range_layout.addWidget(QLabel("时间范围:"))
        self.start_hour_combo = QComboBox()
        for h in range(24):
            self.start_hour_combo.addItem(f"{h:02d}:00")
        self.start_hour_combo.setCurrentText("08:00")
        self.start_hour_combo.currentTextChanged.connect(self.on_time_range_changed)
        time_range_layout.addWidget(self.start_hour_combo)
        time_range_layout.addWidget(QLabel("-"))
        self.end_hour_combo = QComboBox()
        for h in range(24):
            self.end_hour_combo.addItem(f"{h:02d}:00")
        self.end_hour_combo.setCurrentText("18:00")
        self.end_hour_combo.currentTextChanged.connect(self.on_time_range_changed)
        time_range_layout.addWidget(self.end_hour_combo)
        toolbar.addWidget(self.time_range_widget)

        # 日期选择
        toolbar.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self.on_date_changed)
        toolbar.addWidget(self.date_edit)

        # 范围选择（每日统计用）
        self.range_label = QLabel("范围:")
        self.range_combo = QComboBox()
        self.range_combo.addItems(["最近7天", "最近30天", "自定义"])
        self.range_combo.currentTextChanged.connect(self.on_range_changed)
        toolbar.addWidget(self.range_label)
        toolbar.addWidget(self.range_combo)

        # 自定义日期范围
        self.start_label = QLabel("从:")
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.end_label = QLabel("到:")
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.custom_range_widget = QWidget()
        custom_layout = QHBoxLayout(self.custom_range_widget)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.addWidget(self.start_label)
        custom_layout.addWidget(self.start_date)
        custom_layout.addWidget(self.end_label)
        custom_layout.addWidget(self.end_date)
        self.custom_range_widget.setVisible(False)
        toolbar.addWidget(self.custom_range_widget)

        # 导出按钮
        export_btn = QPushButton("导出CSV")
        export_btn.clicked.connect(self.export_csv)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        # 图表区域
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)
        layout.addWidget(self.chart_widget)

    def _init_chart(self):
        if not HAS_MATPLOTLIB:
            no_lib_label = QLabel("需要安装 matplotlib 才能显示图表:\npip install matplotlib")
            no_lib_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chart_layout.addWidget(no_lib_label)
            return

        # 分时图表（按键）
        self.hourly_figure = Figure(figsize=(12, 5))
        self.hourly_canvas = FigureCanvas(self.hourly_figure)
        self.hourly_ax = self.hourly_figure.add_subplot(111)

        # 每日图表
        self.daily_figure = Figure(figsize=(12, 5))
        self.daily_canvas = FigureCanvas(self.daily_figure)
        self.daily_ax = self.daily_figure.add_subplot(111)

        # 移动统计图表
        self.move_figure = Figure(figsize=(12, 5))
        self.move_canvas = FigureCanvas(self.move_figure)
        self.move_ax = self.move_figure.add_subplot(111)

        self.chart_layout.addWidget(self.hourly_canvas)
        self.chart_layout.addWidget(self.daily_canvas)
        self.chart_layout.addWidget(self.move_canvas)
        self.daily_canvas.setVisible(False)
        self.move_canvas.setVisible(False)

        self.update_hourly_chart()
        self.update_daily_chart()
        self.update_move_chart()
        self.show_tab("hourly")

    def on_chart_type_changed(self, index):
        tabs = ["hourly", "daily", "move"]
        self.show_tab(tabs[index])

    def show_tab(self, tab):
        self.current_tab = tab
        self.hourly_canvas.setVisible(tab == "hourly")
        self.daily_canvas.setVisible(tab == "daily")
        self.move_canvas.setVisible(tab == "move")

        # 显示/隐藏控件
        self.time_range_widget.setVisible(tab in ("hourly", "move"))
        self.date_edit.setVisible(True)
        self.range_label.setVisible(tab == "daily")
        self.range_combo.setVisible(tab == "daily")
        self.custom_range_widget.setVisible(False)

        if tab == "hourly":
            self.update_hourly_chart()
        elif tab == "daily":
            self.update_daily_chart()
        else:
            self.update_move_chart()

    def on_date_changed(self):
        if self.current_tab == "hourly":
            self.update_hourly_chart()
        elif self.current_tab == "move":
            self.update_move_chart()

    def on_time_range_changed(self):
        self.update_hourly_chart()

    def on_range_changed(self, text):
        self.update_range_visibility()
        self.update_daily_chart()

    def update_range_visibility(self):
        self.custom_range_widget.setVisible(self.range_combo.currentText() == "自定义")

    def update_hourly_chart(self):
        if not HAS_MATPLOTLIB:
            return

        date_str = self.date_edit.date().toString(Qt.DateFormat.ISODate)
        data = self.stats.get_minute_stats(date_str)
        minutes = data.get("minutes", [0] * 1440)

        start_hour = self.start_hour_combo.currentIndex()
        end_hour = self.end_hour_combo.currentIndex()
        if end_hour <= start_hour:
            end_hour = start_hour + 1

        start_minute = start_hour * 60
        end_minute = end_hour * 60

        self.hourly_ax.clear()
        x = list(range(start_minute, end_minute))
        y = minutes[start_minute:end_minute]
        self.hourly_ax.plot(x, y, linewidth=0.5, alpha=0.8)
        self.hourly_ax.fill_between(x, y, alpha=0.3)
        self.hourly_ax.set_title(f"{date_str} {start_hour:02d}:00-{end_hour:02d}:00 Every Minute")
        self.hourly_ax.set_xlabel("Time (minute)")
        self.hourly_ax.set_ylabel("Key Count")
        self.hourly_ax.grid(True, alpha=0.3)

        hour_range = end_hour - start_hour
        if hour_range <= 4:
            tick_step = 1
        elif hour_range <= 8:
            tick_step = 2
        else:
            tick_step = 4

        hour_positions = [h * 60 for h in range(start_hour, end_hour + 1, tick_step)]
        hour_labels = [f"{h:02d}:00" for h in range(start_hour, end_hour + 1, tick_step)]
        self.hourly_ax.set_xticks(hour_positions)
        self.hourly_ax.set_xticklabels(hour_labels, rotation=45)
        self.hourly_figure.tight_layout()
        self.hourly_canvas.draw()

    def update_daily_chart(self):
        if not HAS_MATPLOTLIB:
            return

        text = self.range_combo.currentText()
        today = datetime.date.today()

        if text == "最近7天":
            end = today.isoformat()
            start = (today - datetime.timedelta(days=6)).isoformat()
        elif text == "最近30天":
            end = today.isoformat()
            start = (today - datetime.timedelta(days=29)).isoformat()
        else:
            start = self.start_date.date().toString(Qt.DateFormat.ISODate)
            end = self.end_date.date().toString(Qt.DateFormat.ISODate)

        daily_data = self.stats.get_daily_totals(start, end)

        self.daily_ax.clear()
        dates = [d["date"] for d in daily_data]
        totals = [d["total"] for d in daily_data]

        self.daily_ax.bar(range(len(dates)), totals, alpha=0.7)
        self.daily_ax.plot(range(len(dates)), totals, marker='o', color='red', linewidth=2, markersize=4)
        self.daily_ax.set_title(f"{start} to {end} Daily Key Count")
        self.daily_ax.set_xlabel("Date")
        self.daily_ax.set_ylabel("Key Count")
        self.daily_ax.grid(True, alpha=0.3, axis='y')

        if len(dates) > 10:
            tick_step = len(dates) // 7
            tick_labels = [dates[i] if i % tick_step == 0 else "" for i in range(len(dates))]
            self.daily_ax.set_xticks(range(len(dates)))
            self.daily_ax.set_xticklabels(tick_labels, rotation=45)
        else:
            self.daily_ax.set_xticks(range(len(dates)))
            self.daily_ax.set_xticklabels(dates, rotation=45)

        self.daily_figure.tight_layout()
        self.daily_canvas.draw()

    def update_move_chart(self):
        if not HAS_MATPLOTLIB:
            return

        date_str = self.date_edit.date().toString(Qt.DateFormat.ISODate)
        data = self.stats.get_minute_stats(date_str)
        minute_distance = data.get("minute_distance", [0] * 1440)

        # 获取时间范围
        start_hour = self.start_hour_combo.currentIndex()
        end_hour = self.end_hour_combo.currentIndex()
        if end_hour <= start_hour:
            end_hour = start_hour + 1

        start_minute = start_hour * 60
        end_minute = end_hour * 60

        self.move_ax.clear()
        x = list(range(start_minute, end_minute))
        y = minute_distance[start_minute:end_minute]
        self.move_ax.plot(x, y, linewidth=0.5, alpha=0.8, color='green')
        self.move_ax.fill_between(x, y, alpha=0.3, color='green')
        self.move_ax.set_title(f"{date_str} {start_hour:02d}:00-{end_hour:02d}:00 Mouse Move Distance")
        self.move_ax.set_xlabel("Time (minute)")
        self.move_ax.set_ylabel("Distance (pixels)")
        self.move_ax.grid(True, alpha=0.3)

        hour_range = end_hour - start_hour
        if hour_range <= 4:
            tick_step = 1
        elif hour_range <= 8:
            tick_step = 2
        else:
            tick_step = 4

        hour_positions = [h * 60 for h in range(start_hour, end_hour + 1, tick_step)]
        hour_labels = [f"{h:02d}:00" for h in range(start_hour, end_hour + 1, tick_step)]
        self.move_ax.set_xticks(hour_positions)
        self.move_ax.set_xticklabels(hour_labels, rotation=45)
        self.move_figure.tight_layout()
        self.move_canvas.draw()

    def export_csv(self):
        if self.current_tab == "hourly":
            date_str = self.date_edit.date().toString(Qt.DateFormat.ISODate)
            data = self.stats.get_minute_stats(date_str)
            minutes = data.get("minutes", [0] * 1440)

            start_hour = self.start_hour_combo.currentIndex()
            end_hour = self.end_hour_combo.currentIndex()
            if end_hour <= start_hour:
                end_hour = start_hour + 1

            lines = ["时间,按键次数"]
            for m in range(start_hour * 60, end_hour * 60):
                hour = m // 60
                minute = m % 60
                lines.append(f"{hour:02d}:{minute:02d},{minutes[m]}")
            filename = f"minute_stats_{date_str}_{start_hour:02d}_{end_hour:02d}.csv"
        elif self.current_tab == "daily":
            text = self.range_combo.currentText()
            today = datetime.date.today()

            if text == "最近7天":
                end = today.isoformat()
                start = (today - datetime.timedelta(days=6)).isoformat()
            elif text == "最近30天":
                end = today.isoformat()
                start = (today - datetime.timedelta(days=29)).isoformat()
            else:
                start = self.start_date.date().toString(Qt.DateFormat.ISODate)
                end = self.end_date.date().toString(Qt.DateFormat.ISODate)

            daily_data = self.stats.get_daily_totals(start, end)
            lines = ["日期,按键次数,移动距离"]
            for d in daily_data:
                lines.append(f"{d['date']},{d['total']},{d['total_distance']}")
            filename = f"daily_stats_{start}_to_{end}.csv"
        else:  # move
            date_str = self.date_edit.date().toString(Qt.DateFormat.ISODate)
            data = self.stats.get_minute_stats(date_str)
            minute_distance = data.get("minute_distance", [0] * 1440)

            lines = ["时间,移动距离(像素)"]
            for h in range(24):
                distance = sum(minute_distance[h*60:(h+1)*60])
                lines.append(f"{h:02d}:00,{distance}")
            filename = f"move_stats_{date_str}.csv"

        path, _ = QFileDialog.getSaveFileName(self, "导出CSV", filename, "CSV Files (*.csv)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            QMessageBox.information(self, "导出成功", f"已导出到 {path}")