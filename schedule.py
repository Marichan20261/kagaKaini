import os
import json
import datetime

class TaskScheduler:
    def __init__(self, filepath="tasks.json"):
        self.filepath = filepath
        self.tasks = []
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                try:
                    self.tasks = json.load(f)
                except json.JSONDecodeError:
                    self.tasks = []
        else:
            self.tasks = []
        self.sort_tasks()

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def sort_tasks(self):
        self.tasks.sort(key=lambda x: x["time"])

    def add_task(self, task_type, run_time: datetime.datetime, message: str):
        new_task = {
            "type": task_type,
            "time": run_time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        }
        self.tasks.append(new_task)
        self.sort_tasks()
        self.save()

    def get_due_tasks(self, now: datetime.datetime):
        """期限が来たタスクを返し、内部リストから削除"""
        due, remain = [], []
        for task in self.tasks:
            task_time = datetime.datetime.strptime(task["time"], "%Y-%m-%d %H:%M:%S")
            if task_time <= now:
                due.append(task)
            else:
                remain.append(task)
        self.tasks = remain
        return due

    def format_message(self, task):
        """通知文を整形"""
        if task["type"] == "入渠終了":
            return f"{task['message']}の入渠が完了しました。"
        elif task["type"] == "遠征帰投":
            return f"{task['message']}に向かった艦隊が帰投しました。報告書を受け取りに向かってください。"
        elif task["type"] == "To-do":
            return f"以下のTo-doの期限が来ました：{task['message']}"
        elif task["type"] == "時報":
            return f"{task['message']}になりました。"
        elif task["type"] == "建造終了":
            return f"{task['time']}の建造が終わりました。{task['message']}が建造される可能性があります"
        else:
            return f"[{task['type']}] {task['message']}"
