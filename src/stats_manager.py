import datetime
import json


class StatsManager:
    def __init__(self):
        self.daily_stats = {}                    # "YYYY-MM-DD": {"keyboard": dict, "mouse": dict}
        self.current_date = datetime.date.today().isoformat()
        self.load()
        self.ensure_today()

    def ensure_today(self):
        if self.current_date not in self.daily_stats:
            self.daily_stats[self.current_date] = {"keyboard": {}, "mouse": {}}
        self.keyboard_counts = self.daily_stats[self.current_date]["keyboard"]
        self.mouse_counts = self.daily_stats[self.current_date]["mouse"]

    def increment_key(self, key_name: str):
        self.check_date_change()
        self.keyboard_counts[key_name] = self.keyboard_counts.get(key_name, 0) + 1
        self.save()

    def increment_mouse(self, button):
        self.check_date_change()
        btn_str = str(button).split('.')[-1]
        self.mouse_counts[btn_str] = self.mouse_counts.get(btn_str, 0) + 1
        self.save()

    def check_date_change(self):
        today = datetime.date.today().isoformat()
        if today != self.current_date:
            self.current_date = today
            self.ensure_today()

    def save(self):
        try:
            with open("keymouse_stats.json", "w", encoding="utf-8") as f:
                json.dump(self.daily_stats, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load(self):
        try:
            with open("keymouse_stats.json", "r", encoding="utf-8") as f:
                self.daily_stats = json.load(f)
        except:
            self.daily_stats = {}