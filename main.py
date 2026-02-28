from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
import sqlite3
import datetime


class ExpenseApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.conn = sqlite3.connect("expenses.db")
        self.create_table()
        return MainScreen()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                type TEXT,
                date TEXT
            )
        """)
        self.conn.commit()

    def add_transaction(self, amount, category, t_type):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (amount, category, type, date)
            VALUES (?, ?, ?, ?)
        """, (amount, category, t_type, str(datetime.date.today())))
        self.conn.commit()

    def get_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        return cursor.fetchall()

    def delete_transaction(self, t_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (t_id,))
        self.conn.commit()

    def calculate_balance(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
        income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
        expense = cursor.fetchone()[0] or 0

        return income - expense


class MainScreen(MDScreen):

    def on_enter(self):
        self.refresh_ui()

    def refresh_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        app = MDApp.get_running_app()
        balance = app.calculate_balance()

        balance_card = MDCard(
            size_hint=(1, None),
            height=dp(100),
            elevation=4,
            padding=dp(20),
        )
        balance_card.add_widget(
            MDLabel(
                text=f"Total Balance: ₹{round(balance,2)}",
                halign="center",
                font_style="H5",
            )
        )
        layout.add_widget(balance_card)

        add_btn = MDRaisedButton(
            text="Add Transaction",
            pos_hint={"center_x": 0.5},
            on_release=self.open_dialog
        )
        layout.add_widget(add_btn)

        scroll = ScrollView()
        list_layout = BoxLayout(orientation="vertical", size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter("height"))

        transactions = app.get_transactions()

        for t in transactions:
            t_id, amount, category, t_type, date = t

            item = OneLineAvatarIconListItem(
                text=f"{t_type}: ₹{amount} | {category} ({date})"
            )

            delete_icon = IconRightWidget(icon="delete")
            delete_icon.bind(
                on_release=lambda x, id=t_id: self.delete_item(id)
            )

            item.add_widget(delete_icon)
            list_layout.add_widget(item)

        scroll.add_widget(list_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def open_dialog(self, instance):
        self.dialog = MDDialog(
            title="Add Transaction",
            type="custom",
            content_cls=BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(200)
            ),
            buttons=[
                MDRaisedButton(text="Save", on_release=self.save_transaction)
            ],
        )

        self.amount_field = MDTextField(
            hint_text="Amount",
            input_filter="float"
        )

        self.category_field = MDTextField(
            hint_text="Category"
        )

        self.type_field = MDTextField(
            hint_text="Income or Expense"
        )

        self.dialog.content_cls.add_widget(self.amount_field)
        self.dialog.content_cls.add_widget(self.category_field)
        self.dialog.content_cls.add_widget(self.type_field)

        self.dialog.open()

    def save_transaction(self, instance):
        amount = self.amount_field.text
        category = self.category_field.text
        t_type = self.type_field.text

        if not amount or not category or not t_type:
            return

        app = MDApp.get_running_app()
        app.add_transaction(float(amount), category, t_type)

        self.dialog.dismiss()
        self.refresh_ui()

    def delete_item(self, t_id):
        app = MDApp.get_running_app()
        app.delete_transaction(t_id)
        self.refresh_ui()


if __name__ == "__main__":
    ExpenseApp().run()