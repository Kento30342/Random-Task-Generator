import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json
from datetime import datetime
from collections import deque

class RandomTaskGenerator:
    """Главное приложение генератора случайных задач"""

    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Генератор случайных задач")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Предопределенные задачи с категориями
        self.default_tasks = [
            {"name": "Прочитать статью о Python", "category": "учёба"},
            {"name": "Сделать зарядку 15 минут", "category": "спорт"},
            {"name": "Написать код для проекта", "category": "работа"},
            {"name": "Выучить 10 новых английских слов", "category": "учёба"},
            {"name": "Пробежка 3 км", "category": "спорт"},
            {"name": "Отправить отчет по работе", "category": "работа"},
            {"name": "Просмотреть обучающее видео", "category": "учёба"},
            {"name": "Сделать план тренировок", "category": "спорт"},
            {"name": "Провести встречу с командой", "category": "работа"},
            {"name": "Решить задачи на LeetCode", "category": "учёба"},
            {"name": "Йога 20 минут", "category": "спорт"},
            {"name": "Закончить дедлайн", "category": "работа"}
        ]

        # Загрузка задач из JSON или использование стандартных
        self.tasks = self.load_tasks()

        # История сгенерированных задач (очередь)
        self.task_history = deque(maxlen=100)
        self.current_task = None

        # Создание интерфейса
        self.setup_ui()

        # Обновление списка категорий в фильтре
        self.update_category_filter()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""

        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Генератор случайных задач",
                                font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # --- Секция генерации задачи ---
        generate_frame = ttk.LabelFrame(main_frame, text="Генерация задачи", padding="10")
        generate_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.generate_btn = ttk.Button(generate_frame, text="🎲 Сгенерировать задачу",
                                       command=self.generate_task, width=30)
        self.generate_btn.pack(pady=5)

        self.current_task_label = ttk.Label(generate_frame, text="Нажмите кнопку для генерации задачи",
                                           font=('Arial', 12), foreground='blue')
        self.current_task_label.pack(pady=10)

        # --- Секция добавления новой задачи ---
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(0, 5))

        ttk.Label(add_frame, text="Название задачи:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.task_entry = ttk.Entry(add_frame, width=30)
        self.task_entry.grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))

        ttk.Label(add_frame, text="Категория:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(add_frame, textvariable=self.category_var,
                                           values=["учёба", "спорт", "работа"], width=27)
        self.category_combo.grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E))
        self.category_combo.set("учёба")

        self.add_btn = ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_task)
        self.add_btn.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))

        # --- Секция фильтрации ---
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация истории", padding="10")
        filter_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.filter_var = tk.StringVar(value="все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=20)
        self.filter_combo.grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        self.filter_combo.bind('<<ComboboxSelected>>', self.filter_history)

        self.clear_filter_btn = ttk.Button(filter_frame, text="🔄 Сбросить фильтр",
                                          command=self.clear_filter)
        self.clear_filter_btn.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))

        # Кнопки управления данными
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.save_btn = ttk.Button(control_frame, text="💾 Сохранить задачи",
                                   command=self.save_tasks)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(control_frame, text="🔄 Сбросить к стандартным",
                                    command=self.reset_to_default)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # --- История задач ---
        history_frame = ttk.LabelFrame(main_frame, text="История сгенерированных задач", padding="10")
        history_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        # Создание Treeview для отображения истории
        columns = ('Время', 'Задача', 'Категория')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=15)

        # Настройка заголовков
        self.history_tree.heading('Время', text='Время генерации')
        self.history_tree.heading('Задача', text='Задача')
        self.history_tree.heading('Категория', text='Категория')

        # Настройка ширины колонок
        self.history_tree.column('Время', width=150)
        self.history_tree.column('Задача', width=350)
        self.history_tree.column('Категория', width=100)

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Информационная метка
        self.info_label = ttk.Label(main_frame, text="Всего задач в базе: 0", font=('Arial', 10))
        self.info_label.grid(row=5, column=0, columnspan=2, pady=5)

        self.update_info_label()

    def update_category_filter(self):
        """Обновление списка категорий в фильтре"""
        categories = list(set(task["category"] for task in self.tasks))
        categories.sort()
        self.filter_combo['values'] = ["все"] + categories
        self.filter_var.set("все")

    def generate_task(self):
        """Генерация случайной задачи"""
        if not self.tasks:
            messagebox.showwarning("Нет задач", "Добавьте хотя бы одну задачу в список!")
            return

        # Выбор случайной задачи
        task = random.choice(self.tasks)
        self.current_task = task

        # Добавление в историю с временной меткой
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": task["name"],
            "category": task["category"]
        }
        self.task_history.append(history_entry)

        # Обновление отображения
        self.current_task_label.config(
            text=f"🎯 {task['name']} (Категория: {task['category']})",
            foreground='green'
        )

        # Обновление истории в таблице
        self.update_history_display()

        # Всплывающее уведомление
        self.root.after(2000, self.clear_task_highlight)

    def clear_task_highlight(self):
        """Очистка подсветки текущей задачи"""
        if hasattr(self, 'current_task_label'):
            self.current_task_label.config(foreground='blue')

    def add_task(self):
        """Добавление новой задачи"""
        task_name = self.task_entry.get().strip()
        category = self.category_var.get()

        # Проверка корректности ввода
        if not task_name:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return

        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию задачи!")
            return

        # Проверка на дубликат
        if any(task["name"].lower() == task_name.lower() for task in self.tasks):
            messagebox.showwarning("Предупреждение", "Такая задача уже существует!")
            return

        # Добавление задачи
        new_task = {"name": task_name, "category": category}
        self.tasks.append(new_task)

        # Очистка поля ввода
        self.task_entry.delete(0, tk.END)

        # Обновление интерфейса
        messagebox.showinfo("Успех", f"Задача '{task_name}' добавлена!")
        self.update_category_filter()
        self.update_info_label()

    def update_history_display(self):
        """Обновление отображения истории в таблице"""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Получение фильтрованной истории
        filtered_history = self.get_filtered_history()

        # Добавление отфильтрованных записей
        for entry in filtered_history:
            self.history_tree.insert('', 'end', values=(
                entry['timestamp'],
                entry['task'],
                entry['category']
            ))

    def get_filtered_history(self):
        """Получение истории с учетом фильтра"""
        filter_value = self.filter_var.get()

        if filter_value == "все":
            return list(self.task_history)
        else:
            return [entry for entry in self.task_history if entry['category'] == filter_value]

    def filter_history(self, event=None):
        """Фильтрация истории по категории"""
        self.update_history_display()

    def clear_filter(self):
        """Сброс фильтра"""
        self.filter_var.set("все")
        self.update_history_display()

    def save_tasks(self):
        """Сохранение задач в JSON файл"""
        try:
            data = {
                "tasks": self.tasks,
                "history": [dict(entry) for entry in self.task_history]
            }
            with open('tasks.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Успех", "Задачи и история успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачи: {str(e)}")

    def load_tasks(self):
        """Загрузка задач из JSON файла"""
        try:
            with open('tasks.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Загрузка задач
            tasks = data.get('tasks', self.default_tasks)

            # Загрузка истории
            history_data = data.get('history', [])
            self.task_history = deque(history_data, maxlen=100)

            # Обновление отображения истории
            self.update_history_display()

            return tasks

        except FileNotFoundError:
            # Если файл не найден, используем стандартные задачи
            return self.default_tasks.copy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")
            return self.default_tasks.copy()

    def reset_to_default(self):
        """Сброс к стандартным задачам"""
        if messagebox.askyesno("Подтверждение", "Сбросить все задачи к стандартным? История будет очищена!"):
            self.tasks = self.default_tasks.copy()
            self.task_history.clear()
            self.update_history_display()
            self.update_category_filter()
            self.update_info_label()
            messagebox.showinfo("Успех", "Сброс выполнен!")

    def update_info_label(self):
        """Обновление информационной метки"""
        categories_count = {}
        for task in self.tasks:
            cat = task["category"]
            categories_count[cat] = categories_count.get(cat, 0) + 1

        info_text = f"Всего задач: {len(self.tasks)} | "
        info_text += " | ".join([f"{cat}: {count}" for cat, count in categories_count.items()])
        self.info_label.config(text=info_text)

    def on_closing(self):
        """Обработка закрытия окна"""
        if messagebox.askyesno("Выход", "Сохранить задачи перед выходом?"):
            self.save_tasks()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
