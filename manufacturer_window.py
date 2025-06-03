from PyQt5.QtCore import QTimer, Qt
from mainManufacturerWindow import Ui_ManufacturerWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFrame, QApplication, QMessageBox, QHBoxLayout, QScrollArea, QPlainTextEdit, QLabel, QMainWindow, QDesktopWidget, QPushButton, QVBoxLayout, QWidget
import sys
import pymysql
import datetime

class MainManufacturerWindow(QtWidgets.QMainWindow):
    def __init__(self, manufacturer_id):
        super().__init__()
        self.manufacturer_id = manufacturer_id
        self.ui = Ui_ManufacturerWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.success_error_Type.setCurrentIndex(0)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()

        exit_button = QPushButton(self)
        exit_button.setText("X")
        exit_button.setGeometry(QtCore.QRect(self.width() - 50, 10, 40, 40))
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 50);
                color: white;
                font: 14pt "微软雅黑";
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 100);
            }
        """)
        exit_button.clicked.connect(self.close)

        self.ui.pushButton_releaseGame.clicked.connect(self.show_releasegame_page)
        self.ui.pushButton_HomePage.clicked.connect(self.show_homepage)
        self.ui.pushButton_manageGame.clicked.connect(self.show_managegame_page)

        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT ACCOUNT_NUMBER FROM manufacturer WHERE MANUFACTURER_ID = %s", (self.manufacturer_id,))
        manufacturer_name = cursor.fetchone()[0]
        self.ui.message1.setText(manufacturer_name)
        cursor.execute("SELECT COUNT(*) FROM game WHERE MANUFACTURER_ID = %s", (self.manufacturer_id,))
        game_count = int(cursor.fetchone()[0])
        self.ui.message3.setText(str(game_count))
        db.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def show_homepage(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.show()

    def show_releasegame_page(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.pushButton_releaseSure.clicked.connect(self.release_game)
        self.show()

    def show_managegame_page(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT GAME_NAME FROM game WHERE MANUFACTURER_ID = %s", (self.manufacturer_id,))
        all_gamename = cursor.fetchall()
        db.close()
        x, y = 40, 20
        for gamename in all_gamename:
            self.add_managegame_page(x, y, gamename)
            y += 80
        self.show()

    def release_game(self):
        new_gamename = self.ui.lineEdit_gameName.text()
        new_gameintroduction = self.ui.textEdit_gameIntroduction.toPlainText()
        new_gametype1 = self.ui.lineEdit_gameType1.text()
        new_gametype2 = self.ui.lineEdit_gameType2.text()
        new_gametype3 = self.ui.lineEdit_gameType3.text()
        new_gameprice = self.ui.lineEdit_gamePrice.text()
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM game WHERE GAME_NAME = %s", (new_gamename,))
            if cursor.fetchone()[0] > 0:
                self.ui.success_error_Type.setCurrentIndex(3)
                return
            if not all([new_gamename, new_gameintroduction, new_gameprice]):
                self.ui.success_error_Type.setCurrentIndex(2)
                return
            game_types = [t for t in [new_gametype1, new_gametype2, new_gametype3] if t.strip()]
            if not game_types:
                self.ui.success_error_Type.setCurrentIndex(2)
                return
            now_time = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO game (GAME_NAME, MANUFACTURER_ID, INTRODUCTION, PRICE, PUBLISH_TIME) VALUES (%s, %s, %s, %s, %s)",
                (new_gamename, self.manufacturer_id, new_gameintroduction, new_gameprice, now_time))
            game_id = cursor.lastrowid
            for gametype in game_types:
                cursor.execute("INSERT INTO game_to_type (GAME_ID, TYPE_NAME) VALUES (%s, %s)", (game_id, gametype))
            db.commit()
            self.ui.success_error_Type.setCurrentIndex(1)
        except pymysql.MySQLError as e:
            print(f"Database Error: {e}")
            db.rollback()
            self.ui.success_error_Type.setCurrentIndex(3)
        finally:
            db.close()

    def add_managegame_page(self, x, y, gamename):
        frame_applicationuser = QFrame(self.ui.scrollAreaWidgetContents_manageGame)
        frame_applicationuser.move(x, y)
        frame_applicationuser.setMinimumSize(700, 70)
        frame_applicationuser.setMaximumSize(700, 70)
        frame_applicationuser.setStyleSheet("background-color: rgb(59, 59, 89); border-radius: 8px;")
        Game_Name = QLabel(frame_applicationuser)
        Game_Name.setGeometry(QtCore.QRect(20, 15, 500, 40))
        Game_Name.setStyleSheet("font: 16pt '微软雅黑'; color: white; background: transparent;")
        display_name = str(gamename[0]) if isinstance(gamename, tuple) and len(gamename) > 0 else str(gamename)
        Game_Name.setText(display_name)
        pushButton_Delete = QPushButton(frame_applicationuser)
        pushButton_Delete.setGeometry(QtCore.QRect(550, 20, 120, 30))
        pushButton_Delete.setStyleSheet("""
            QPushButton {
                background-color: rgb(100, 180, 180);
                color: white;
                border-radius: 5px;
                font: 12pt "微软雅黑";
            }
            QPushButton:hover {
                background-color: rgb(120, 200, 200);
            }
        """)
        pushButton_Delete.clicked.connect(lambda: self.delete_game(gamename))
        pushButton_Delete.setText("下架")
        frame_applicationuser.show()

    def delete_game(self, game_name):
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT GAME_ID FROM game WHERE GAME_NAME = %s", (game_name,))
            game_id_result = cursor.fetchone()
            if game_id_result:
                game_id = game_id_result[0]
                cursor.execute("DELETE FROM evaluatetable WHERE GAME_ID = %s", (game_id,))
                cursor.execute("DELETE FROM order_details WHERE GAME_ID = %s", (game_id,))
                cursor.execute("DELETE FROM having_games WHERE GAME_ID = %s", (game_id,))
                cursor.execute("DELETE FROM game_to_type WHERE GAME_ID = %s", (game_id,))
                cursor.execute("DELETE FROM game WHERE GAME_ID = %s", (game_id,))
                db.commit()
        except pymysql.MySQLError as e:
            print(f"Database Error: {e}")
            db.rollback()
        finally:
            db.close()
        self.reload_managegame()

    def reload_managegame(self):
        for child in self.ui.scrollAreaWidgetContents_manageGame.findChildren(QWidget):
            child.deleteLater()
        QApplication.processEvents()
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT GAME_NAME FROM game WHERE MANUFACTURER_ID = %s", (self.manufacturer_id,))
        all_gamename = list(cursor.fetchall())
        db.close()
        x, y = 40, 20
        for gamename in all_gamename:
            self.add_managegame_page(x, y, gamename)
            y += 80