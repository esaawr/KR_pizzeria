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
        self.root.title("������� ���������� �������� ��������")
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
        """������� ���� ���� � Excel ����."""
        try:
            self.cursor.execute("SELECT * FROM menu")
            menu_items = self.cursor.fetchall()

            if not menu_items:
                messagebox.showinfo("����������", "���� �����. ������ ��������������.")
                return

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "����"
            sheet.append(["ID", "�������� �����", "����"])

            for item in menu_items:
                sheet.append(item)

            filename = "menu_export.xlsx"
            workbook.save(filename)

            messagebox.showinfo("�����", f"���� ������� �������������� � ����: {filename}")
        except Exception as e:
            messagebox.showerror("������", f"�� ������� �������������� ����: {e}")

    def setup_database(self):
        """�������� ����������� ������ � ���� ������."""
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
        """����� �����������."""
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="�����������", font=("Calibri", 44, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)

        tk.Button(frame, text="���� ��� ��������������", command=self.admin_login,
          font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
          relief=tk.RAISED, width=20, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)

        tk.Button(frame, text="���� ��� ������������", command=self.user_login,
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
        """����������� ��������������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="�������������", font=("Arial", 34, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)
        tk.Label(frame, text="�����:", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#000000").pack()
        username_entry = tk.Entry(frame, font=("Arial", 18), width=30, relief=tk.GROOVE, bd=3)
        username_entry.pack(pady=5)
        tk.Label(frame, text="������:", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#000000").pack()
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
                messagebox.showerror("������", "�������� ����� ��� ������.")

        tk.Button(frame, text="�����", command=check_login,
          font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
          relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)
        tk.Button(frame, text="�����", command=self.login_screen,font=("Arial", 18, "bold"), bg="#d93c3a", fg="white", activebackground="#a62220",
          relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
          borderwidth=5, padx=25, pady=15).pack(pady=10)

    def user_login(self):
        """����������� ������������ (���� ������ ������������)."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="������������", font=("Arial", 34, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=80, pady=(10, 3))

        tk.Label(frame, text="���:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=388, pady=(10, 3))
        first_name_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        first_name_entry.pack(pady=(5, 15), anchor="e", padx=50)

        tk.Label(frame, text="�������:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=328, pady=(10, 3))
        last_name_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        last_name_entry.pack(pady=(5, 15), anchor="e", padx=50)

        tk.Label(frame, text="�����:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=363, pady=(10, 3))
        address_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        address_entry.pack(pady=(5, 15), anchor="e", padx=50)

        tk.Label(frame, text="�������:", font=("Arial", 19, "bold"), bg="#FFFFFF", fg="#000000").pack(anchor="e", padx=328, pady=(10, ))
        phone_entry = tk.Entry(frame, font=("Arial", 18, "bold"), width=30, relief=tk.GROOVE, bd=3)
        phone_entry.pack(pady=(5, 15), anchor="e", padx=50)

        def user_login_action():
            phone = phone_entry.get()
            if not re.match(r'^\+7\d{10}$|^8\d{10}$', phone):
                messagebox.showerror(
                    "������", 
                    "����� �������� ������ ���������� � '+7' ��� '8' � ��������� 10 ���� ����� �����."
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
                messagebox.showerror("������", "����������, ��������� ��� ����.")

        tk.Button(frame, text="�����", command=user_login_action,
                  font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f",
                  relief=tk.RAISED, width=10, height=1, bd=5, highlightthickness=0,
                  borderwidth=5, padx=25, pady=15).pack(anchor="e", padx=140, pady=(20, 10))

        tk.Button(frame, text="�����", command=self.login_screen,
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
        """����� ��������������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="�������������", font=("Arial", 34, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)
        tk.Button(frame, text="���������� ����", command=self.manage_menu,
                  font=("Arial", 18, "bold"),bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="�������� �������", command=self.view_orders_admin,
                  font=("Arial", 18, "bold"), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="�����", command=self.login_screen,
                  font=("Arial", 18, "bold"), bg="#d93c3a", fg="white", activebackground="#a62220", relief=tk.RAISED, width=25).pack(pady=10)

        image = Image.open("pizza3.png")
        image = image.resize((550, 200))
        image = ImageOps.expand(image, border=0)
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(root, image=photo, bd=0, highlightthickness=0, bg="#FFFFFF")
        label.image = photo
        label.place(relx=0.5, rely=1, anchor="s", y=-130)

    def manage_menu(self):
        """���������� ���� ���� ��� ��������������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="���������� ����", font=("Arial", 24, "bold"), bg="#FFFFFF", fg="#000000").pack(pady=20)
        tk.Label(frame, text="�������� �����:", font=("Arial", 14), bg="#FFFFFF").pack()
        name_entry = tk.Entry(frame, font=("Arial", 14), width=30, relief=tk.GROOVE, bd=3)
        name_entry.pack(pady=5)
        tk.Label(frame, text="���� �����:", font=("Arial", 14), bg="#FFFFFF").pack()
        price_entry = tk.Entry(frame, font=("Arial", 14), width=30, relief=tk.GROOVE, bd=3)
        price_entry.pack(pady=5)
        tk.Label(frame, text="�������� �����������:", font=("Arial", 14), bg="#FFFFFF").pack()
        image_label = tk.Label(frame, text="���� �� ������", font=("Arial", 12), bg="#FFFFFF", fg="#888888")
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
            image_path = filedialog.askopenfilename(filetypes=[("�����������", "*.png;*.jpg;*.jpeg")])
            if image_path:
                image_label.config(text=os.path.basename(image_path))

        tk.Button(frame, text="������� �����������", command=select_image, font=("Arial", 12), bg="#3bc43b", fg="white",
                  activebackground="#4fca4f", relief=tk.RAISED).pack(pady=5)

        def add_pizza():
            nonlocal image_path
            name = name_entry.get()
            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("������", "���� ������ ���� ������!")
                return

            if not name or not image_path:
                messagebox.showerror("������", "������� �������� ����� � �������� �����������!")
                return

            
            image_name = f"{name}_{int(time.time())}.jpg"  
            save_path = os.path.join("all_pizzas", image_name)
            shutil.copy(image_path, save_path)

            
            self.cursor.execute("INSERT INTO menu (name, price, image_path) VALUES (?, ?, ?)", (name, price, image_path))
            self.conn.commit()
            messagebox.showinfo("�����", "����� ������� ��������� � ����!")
            self.manage_menu() 

        tk.Button(frame, text="�������� �����", command=add_pizza, font=("Arial", 14), bg="#3bc43b", fg="white",
                  activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="������� � Excel", command=self.export_to_excel, font=("Arial", 14), bg="#3bc43b", fg="white",
              activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="�����", command=self.admin_screen, font=("Arial", 14), bg="#d93c3a", fg="white",
                  activebackground="#a62220", relief=tk.RAISED, width=25).pack(pady=10)

    def user_screen(self):
        """����� ������������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text=f"����� ����������, {self.current_user['name']}", font=("Arial", 20, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)
        tk.Button(frame, text="����", command=self.view_menu, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="�������", command=self.view_cart, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="������� �����", command=self.create_order, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="������ ������", command=self.view_orders_user, font=("Arial", 14), bg="#3bc43b", fg="white", activebackground="#4fca4f", relief=tk.RAISED, width=25).pack(pady=10)
        tk.Button(frame, text="�����", command=self.login_screen, font=("Arial", 14), bg="#d93c3a", fg="white", activebackground="#a62220", relief=tk.RAISED, width=25).pack(pady=10)

    def view_menu(self):
        """�������� ���� ��� ������������ � ���������� � �������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#FFFFFF", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="����", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

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
            text="�����",
            command=self.user_screen,
            font=("Arial", 14),
            bg="#d93c3a",
            fg="white",
            activebackground="#a62220",
            relief=tk.RAISED,
            width=25,
        ).pack(pady=10)


    def update_menu(self):
        """�������� ���� �� ���� ������."""
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
                    raise FileNotFoundError(f"���� �� ������: {image_path}")

                img = Image.open(image_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"������ �������� ����������� {image_path}: {e}")
                
                placeholder_path = "placeholder.jpg"  
                img = Image.open(placeholder_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

            self.image_cache.append(photo)
            img_label = tk.Label(pizza_frame, image=photo, bg="#FFFFFF")
            img_label.pack(side=tk.LEFT, padx=10)

            pizza_info = tk.Label(pizza_frame, text=f"{pizza[1]} - {pizza[2]} ���.", font=("Arial", 14), bg="#FFFFFF", fg="#333333")
            pizza_info.pack(side=tk.LEFT, padx=10)

            add_button = tk.Button(
                pizza_frame,
                text="�������� � �������",
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
        """�������� ����� � �������."""
        self.cart.append(pizza_id)
        messagebox.showinfo("�����", "����� ��������� � �������!")

    def view_cart(self):
        """�������� ������� ��� ������������ � ������������� � ������������ ��������."""
        self.clear_screen()
        frame = tk.Frame(self.root, bg="#ffffff", bd=0, relief=tk.FLAT)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="�������", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

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
                            raise FileNotFoundError(f"���� �� ������: {image_path}")

                        img = Image.open(image_path)
                        img = img.resize((100, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                    except Exception as e:
                        print(f"������ �������� ����������� {image_path}: {e}")
                        placeholder_path = "placeholder.jpg"
                        img = Image.open(placeholder_path)
                        img = img.resize((100, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)

                    self.image_cache.append(photo)
                    img_label = tk.Label(pizza_frame, image=photo, bg="#ffffff")
                    img_label.pack(side=tk.LEFT, padx=5)

                    info_label = tk.Label(pizza_frame, text=f"{pizza[0]} - {pizza[1]} ���.", font=("Arial", 14), bg="#ffffff", fg="#333333")
                    info_label.pack(side=tk.LEFT, padx=10)

                    def remove(idx=idx):
                        del self.cart[idx]
                        update_cart()

                    remove_button = tk.Button(pizza_frame, text="�������", command=remove, font=("Arial", 12),
                                              bg="#d93c3a", fg="white", activebackground="#a62220", relief=tk.RAISED)
                    remove_button.pack(side=tk.RIGHT, padx=5)

                    total_price += pizza[1]

            total_label.config(text=f"�����: {total_price} ���.")

        total_label = tk.Label(frame, text="�����: 0 ���.", font=("Arial", 14), bg="#ffffff", fg="#333333")
        total_label.pack(pady=10)

        tk.Button(frame, text="�����", command=self.user_screen, font=("Arial", 14), bg="#f44336", fg="white",
                  activebackground="#e53935", relief=tk.RAISED, width=25).pack(pady=10)

        update_cart()

    def create_order(self):
        """�������� ������ ������ �������������."""
        if not self.cart:
            messagebox.showerror("������", "���� ������� �����! �������� ����� � ������� ����� ��������� ������.")
            return

        total_price = 0
        for pizza_id in self.cart:
            self.cursor.execute("SELECT price FROM menu WHERE id=?", (pizza_id,))
            total_price += self.cursor.fetchone()[0]

        comment = simpledialog.askstring("�����������", "������� ����������� � ������ (���� ����):")

        self.cursor.execute("INSERT INTO orders (user_name, user_address, user_phone, status, total, comment) VALUES (?, ?, ?, ?, ?, ?)",
                            (self.current_user['name'], self.current_user['address'], self.current_user['phone'], "���������", total_price, comment))
        order_id = self.cursor.lastrowid

        for pizza_id in self.cart:
            self.cursor.execute("INSERT INTO order_items (order_id, pizza_id) VALUES (?, ?)", (order_id, pizza_id))

        self.conn.commit()
        self.cart = []

        messagebox.showinfo("�����", f"����� ������! ����� ���������: {total_price} ���.")
        self.user_screen()

    def view_orders_user(self):
        """�������� ������� ������ ��� ������������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#ffffff", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="���� ������", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        self.cursor.execute("SELECT * FROM orders WHERE user_name=?", (self.current_user['name'],))
        orders = self.cursor.fetchall()

        if not orders:
            tk.Label(frame, text="� ��� ��� �������.", font=("Arial", 14), bg="#ffffff").pack(pady=10)
        else:
            for order in orders:
                order_frame = tk.Frame(frame, bg="#ffffff", bd=0, relief=tk.GROOVE)
                order_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(order_frame, text=f"����� #{order[0]}", font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").pack()
                tk.Label(order_frame, text=f"������: {order[4]}", font=("Arial", 12), bg="#ffffff").pack(anchor="w")
                tk.Label(order_frame, text=f"�����������: {order[6]}", font=("Arial", 12), bg="#ffffff").pack(anchor="w")

        tk.Button(frame, text="�����", command=self.user_screen, font=("Arial", 14), bg="#f44336", fg="white",
                  activebackground="#e53935", relief=tk.RAISED, width=25).pack(pady=10)

    def view_orders_admin(self):
        """�������� ������� ��� ��������������."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#ffffff", bd=0, relief=tk.RIDGE)
        frame.pack(pady=30, padx=50, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="��� ������", font=("Arial", 24, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        self.cursor.execute("SELECT * FROM orders")
        orders = self.cursor.fetchall()

        if not orders:
            tk.Label(frame, text="��� �������.", font=("Arial", 14), bg="#ffffff").pack(pady=10)
        else:
            for order in orders:
                order_frame = tk.Frame(frame, bg="#ffffff", bd=0, relief=tk.GROOVE)
                order_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(order_frame, text=f"����� #{order[0]} ({order[1]})", font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").pack()
                tk.Label(order_frame, text=f"������: {order[4]}", font=("Arial", 12), bg="#ffffff").pack(anchor="w")
                tk.Label(order_frame, text=f"�����: {order[5]} ���.", font=("Arial", 12), bg="#ffffff").pack(anchor="w")

                def update_status(order_id, new_status):
                    self.cursor.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
                    self.conn.commit()
                    messagebox.showinfo("�����", f"������ ������ #{order_id} �������� �� '{new_status}'")
                    self.view_orders_admin()

                tk.Button(order_frame, text="���������", command=lambda oid=order[0]: update_status(oid, "���������"), font=("Arial", 12),
                          bg="#FFC107", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
                tk.Button(order_frame, text="� ����", command=lambda oid=order[0]: update_status(oid, "� ����"), font=("Arial", 12),
                          bg="#FF9800", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
                tk.Button(order_frame, text="��������", command=lambda oid=order[0]: update_status(oid, "��������"), font=("Arial", 12),
                          bg="#4CAF50", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
                tk.Button(order_frame, text="��������", command=lambda oid=order[0]: update_status(oid, "����� ��������"), font=("Arial", 12),
                          bg="#8BC34A", relief=tk.RAISED).pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="�����", command=self.admin_screen, font=("Arial", 14), bg="#f44336", fg="white",
                  activebackground="#e53935", relief=tk.RAISED, width=25).pack(pady=10)

    def clear_screen(self):
        """������� �������� ������."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_exit(self):
        self.conn.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PizzaManagementApp(root)
    root.mainloop()