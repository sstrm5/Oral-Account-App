import hashlib
import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QDialogButtonBox
from PyQt6.QtCore import QCoreApplication
import sqlite3
from sql_commands import CREATE_TABLE_USERS, CREATE_TABLE_USERS_SCORES, CREATE_USER, GET_USER


class HelloWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/hello_screen.ui", self)


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/login.ui", self)


class SigninWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/signin.ui", self)


class SigninSuccessWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/signin_success.ui", self)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450, 250, 660, 660)
        # self.setFixedSize(400, 450)
        # self.setWindowIcon(QIcon("favicon.png"))
        self.user = None
        self.db_connection = sqlite3.connect('db.db')
        self.cursor = self.db_connection.cursor()
        self.cursor.execute(CREATE_TABLE_USERS)
        self.cursor.execute(CREATE_TABLE_USERS_SCORES)
        self.db_connection.commit()
        self.start_hello_frame()

    def start_hello_frame(self):
        self.hello_frame = HelloWidget(self)
        self.setWindowTitle("Устный счёт")
        self.setCentralWidget(self.hello_frame)

        if self.user:
            self.hello_frame.user_label.setText(
                f"Привет, {self.user[1]}!")
            self.hello_frame.user_quit_btn.show()
        else:
            self.hello_frame.user_label.setText("Привет, гость!")
            self.hello_frame.user_quit_btn.hide()

        self.hello_frame.start_game_btn.clicked.connect(
            self.start_game)
        self.hello_frame.login_btn.clicked.connect(
            self.start_login)
        self.hello_frame.exit_btn.clicked.connect(
            QCoreApplication.instance().quit)
        self.hello_frame.signin_btn.clicked.connect(
            self.start_signin)
        self.hello_frame.user_quit_btn.clicked.connect(
            self.user_quit)
        self.show()

    def start_game(self):
        # self.frame1.label_2.setText("Игра началась")
        ...

    def start_login(self):
        self.login_frame = LoginWidget(self)
        self.setWindowTitle("Вход")
        self.setCentralWidget(self.login_frame)

        # Подключение кнопок
        self.login_frame.back_btn.clicked.connect(
            self.start_hello_frame)
        self.login_frame.login_btn.clicked.connect(
            self.login_user)
        self.show()

    def login_user(self):
        login = self.login_frame.login_edit.text()
        password = self.login_frame.password_edit.text()

        self.cursor.execute(
            GET_USER.format(login=login))

        user = self.cursor.fetchone()
        if user:
            password_hash = user[2]
            print(password_hash)
            salt_str = password_hash[:32]
            salt_b = bytes.fromhex(salt_str)

            key = password_hash[32:]
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt_b,
                100000,
            )
            print(
                f"Соль: {salt_str}, key: {key}, new_key: {new_key.hex()}"
            )
            if new_key.hex() == key:
                self.user = user
                self.start_hello_frame()
        else:
            self.login_frame.info_label.setText(
                "Неправильный логин или пароль!")

    def start_signin(self):
        self.signin_frame = SigninWidget(self)
        self.setWindowTitle("Регистрация")
        self.setCentralWidget(self.signin_frame)

        # Подключение кнопок
        self.signin_frame.back_btn.clicked.connect(
            self.start_hello_frame)
        self.signin_frame.signin_btn.clicked.connect(
            self.signin_user)
        self.show()

    def signin_user(self):
        login = self.signin_frame.login_edit.text()
        password = self.signin_frame.password_edit.text()

        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
        )
        password_hash = f"{salt.hex()}{key.hex()}"

        # Добавление пользователя в БД
        self.cursor.execute(
            GET_USER.format(login=login))
        if self.cursor.fetchone():
            self.signin_frame.info_label.setText(
                "Такой пользователь уже существует!")
            return

        self.cursor.execute(CREATE_USER.format(
            login=login, password_hash=password_hash))
        self.db_connection.commit()
        self.dialog = SigninSuccessWidget(self)
        self.dialog.setWindowTitle("Регистрация")
        self.dialog.buttonBox.accepted.connect(self.start_login)
        self.dialog.exec()
        self.signin_frame.info_label.setText(f"Привет, {login}!")

    def user_quit(self):
        self.user = None
        self.start_hello_frame()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
