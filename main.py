import hashlib
import os
import sys
from threading import Timer
import time
from PyQt6 import uic
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QDialogButtonBox
from PyQt6.QtCore import QCoreApplication
import sqlite3
from sql_commands import CREATE_TABLE_USERS, CREATE_TABLE_USERS_SCORES, CREATE_USER, GET_USER
import game


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


class SigninSuccessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/signin_success.ui", self)


class StartGameAlertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/start_game_alert.ui", self)


class EndGameAlertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/end_game_alert.ui", self)

    def closeEvent(self, event):
        ex.start_hello_frame()


class StartGameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/game.ui", self)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450, 250, 660, 660)
        # self.setFixedSize(400, 450)
        # self.setWindowIcon(QIcon("favicon.png"))
        self.user = None
        self.alert = None
        self.end_game_alert = None
        self.timer = None
        self.total_score = 0
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
            self.hello_frame.login_btn.hide()
            self.hello_frame.signin_btn.hide()
        else:
            self.hello_frame.user_label.setText("Привет, гость!")
            self.hello_frame.user_quit_btn.hide()
            self.hello_frame.login_btn.show()
            self.hello_frame.signin_btn.show()

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

        if self.end_game_alert and self.sender() == self.end_game_alert.ok_btn:
            self.end_game_alert.hide()
        self.show()

    def generate_problem(self):
        time_limit = 20
        self.game_frame.time_left_label.setText(
            f"Ограничение по времени:\n{time_limit} сек.")
        self.timer = Timer(time_limit, self.end_game, ['problem_timer'])
        self.timer.start()
        num1, operator, num2, self.answer = game.random_problem()
        problem = f"{num1} {operator} {num2}"
        self.game_frame.problem_label.setText(problem)

    def start_game(self):
        if not self.user:
            self.alert = StartGameAlertDialog(self)
            self.alert.setWindowTitle("Предупреждение")
            self.alert.login_btn.clicked.connect(self.start_login)
            self.alert.signin_btn.clicked.connect(self.start_signin)
            self.alert.cancel_btn.clicked.connect(self.alert.hide)
            self.alert.exec()
            return
        self.game_frame = StartGameWidget(self)
        self.setWindowTitle("Устный счёт")
        self.setCentralWidget(self.game_frame)

        self.generate_problem()

        self.game_frame.exit_btn.clicked.connect(self.start_hello_frame)
        self.game_frame.check_btn.clicked.connect(self.check_answer)

    def check_answer(self):
        user_answer = self.game_frame.user_answer_edit.text()
        if user_answer.strip() == self.answer:
            self.total_score += 1
            self.game_frame.score_QLCD.display(self.total_score)
            self.game_frame.user_answer_edit.clear()
            self.generate_problem()
        else:
            self.total_score = self.game_frame.score_QLCD.intValue()
            self.end_game('check_answer')

    def end_game(self, who_called):
        self.end_game_alert = EndGameAlertDialog(self)
        self.end_game_alert.setWindowTitle("Игра окончена")
        if who_called == 'check_answer':
            self.timer.cancel()
            text = f"""Ошибка! Правильный ответ: {
                self.answer}. Вы набрали {self.total_score} очков."""
        else:
            text = f"""Время вышло! Вы набрали {self.total_score} очков."""
        self.end_game_alert.label.setText(text)
        self.end_game_alert.ok_btn.clicked.connect(
            self.start_hello_frame)
        self.end_game_alert.exec()

    def start_login(self):
        self.login_frame = LoginWidget(self)
        self.setWindowTitle("Вход")
        self.setCentralWidget(self.login_frame)

        # Подключение кнопок
        self.login_frame.back_btn.clicked.connect(
            self.start_hello_frame)
        self.login_frame.login_btn.clicked.connect(
            self.login_user)

        if self.alert and self.sender() == self.alert.login_btn:
            self.alert.hide()
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

        if self.alert and self.sender() == self.alert.signin_btn:
            self.alert.hide()
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
        self.dialog = SigninSuccessDialog(self)
        self.dialog.setWindowTitle("Регистрация")
        self.dialog.buttonBox.accepted.connect(self.start_login)
        self.dialog.exec()
        self.signin_frame.info_label.setText(f"Привет, {login}!")

    def user_quit(self):
        self.user = None
        self.start_hello_frame()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.db_connection.close()
        if self.timer:
            self.timer.cancel()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
