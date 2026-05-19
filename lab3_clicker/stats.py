import json
import statistics
import os


class Stats:
    def __init__(self):
        self.reactions = []
        self.load()

    def add_reaction(self, time_ms: float):
        self.reactions.append(time_ms)
        self.save()

    def get_best(self):
        return min(self.reactions) if self.reactions else 0

    def get_average(self):
        return round(statistics.mean(self.reactions), 2) if self.reactions else 0

    def get_count(self):
        return len(self.reactions)

    def save(self):
        data = {
            "reactions": self.reactions,
            "best": self.get_best(),
            "average": self.get_average(),
            "count": self.get_count(),
        }
        try:
            with open("stats.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            # на случай ошибок записи просто не падаем
            pass

    def load(self):
        if os.path.exists("stats.json"):
            try:
                with open("stats.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.reactions = data.get("reactions", [])
            except Exception:
                # если файл битый — начинаем с пустой статистики
                self.reactions = []