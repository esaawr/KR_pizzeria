#-*- coding: cp1251 -*-
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import filedialog
from PIL import ImageTk, Image, ImageOps
import shutil
import os
import time
import sqlite3
import re
import openpyxl
from openpyxl import Workbook

class PizzaManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления заказами пиццерии")
        self.root.geometry("2560x1600")
        self.root.configure(bg="#FFFFFF")
        self.current_user = None
        self.cart = []
        self.image_cache = []

        self.conn = sqlite3.connect('pizzeria.db')
        self.cursor = self.conn.cursor()
        self.setup_database()

        self.login_screen()

    def export_to_excel(self):
        """Экспорт меню пицц в Excel файл."""
        try:
            self.cursor.execute("SELECT * FROM menu")
            menu_items = self.cursor.fetchall()

            if not menu_items:
                messagebox.showinfo("Информация", "Меню пусто. Нечего экспортировать.")
                return

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Меню"
            sheet.append(["ID", "Название пиццы", "Цена"])

            for item in menu_items:
                sheet.append(item)

            filename = "menu_export.xlsx"
            workbook.save(filename)

            messagebox.showinfo("Успех", f"Меню успешно экспортировано в файл: {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать меню: {e}")

    def setup_database(self):
        """Создание необходимых таблиц в базе данных."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                user_address TEXT NOT NULL,
                user_phone TEXT NOT NULL,
                status TEXT NOT NULL,
                total REAL NOT NULL,
                comment TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_id INTEGER,
                pizza_id INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (pizza_id) REFERENCES menu(id)
            )
        """)
        self.conn.commit()
 
    def login_screen(self):
        """Экран авторизации."""
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Авторизация", font=("Calibri", 44, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)

        tk.Button(frame, text="Вход для администратора", command=self.admin_login,
          font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
          relief=tk.RAISED, width=20, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)

        tk.Button(frame, text="Вход для пользователя", command=self.user_login,
          font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
          relief=tk.RAISED, width=20, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)

        image = Image.open("pizza3.png")
        image = image.resize((550, 200))
        image = ImageOps.expand(image, border=0)
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(root, image=photo, bd=0, highlightthickness=0, bg="#FFFFFF")
        label.image = photo
        label.place(relx=0.5, rely=1, anchor="s", y=-130)

    def admin_login(self):
        """Авторизация администратора."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Администратор", font=("Arial", 34, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)
        tk.Label(frame, text="Логин:", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#000000").pack()
        username_entry = tk.Entry(frame, font=("Arial", 18), width=30, relief=tk.GROOVE, bd=3)
        username_entry.pack(pady=5)
        tk.Label(frame, text="Пароль:", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#000000").pack()
        password_entry = tk.Entry(frame, show="*", font=("Arial", 18), width=30, relief=tk.GROOVE, bd=3)
        password_entry.pack(pady=5)

        image = Image.open("pizza3.png")
        image = image.resize((350, 120))
        image = ImageOps.expand(image, border=0)
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(root, image=photo, bd=0, highlightthickness=0, bg="#FFFFFF")
        label.image = photo
        label.place(relx=0.5, rely=1, anchor="s", y=-100)

        def check_login():
            if username_entry.get() == "Admin" and password_entry.get() == "Admin":
                self.admin_screen()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль.")

        tk.Button(frame, text="Войти", command=check_login,
          font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
          relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)
        tk.Button(frame, text="Назад", command=self.login_screen,font=("Arial", 18, "bold"), bg="#d93c3a", fg="white", activebackground="#a62220",
          relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)

    def user_login(self):
        """Авторизация пользователя (ввод данных пользователя)."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Пользователь", font=("Arial", 34, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=80, pady=(10, 3))

        tk.Label(frame, text="Имя:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=388, pady=(10, 3))
        first_name_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        first_name_entry.pack(pady=(5, 15), anchor="e", padx=50)

        tk.Label(frame, text="Фамилия:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=328, pady=(10, 3))
        last_name_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        last_name_entry.pack(pady=(5, 15), anchor="e", padx=50)

        tk.Label(frame, text="Адрес:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=363, pady=(10, 3))
        address_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        address_entry.pack(pady=(5, 15), anchor="e", padx=50)

        tk.Label(frame, text="Телефон:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=328, pady=(10, ))
        phone_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        phone_entry.pack(pady=(5, 15), anchor="e", padx=50)

        def user_login_action():
            phone = phone_entry.get()
            if not re.match(r'^\+7\d{10}$|^8\d{10}$', phone):
                messagebox.showerror(
                    "Ошибка", 
                    "Номер телефона должен начинаться с '+7' или '8' и содержать 10 цифр после этого."
                )
                return


            if (first_name_entry.get() and last_name_entry.get() and
                    address_entry.get() and phone_entry.get()):
                self.current_user = {
                    "name": f"{first_name_entry.get()} {last_name_entry.get()}",
                    "address": address_entry.get(),
                    "phone": phone_entry.get()
                }
                self.user_screen()
            else:
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")

        tk.Button(frame, text="Войти", command=user_login_action,
                  font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
                  relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
                  borderwidth=5, padx=25, pady=15).pack(anchor="e", padx=140, pady=(20, 10))

        tk.Button(frame, text="Назад", command=self.login_screen,
                  font=("Arial", 18, "bold"), bg="#d93c3a", fg="white", activebackground="#a62220",
                  relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
                  borderwidth=5, padx=25, pady=15).pack(anchor="e", padx=140, pady=(10, 20))

        image = Image.open("pizzeria.png")
        image = image.resize((550, 700))  
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(self.root, image=photo, bd=0, highlightthickness=0, bg="#FFFFFF")
        label.image = photo
        label.place(relx=0.3, rely=1, anchor="s", y=-47)

    def admin_screen(self):
        """Экран администратора."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Администратор", font=("Arial", 34, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)
        tk.Button(frame, text="Управление меню", command=self.manage_menu,
                  font=("Arial", 18, "bold"),bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Просмотр заказов", command=self.view_orders_admin,
                  font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Выход", command=self.login_screen,
                  font=("Arial", 18, "bold"), bg="#d93c3a", fg="white", activebackground="#a62220", relief=tk.RAISED, width=25).pack(pady=10)

        image = Image.open("pizza3.png")
        image = image.resize((550, 200))
        image = ImageOps.expand(image, border=0)
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(root, image=photo, bd=0, highlightthickness=0, bg="#FFFFFF")
        label.image = photo
        label.place(relx=0.5, rely=1, anchor="s", y=-130)

    def manage_menu(self):
        """Управление меню пицц для администратора."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Управление меню", font=("Arial", 24, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)
        tk.Label(frame, text="Название пиццы:", font=("Arial", 14), bg="#FFFFFF").pack()
        name_entry = tk.Entry(frame, font=("Arial", 14), width=30, relief=tk.GROOVE, bd=3)
        name_entry.pack(pady=5)
        tk.Label(frame, text="Цена пиццы:", font=("Arial", 14), bg="#FFFFFF").pack()
        price_entry = tk.Entry(frame, font=("Arial", 14), width=30, relief=tk.GROOVE, bd=3)
        price_entry.pack(pady=5)
        tk.Label(frame, text="Выберите изображение:", font=("Arial", 14), bg="#FFFFFF").pack()
        image_label = tk.Label(frame, text="Файл не выбран", font=("Arial", 12), bg="#FFFFFF", fg="#888888")
        image_label.pack(pady=5)

        image_path = None

        image = Image.open("pizza3.png")
        image = image.resize((350, 120))
        image = ImageOps.expand(image, border=0)
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(root, image=photo, bd=0, highlightthickness=0, bg="#FFFFFF")
        label.image = photo
        label.place(relx=0.5, rely=1, anchor="s", y=-100)
        def select_image():
            nonlocal image_path
            image_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg;*.jpeg")])
            if image_path:
                image_label.config(text=os.path.basename(image_path))

        tk.Button(frame, text="Выбрать изображение", command=select_image, font=("Arial", 12), bg="#3bc43b", fg="white",
                  activebackground="#4fca4f", relief=tk.RAISED).pack(pady=5)

        def add_pizza():
            nonlocal image_path
            name = name_entry.get()
            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом!")
                return

            if not name or not image_path:
                messagebox.showerror("Ошибка", "Введите название пиццы и выберите изображение!")
                return

            
            image_name = f"{name}_{int(time.time())}.jpg"  
            save_path = os.path.join("all_pizzas", image_name)
            shutil.copy(image_path, save_path)

            
            self.cursor.execute("INSERT INTO menu (name, price, image_path) VALUES (?, ?, ?)", (name, price, image_path))
            self.conn.commit()
            messagebox.showinfo("Успех", "Пицца успешно добавлена в меню!")
            self.manage_menu() 

        tk.Button(frame, text="Добавить пиццу", command=add_pizza, font=("Arial", 14), bg="#3bc43b", fg="white",
                  activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Экспорт в Excel", command=self.export_to_excel, font=("Arial", 14), bg="#3bc43b", fg="white",
              activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Назад", command=self.admin_screen, font=("Arial", 14), bg="#d93c3a", fg="white",
                  activebackground="#a62220", relief=tk.RAISED, width=25).pack(pady=10)

    def user_screen(self):
        """Экран пользователя."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text=f"Добро пожаловать, {self.current_user['name']}", font=("Arial", 20, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)
        tk.Button(frame, text="Меню", command=self.view_menu, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Корзина", command=self.view_cart, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Создать заказ", command=self.create_order, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Статус заказа", command=self.view_orders_user, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="Выход", command=self.login_screen, font=("Arial", 14), bg="#d93c3a", fg="white", activebackground="#a62220", relief=tk.RAISED, width=25).pack(pady=10)

    def view_menu(self):
        """Просмотр меню для пользователя и добавление в корзину."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Меню", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        canvas = tk.Canvas(frame, bg="#FFFFFF", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFFFFF")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.menu_container = scrollable_frame  
        self.update_menu()

        tk.Button(
            frame,
            text="Назад",
            command=self.user_screen,
            font=("Arial", 14),
            bg="#d93c3a",
            fg="white",
            activebackground="#a62220",
            relief=tk.RAISED,
            width=25,
        ).pack(pady=10)


    def update_menu(self):
        """Обновить меню из базы данных."""
        for widget in self.menu_container.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT * FROM menu")
        menu_items = self.cursor.fetchall()

        for pizza in menu_items:
            pizza_frame = tk.Frame(self.menu_container, bg="#FFFFFF")
            pizza_frame.pack(pady=10, padx=10, fill=tk.X)

            image_path = pizza[3].strip()
            try:
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Файл не найден: {image_path}")

                img = Image.open(image_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Ошибка загрузки изображения {image_path}: {e}")
                
                placeholder_path = "placeholder.jpg"  
                img = Image.open(placeholder_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

            self.image_cache.append(photo)
            img_label = tk.Label(pizza_frame, image=photo, bg="#FFFFFF")
            img_label.pack(side=tk.LEFT, padx=10)

            pizza_info = tk.Label(pizza_frame, text=f"{pizza[1]} - {pizza[2]} руб.", font=("Arial", 14), bg="#FFFFFF", fg="#333333")
            pizza_info.pack(side=tk.LEFT, padx=10)

            add_button = tk.Button(
                pizza_frame,
                text="Добавить в корзину",
                command=lambda pizza_id=pizza[0]: self.add_to_cart(pizza_id),
                font=("Arial", 12),
                bg="#3bc43b",
                fg="white",
                activebackground="#4fca4f",
                relief=tk.RAISED,
                width=20,
            )
            add_button.pack(side=tk.RIGHT, padx=10)

    def add_to_cart(self, pizza_id):
        """Добавить пиццу в корзину."""
        self.cart.append(pizza_id)
        messagebox.showinfo("Успех", "Пицца добавлена в корзину!")

    def view_cart(self):
        """Просмотр корзины для пользователя с изображениями и возможностью удаления."""
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#ffffff", bd=0, relief=tk.FLAT)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Корзина", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        canvas = tk.Canvas(frame, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        cart_container = tk.Frame(canvas, bg="#ffffff")

        cart_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=cart_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def update_cart():
            for widget in cart_container.winfo_children():
                widget.destroy()

            total_price = 0

            for idx, pizza_id in enumerate(self.cart):
                self.cursor.execute("SELECT name, price, image_path FROM menu WHERE id=?", (pizza_id,))
                pizza = self.cursor.fetchone()

                if pizza:
                    pizza_frame = tk.Frame(cart_container, bg="#ffffff", bd=0, relief=tk.FLAT)
                    pizza_frame.pack(pady=5, padx=10, fill=tk.X)

                    image_path = pizza[2].strip()
                    try:
                        if not os.path.exists(image_path):
                            raise FileNotFoundError(f"Файл не найден: {image_path}")

                        img = Image.open(image_path)
                        img = img.resize((100, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                    except Exception as e:
                        print(f"Ошибка загрузки изображения {image_path}: {e}")
                        placeholder_path = "placeholder.jpg"
                        img = Image.open(placeholder_path)
                        img = img.resize((100, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)

                    self.image_cache.append(photo)
                    img_label = tk.Label(pizza_frame, image=photo, bg="#ffffff")
                    img_label.pack(side=tk.LEFT, padx=5)

                    info_label = tk.Label(pizza_frame, text=f"{pizza[0]} - {pizza[1]} руб.", font=("Arial", 14), bg="#ffffff", fg="#333333")
                    info_label.pack(side=tk.LEFT, padx=10)

                    def remove(idx=idx):
                        del self.cart[idx]
                        update_cart()

                    remove_button = tk.Button(pizza_frame, text="Удалить", command=remove, font=("Arial", 12),
                                              bg="#d93c3a", fg="white", activebackground="#a62220", relief=tk.RAISED)
                    remove_button.pack(side=tk.RIGHT, padx=5)

                    total_price += pizza[1]

            total_label.config(text=f"Итого: {total_price} руб.")

        total_label = tk.Label(frame, text="Итого: 0 руб.", font=("Arial", 14), bg="#ffffff", fg="#333333")
        total_label.pack(pady=10)

        tk.Button(frame, text="Назад", command=self.user_screen, font=("Arial", 14), bg="#f44336", fg="white",
                  activebackground="#e53935", relief=tk.RAISED, width=25).pack(pady=10)

        update_cart()

    def create_order(self):
        """Создание нового заказа пользователем."""
        if not self.cart:
            messagebox.showerror("Ошибка", "Ваша корзина пуста! Добавьте пиццы в корзину перед созданием заказа.")
            return

        total_price = 0
        for pizza_id in self.cart:
            self.cursor.execute("SELECT price FROM menu WHERE id=?", (pizza_id,))
            total_price += self.cursor.fetchone()[0]

        comment = simpledialog.askstring("Комментарий", "Введите комментарий к заказу (если есть):")

        self.cursor.execute("INSERT INTO orders (user_name, user_address, user_phone, status, total, comment) VALUES (?, ?, ?, ?, ?, ?)",
                            (self.current_user['name'], self.current_user['address'], self.current_user['phone'], "Готовится", total_price, comment))
        order_id = self.cursor.lastrowid

        for pizza_id in self.cart:
            self.cursor.execute("INSERT INTO order_items (order_id, pizza_id) VALUES (?, ?)", (order_id, pizza_id))

        self.conn.commit()
        self.cart = []

        messagebox.showinfo("Успех", f"Заказ создан! Общая стоимость: {total_price} руб.")
        self.user_screen()

    def view_orders_user(self):
        """Просмотр статуса заказа для пользователя."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#ffffff", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Ваши заказы", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        self.cursor.execute("SELECT * FROM orders WHERE user_name=?", (self.current_user['name'],))
        orders = self.cursor.fetchall()

        if not orders:
            tk.Label(frame, text="У вас нет заказов.", font=("Arial", 14), bg="#ffffff").pack(pady=10)
        else:
            for order in orders:
                order_frame = tk.Frame(frame, bg="#ffffff", bd=0, relief=tk.GROOVE)
                order_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(order_frame, text=f"Заказ #{order[0]}", font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").pack()
                tk.Label(order_frame, text=f"Статус: {order[4]}", font=("Arial", 12), bg="#ffffff").pack(anchor="w")
                tk.Label(order_frame, text=f"Комментарий: {order[6]}", font=("Arial", 12), bg="#ffffff").pack(anchor="w")

        tk.Button(frame, text="Назад", command=self.user_screen, font=("Arial", 14), bg="#f44336", fg="white",
                  activebackground="#e53935", relief=tk.RAISED, width=25).pack(pady=10)

    def view_orders_admin(self):
        """Просмотр заказов для администратора."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#ffffff", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Все заказы", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        self.cursor.execute("SELECT * FROM orders")
        orders = self.cursor.fetchall()

        if not orders:
            tk.Label(frame, text="Нет заказов.", font=("Arial", 14), bg="#ffffff").pack(pady=10)
        else:
            for order in orders:
                order_frame = tk.Frame(frame, bg="#ffffff", bd=0, relief=tk.GROOVE)
                order_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(order_frame, text=f"Заказ #{order[0]} ({order[1]})", font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").pack()
                tk.Label(order_frame, text=f"Статус: {order[4]}", font=("Arial", 12), bg="#ffffff").pack(anchor="w")
                tk.Label(order_frame, text=f"Итого: {order[5]} руб.", font=("Arial", 12), bg="#ffffff").pack(anchor="w")

                def update_status(order_id, new_status):
                    self.cursor.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
                    self.conn.commit()
                    messagebox.showinfo("Успех", f"Статус заказа #{order_id} обновлен на '{new_status}'")
                    self.view_orders_admin()

                tk.Button(order_frame, text="Готовится", command=lambda oid=order[0]: update_status(oid, "Готовится"), font=("Arial", 12),
                          bg="#FFC107", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
                tk.Button(order_frame, text="В пути", command=lambda oid=order[0]: update_status(oid, "В пути"), font=("Arial", 12),
                          bg="#FF9800", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
                tk.Button(order_frame, text="Приехало", command=lambda oid=order[0]: update_status(oid, "Приехало"), font=("Arial", 12),
                          bg="#4CAF50", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
                tk.Button(order_frame, text="Завершён", command=lambda oid=order[0]: update_status(oid, "Заказ завершён"), font=("Arial", 12),
                          bg="#8BC34A", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="Назад", command=self.admin_screen, font=("Arial", 14), bg="#f44336", fg="white",
                  activebackground="#e53935", relief=tk.RAISED, width=25).pack(pady=10)

    def clear_screen(self):
        """Очистка текущего экрана."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_exit(self):
        self.conn.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PizzaManagementApp(root)
    root.mainloop()