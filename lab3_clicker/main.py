import tkinter as tk
from tkinter import messagebox
import random
import time

from stats import Stats


class ClickerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лабораторная №3: Тестер реакции (Кликер)")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)

        self.stats = Stats()

        self.button = None          # id объекта на canvas
        self.button_bbox = None     # (x1, y1, x2, y2) — границы кнопки
        self.start_time = 0
        self.state = "ready"        # ready, waiting, active

        self.setup_ui()

        # горячие клавиши
        self.root.bind("<space>", lambda e: self.start_game())
        self.root.bind("<Escape>", lambda e: self.reset())
        self.root.focus_set()

    def setup_ui(self):
        title = tk.Label(
            self.root,
            text="🧠 Тестер реакции",
            font=("Arial", 24, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50",
        )
        title.pack(pady=20)

        instr = tk.Label(
            self.root,
            text="Нажмите SPACE или 'Старт'.\nКликните на зелёную кнопку как можно быстрее!",
            font=("Arial", 12),
            fg="#bdc3c7",
            bg="#2c3e50",
        )
        instr.pack(pady=10)

        self.start_btn = tk.Button(
            self.root,
            text="🚀 Старт",
            font=("Arial", 16, "bold"),
            bg="#27ae60",
            fg="white",
            width=15,
            height=2,
            command=self.start_game,
            relief="flat",
        )
        self.start_btn.pack(pady=20)

        self.canvas = tk.Canvas(
            self.root,
            width=500,
            height=250,
            bg="#34495e",
            relief="ridge",
            highlightthickness=0,
        )
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        stats_frame = tk.Frame(self.root, bg="#2c3e50")
        stats_frame.pack(pady=10)

        self.best_label = tk.Label(
            stats_frame,
            text=f"Лучшее: {self.stats.get_best()} мс",
            font=("Arial", 12, "bold"),
            fg="#f39c12",
            bg="#2c3e50",
        )
        self.best_label.pack(side="left", padx=20)

        self.avg_label = tk.Label(
            stats_frame,
            text=f"Среднее: {self.stats.get_average()} мс",
            font=("Arial", 12, "bold"),
            fg="#3498db",
            bg="#2c3e50",
        )
        self.avg_label.pack(side="left", padx=20)

        self.count_label = tk.Label(
            stats_frame,
            text=f"Попыток: {self.stats.get_count()}",
            font=("Arial", 12, "bold"),
            fg="#e74c3c",
            bg="#2c3e50",
        )
        self.count_label.pack(side="left", padx=20)

        self.status_label = tk.Label(
            self.root,
            text="Готов к игре (SPACE или Старт)",
            font=("Arial", 14),
            fg="#95a5a6",
            bg="#2c3e50",
        )
        self.status_label.pack(pady=10)

    def start_game(self):
        if self.state != "ready":
            return
        self.state = "waiting"
        self.status_label.config(
            text="Ждите... (зелёная кнопка появится случайно)", fg="#f39c12"
        )
        self.start_btn.config(state="disabled")
        self.canvas.delete("all")
        self.button = None
        self.button_bbox = None
        # задержка от 1 до 5 секунд
        delay = random.randint(1000, 5000)
        self.root.after(delay, self.show_button)

    def show_button(self):
        if self.state != "waiting":
            return

        self.state = "active"
        self.start_time = time.time() * 1000  # миллисекунды
        self.status_label.config(text="КЛИКНИТЕ НА КНОПКУ!", fg="#27ae60")

        # случайная позиция
        x = random.randint(50, 400)
        y = random.randint(50, 150)
        r = 40  # радиус

        self.button = self.canvas.create_oval(
            x, y, x + 2 * r, y + 2 * r,
            fill="#27ae60",
            outline="white",
            width=4,
            tags="target",
        )
        self.canvas.create_text(
            x + r,
            y + r,
            text="КЛИК!",
            font=("Arial", 14, "bold"),
            fill="white",
            tags="target",
        )

        # запоминаем прямоугольник, в котором находится кнопка
        self.button_bbox = (x, y, x + 2 * r, y + 2 * r)

    def on_canvas_click(self, event):
        # клик до появления кнопки
        if self.state == "waiting":
            messagebox.showerror("Ошибка", "Слишком рано! Ждите зелёной кнопки.")
            self.reset()
            return

        # если игра не в активном состоянии — игнор
        if self.state != "active" or not self.button or not self.button_bbox:
            return

        x1, y1, x2, y2 = self.button_bbox

        # проверка промаха
        if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
            messagebox.showerror("Промах", "Вы не попали по кнопке!")
            self.reset()
            return

        # сюда попадаем только если кликнули по кнопке
        end_time = time.time() * 1000
        reaction_time = end_time - self.start_time

        self.stats.add_reaction(reaction_time)
        self.update_stats()

        self.canvas.delete("target")
        self.button = None
        self.button_bbox = None

        color = "gold" if reaction_time < 250 else "#e74c3c"
        text_comment = "Отлично!" if reaction_time < 250 else "Попробуйте ещё"
        self.status_label.config(
            text=f"Ваше время: {reaction_time:.0f} мс ({text_comment})",
            fg=color,
        )

        self.root.after(2000, self.reset)

    def reset(self):
        self.state = "ready"
        self.status_label.config(
            text="Готов к игре (SPACE или Старт)", fg="#95a5a6"
        )
        self.start_btn.config(state="normal")
        self.canvas.delete("all")
        self.button = None
        self.button_bbox = None

    def update_stats(self):
        self.best_label.config(text=f"Лучшее: {self.stats.get_best()} мс")
        self.avg_label.config(text=f"Среднее: {self.stats.get_average()} мс")
        self.count_label.config(text=f"Попыток: {self.stats.get_count()}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ClickerApp()
    app.run()