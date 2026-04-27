import datetime
import json
import os
import sys


def get_data_dir():
    """获取数据文件目录（程序所在目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 exe，数据放在 exe 同目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境，数据放在 main.py 同目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StatsManager:
    def __init__(self):
        self.data_dir = get_data_dir()
        self.daily_stats = {}                    # "YYYY-MM-DD": {"keyboard": dict, "mouse": dict}
        self.minute_stats = {}                   # "YYYY-MM-DD": {"minutes": [], "minute_distance": [], "total": int, "total_distance": int}
        self.current_date = datetime.date.today().isoformat()
        self.current_minute = self._get_current_minute()
        self.load()
        self.ensure_today()
        self.ensure_today_minute()

    def _get_current_minute(self):
        """获取当前分钟索引 (0-1439)"""
        now = datetime.datetime.now()
        return now.hour * 60 + now.minute

    def ensure_today(self):
        if self.current_date not in self.daily_stats:
            self.daily_stats[self.current_date] = {"keyboard": {}, "mouse": {}}
        if "move_distance" not in self.daily_stats[self.current_date]["mouse"]:
            self.daily_stats[self.current_date]["mouse"]["move_distance"] = 0
        self.keyboard_counts = self.daily_stats[self.current_date]["keyboard"]
        self.mouse_counts = self.daily_stats[self.current_date]["mouse"]

    def ensure_today_minute(self):
        """确保今日分时统计数据存在"""
        if self.current_date not in self.minute_stats:
            self.minute_stats[self.current_date] = {
                "minutes": [0] * 1440,
                "minute_distance": [0] * 1440,
                "total": 0,
                "total_distance": 0
            }
        self.today_minutes = self.minute_stats[self.current_date]["minutes"]
        self.today_minute_distance = self.minute_stats[self.current_date]["minute_distance"]

    def increment_key(self, key_name: str):
        self.check_date_change()
        self.keyboard_counts[key_name] = self.keyboard_counts.get(key_name, 0) + 1
        self._increment_minute()
        self.save()

    # pynput 鼠标按钮名称映射到热力图按键名称
    MOUSE_BUTTON_MAP = {
        "left": "left",
        "right": "right",
        "middle": "wheel",
        "x1": "side1",
        "x2": "side2",
    }

    def increment_mouse(self, button):
        self.check_date_change()
        btn_str = str(button).split('.')[-1].lower()
        key_name = self.MOUSE_BUTTON_MAP.get(btn_str, btn_str)
        if key_name in ("side1", "side2"):
            return
        self.mouse_counts[key_name] = self.mouse_counts.get(key_name, 0) + 1
        self._increment_minute()
        self.save()

    def increment_move_distance(self, distance: int):
        """增加移动距离（像素）"""
        self.check_date_change()
        self.check_minute_change()
        self.mouse_counts["move_distance"] = self.mouse_counts.get("move_distance", 0) + distance
        self.today_minute_distance[self.current_minute] += distance
        self.minute_stats[self.current_date]["total_distance"] += distance
        self.save()

    def _increment_minute(self):
        """增加当前分钟的计数"""
        self.check_minute_change()
        self.today_minutes[self.current_minute] += 1
        self.minute_stats[self.current_date]["total"] += 1

    def check_date_change(self):
        today = datetime.date.today().isoformat()
        if today != self.current_date:
            self.current_date = today
            self.current_minute = self._get_current_minute()
            self.ensure_today()
            self.ensure_today_minute()

    def check_minute_change(self):
        """检查分钟是否变化"""
        current = self._get_current_minute()
        if current != self.current_minute:
            self.current_minute = current

    def save(self):
        try:
            keymouse_path = os.path.join(self.data_dir, "keymouse_stats.json")
            with open(keymouse_path, "w", encoding="utf-8") as f:
                json.dump(self.daily_stats, f, ensure_ascii=False, indent=2)
        except:
            pass
        try:
            minute_path = os.path.join(self.data_dir, "minute_stats.json")
            with open(minute_path, "w", encoding="utf-8") as f:
                json.dump(self.minute_stats, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load(self):
        try:
            keymouse_path = os.path.join(self.data_dir, "keymouse_stats.json")
            with open(keymouse_path, "r", encoding="utf-8") as f:
                self.daily_stats = json.load(f)
        except:
            self.daily_stats = {}
        try:
            minute_path = os.path.join(self.data_dir, "minute_stats.json")
            with open(minute_path, "r", encoding="utf-8") as f:
                self.minute_stats = json.load(f)
        except:
            self.minute_stats = {}
        self._recalculate_all_totals()

    def _recalculate_all_totals(self):
        """重新计算所有日期的 total，确保与 minutes 之和一致"""
        for date_str, data in self.minute_stats.items():
            if "minutes" in data:
                data["total"] = sum(data["minutes"])
            if "minute_distance" not in data:
                data["minute_distance"] = [0] * 1440
            if "total_distance" not in data:
                data["total_distance"] = sum(data.get("minute_distance", []))

    def get_minute_stats(self, date_str: str):
        """获取指定日期的分时数据"""
        if date_str in self.minute_stats:
            data = self.minute_stats[date_str]
            data["total"] = sum(data.get("minutes", []))
            data["total_distance"] = sum(data.get("minute_distance", []))
            return data
        return {"minutes": [0] * 1440, "minute_distance": [0] * 1440, "total": 0, "total_distance": 0}

    def get_daily_totals(self, start_date: str, end_date: str):
        """获取日期范围内的每日总按键数和移动距离"""
        result = []
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        current = start
        while current <= end:
            date_str = current.isoformat()
            if date_str in self.minute_stats:
                minutes = self.minute_stats[date_str].get("minutes", [])
                minute_distance = self.minute_stats[date_str].get("minute_distance", [])
                result.append({
                    "date": date_str,
                    "total": sum(minutes),
                    "total_distance": sum(minute_distance)
                })
            else:
                result.append({"date": date_str, "total": 0, "total_distance": 0})
            current += datetime.timedelta(days=1)
        return result

    def get_total_move_distance(self):
        """获取今日总移动距离（像素）"""
        return self.mouse_counts.get("move_distance", 0)