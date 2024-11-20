import hashlib
import os
import sys
from PyQt6.QtCore import QTimer, Qt
import time
from PyQt6 import uic
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QDialogButtonBox, QHeaderView, QTableWidgetItem, QButtonGroup
from PyQt6.QtCore import QCoreApplication
import sqlite3
from sql_commands import (
    CREATE_TABLE_USERS, CREATE_TABLE_USERS_SCORES, CREATE_USER, GET_USER, UPDATE_SCORES,
    GET_SCORES, GET_SCORES_SORTED_BY_TIME, GET_SCORES_SORTED_BY_USER,
    GET_SCORES_SORTED_BY_SCORE, GET_USERS)
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


class TableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/table.ui", self)


class StartGameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/game.ui", self)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(450, 250, 660, 660)
        self.setFixedSize(660, 660)
        self.user = None
        self.alert = None
        self.end_game_alert = None
        self.timer = None
        self.game_frame = None
        self.time_limit = 20
        self.time_spent = 0
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
        self.hello_frame.btn_table.clicked.connect(
            self.show_table)

        if self.end_game_alert and self.sender() == self.end_game_alert.ok_btn:
            self.end_game_alert.hide()
        if self.game_frame and self.sender() == self.game_frame.exit_btn:
            self.timer.stop()
        self.show()

    def timing(self):
        self.show_time -= 0.1
        self.show_time = round(self.show_time, 1)
        self.game_frame.time_left_label.setText(
            f"{self.show_time} сек.")
        match self.show_time:
            case 10:
                self.game_frame.time_left_label.setStyleSheet(
                    "QLabel { color : rgb(50, 0, 0); }")
            case 7:
                self.game_frame.time_left_label.setStyleSheet(
                    "QLabel { color : rgb(100, 0, 0); }")
            case 5:
                self.game_frame.time_left_label.setStyleSheet(
                    "QLabel { color : rgb(200, 0, 0); }")
            case 3.5:
                self.game_frame.time_left_label.setStyleSheet(
                    "QLabel { color : rgb(235, 0, 0); }")
            case 2:
                self.game_frame.time_left_label.setStyleSheet(
                    "QLabel { color : rgb(255, 0, 0); }")
        if self.show_time <= 0:
            self.end_game(who_called='timer')

    def generate_problem(self):
        self.show_time = self.time_limit
        self.game_frame.time_left_label.setText(
            f"{self.show_time} сек.")
        self.timer = QTimer()
        self.timer.timeout.connect(self.timing)
        self.timer.start(100)
        num1, operator, num2, self.answer = game.random_problem()
        problem = f"{num1} {operator} {num2}"
        self.game_frame.time_left_label.setStyleSheet(
            "QLabel { color : rgb(50, 0, 0)}")
        self.game_frame.problem_label.setText(problem)
        random_color = f"color: {game.random_color()}"
        self.game_frame.problem_label.setStyleSheet(
            f"QLabel {{ {random_color} }}"
        )
        self.game_frame.user_answer_edit.setFocus()

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
        self.game_frame.user_answer_edit.returnPressed.connect(
            self.check_answer)

    def check_answer(self):
        self.time_spent += self.time_limit - self.show_time
        user_answer = self.game_frame.user_answer_edit.text()
        if user_answer.strip() == self.answer:
            self.total_score += 1
            self.game_frame.score_QLCD.display(self.total_score)
            self.game_frame.score_QLCD.setStyleSheet(
                "QLCDNumber { color : rgb(0, 200, 0); }"
            )
            self.game_frame.user_answer_edit.clear()
            self.generate_problem()
        else:
            self.total_score = self.game_frame.score_QLCD.intValue()
            self.end_game('check_answer')

    def end_game(self, who_called='timer'):
        self.timer.stop()
        if self.time_spent == 0:
            self.time_spent = self.time_limit - self.show_time
        self.show_time = 0

        if who_called == 'check_answer':
            text = f"""Ошибка! Правильный ответ: {
                self.answer}. Количество набранных очков {self.total_score}."""
        else:
            text = f"""Время вышло! Количество набранных очков {
                self.total_score}."""
        self.cursor.execute(
            UPDATE_SCORES.format(user_name=self.user[1], score=self.total_score, time=round(self.time_spent, 2)))
        self.db_connection.commit()
        self.time_spent = 0
        self.end_game_alert = EndGameAlertDialog(self)
        self.end_game_alert.setWindowTitle("Игра окончена")
        self.end_game_alert.label.setText(text)
        self.end_game_alert.ok_btn.clicked.connect(
            self.start_hello_frame)
        self.end_game_alert.open_table_btn.clicked.connect(
            self.show_table)
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
        self.login_frame.login_edit.setFocus()

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
            salt_str = password_hash[:32]
            salt_b = bytes.fromhex(salt_str)

            key = password_hash[32:]
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt_b,
                100000,
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
        self.signin_frame.login_edit.setFocus()

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

    def show_table(self):
        if self.end_game_alert and self.sender() == self.end_game_alert.open_table_btn:
            self.end_game_alert.hide()
        self.table_frame = TableWidget(self)
        self.table_frame.back_btn.clicked.connect(self.start_hello_frame)
        self.table_frame.sort_btn.clicked.connect(self.sort_table)
        self.setWindowTitle("Таблица рекордов")
        self.setCentralWidget(self.table_frame)

        self.cursor.execute(GET_SCORES)
        scores = self.cursor.fetchall()

        headers = ["Имя пользователя", "Счет", "Время"]
        self.table_frame.table.setColumnCount(len(headers))
        self.table_frame.table.setRowCount(len(scores))
        self.table_frame.table.setHorizontalHeaderLabels(headers)
        self.table_frame.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        for i, score in enumerate(scores):
            self.table_frame.table.setItem(
                i, 0, QTableWidgetItem(str(score[1])))
            self.table_frame.table.setItem(
                i, 1, QTableWidgetItem(str(score[2])))
            self.table_frame.table.setItem(
                i, 2, QTableWidgetItem(str(score[3])))

    def sort_table(self):
        self.table_frame.layout = QButtonGroup()
        self.table_frame.layout.addButton(self.table_frame.rb_name)
        self.table_frame.layout.addButton(self.table_frame.rb_score)
        self.table_frame.layout.addButton(self.table_frame.rb_time)
        if self.table_frame.rb_name.isChecked():
            scores = self.cursor.execute(GET_SCORES_SORTED_BY_USER).fetchall()
        elif self.table_frame.rb_score.isChecked():
            scores = self.cursor.execute(GET_SCORES_SORTED_BY_SCORE).fetchall()
        elif self.table_frame.rb_time.isChecked():
            scores = self.cursor.execute(GET_SCORES_SORTED_BY_TIME).fetchall()
        else:
            scores = self.cursor.execute(GET_SCORES).fetchall()
        for i, score in enumerate(scores):
            self.table_frame.table.setItem(
                i, 0, QTableWidgetItem(str(score[1])))
            self.table_frame.table.setItem(
                i, 1, QTableWidgetItem(str(score[2])))
            self.table_frame.table.setItem(
                i, 2, QTableWidgetItem(str(score[3])))

    def user_quit(self):
        self.user = None
        self.start_hello_frame()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.start_hello_frame()
        elif event.key() == Qt.Key.Key_Enter:
            if self.sender() in (self.game_frame.check_btn, self.game_frame.user_answer_edit):
                self.check_answer()
            elif self.sender() == self.login_frame.login_edit:
                self.login_frame.password_edit.setFocus()
            elif self.sender() == self.signin_frame.signin_edit:
                self.signin_frame.password_edit.setFocus()
            elif self.sender() == self.end_game_alert.ok_btn:
                self.start_hello_frame()
            elif self.sender() == self.end_game_alert.open_table_btn:
                self.show_table()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.db_connection.close()
        if self.timer:
            self.timer.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
