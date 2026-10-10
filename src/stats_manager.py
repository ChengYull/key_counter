import datetime
import json
from typing import Any


# class StatsManager:
#     # pynput 鼠标按钮名称映射到热力图按键名称
#     MOUSE_BUTTON_MAP: dict[str, str] = {
#         "left": "left",
#         "right": "right",
#         "middle": "wheel",
#         "x1": "side1",
#         "x2": "side2",
#     }
#
#     # TODO: 感觉 minute_stats 和 daily_stats 可以用具名类当结构体替换，就几个字段呢，而且这样没有 Any（
#     daily_stats: dict[str, dict[str, dict[str, int]]]
#     minute_stats: dict[
#         str, dict[str, Any]
#     ]  # date -> {"minutes": dict[str,int], "minute_distance": dict[str,int], "total": int, "total_distance": int}
#     current_date: str
#     current_minute: int
#     keyboard_counts: dict[str, int]
#     mouse_counts: dict[str, int]
#     today_minutes: dict[str, int]
#     today_minute_distance: dict[str, int]
#
#     def __init__(self) -> None:
#         self.daily_stats = {}  # "YYYY-MM-DD": {"keyboard": dict, "mouse": dict}
#         self.minute_stats = (
#             {}
#         )  # "YYYY-MM-DD": {"minutes": {}, "minute_distance": {}, "total": int, "total_distance": int}
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
    MOUSE_BUTTON_MAP: dict[str, str] = {
        "left": "left",
        "right": "right",
        "middle": "wheel",
        "x1": "side1",
        "x2": "side2",
    }
    def __init__(self):
        self.data_dir = get_data_dir()
        self.daily_stats = {}                    # "YYYY-MM-DD": {"keyboard": dict, "mouse": dict}
        self.minute_stats = {}                   # "YYYY-MM-DD": {"minutes": dict, "total": int}
        self.current_date = datetime.date.today().isoformat()
        self.current_minute = self._get_current_minute()
        self.load()
        self.ensure_today()
        self.ensure_today_minute()

    def _get_current_minute(self) -> int:
        """获取当前分钟索引 (0-1439)"""
        now = datetime.datetime.now()
        return now.hour * 60 + now.minute

    def ensure_today(self) -> None:
        if self.current_date not in self.daily_stats:
            self.daily_stats[self.current_date] = {"keyboard": {}, "mouse": {}}
        self.keyboard_counts = self.daily_stats[self.current_date]["keyboard"]
        self.mouse_counts = self.daily_stats[self.current_date]["mouse"]

    def ensure_today_minute(self) -> None:
        """确保今日分时统计数据存在"""
        if self.current_date not in self.minute_stats:
            self.minute_stats[self.current_date] = {
                "minutes": {},
                "total": 0,
            }
        self.today_minutes = self.minute_stats[self.current_date]["minutes"]

    def increment_key(self, key_name: str) -> None:
        self.check_date_change()
        self.keyboard_counts[key_name] = self.keyboard_counts.get(key_name, 0) + 1
        self._increment_minute()
        self.save()

    def increment_mouse(self, button: Any) -> None:
        self.check_date_change()
        btn_str = str(button).split(".")[-1].lower()
        key_name = self.MOUSE_BUTTON_MAP.get(btn_str, btn_str)
        if key_name in ("side1", "side2"):
            return
        self.mouse_counts[key_name] = self.mouse_counts.get(key_name, 0) + 1
        self._increment_minute()
        self.save()

    def _increment_minute(self) -> None:
        """增加当前分钟的计数"""
        self.check_minute_change()
        key = str(self.current_minute)
        self.today_minutes[key] = self.today_minutes.get(key, 0) + 1
        self.minute_stats[self.current_date]["total"] += 1

    def check_date_change(self) -> None:
        """检查日期是否变化"""
        today = datetime.date.today().isoformat()
        if today != self.current_date:
            self.current_date = today
            self.current_minute = self._get_current_minute()
            self.ensure_today()
            self.ensure_today_minute()

    def check_minute_change(self) -> None:
        """检查分钟是否变化"""
        current = self._get_current_minute()
        if current != self.current_minute:
            self.current_minute = current

    def save(self) -> None:
        try:
            keymouse_path = os.path.join(self.data_dir, "keymouse_stats.json")
            with open(keymouse_path, "w", encoding="utf-8") as f:
                json.dump(self.daily_stats, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 噗
        try:
            minute_path = os.path.join(self.data_dir, "minute_stats.json")
            with open(minute_path, "w", encoding="utf-8") as f:
                json.dump(self.minute_stats, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 吞掉了

    def load(self) -> None:
        try:
            keymouse_path = os.path.join(self.data_dir, "keymouse_stats.json")
            with open(keymouse_path, "r", encoding="utf-8") as f:
                self.daily_stats = json.load(f)
        except Exception:
            self.daily_stats = {}
        # 兼容旧数据：移除已废弃的移动距离字段
        for _daily in self.daily_stats.values():
            _daily.get("mouse", {}).pop("move_distance", None)
        try:
            minute_path = os.path.join(self.data_dir, "minute_stats.json")
            with open(minute_path, "r", encoding="utf-8") as f:
                self.minute_stats = json.load(f)
        except Exception:
            self.minute_stats = {}
        self._recalculate_all_totals()

    def _migrate_sparse(self, data: dict[str, Any]) -> None:
        """将旧列表格式转为稀疏字典格式"""
        if isinstance(data.get("minutes"), list):
            data["minutes"] = {
                str(i): v for i, v in enumerate(data["minutes"]) if v != 0
            }
        # 兼容旧数据：移除已废弃的移动距离字段
        data.pop("minute_distance", None)
        data.pop("total_distance", None)

    def _recalculate_all_totals(self) -> None:
        """迁移并重新计算所有日期的 total"""
        for _date_str, data in self.minute_stats.items():
            self._migrate_sparse(data)
            if "minutes" in data:
                data["total"] = sum(data.get("minutes", {}).values())

    def _expand_minutes(self, sparse_dict: dict[str, int]) -> list[int]:
        """展开稀疏表为 1440 项的数组"""
        result = [0] * 1440
        for k, v in sparse_dict.items():
            result[int(k)] = v
        return result

    def get_minute_stats(self, date_str: str) -> dict[str, Any]:
        """获取指定日期的分时数据"""
        if date_str in self.minute_stats:
            data = self.minute_stats[date_str]
            data["total"] = sum(data.get("minutes", {}).values())
            return {
                "minutes": self._expand_minutes(data.get("minutes", {})),
                "total": data["total"],
            }
        return {
            "minutes": [0] * 1440,
            "total": 0,
        }

    def get_daily_totals(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """获取日期范围内的每日总按键数"""
        result: list[dict[str, Any]] = []
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        current = start
        while current <= end:
            date_str = current.isoformat()
            if date_str in self.minute_stats:
                minutes = self.minute_stats[date_str].get("minutes", {})
                result.append(
                    {
                        "date": date_str,
                        "total": sum(minutes.values()),
                    }
                )
            else:
                result.append({"date": date_str, "total": 0})
            current += datetime.timedelta(days=1)
        return result
