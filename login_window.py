from PyQt5.QtCore import QTimer, Qt
from LogIn import Ui_LRMainWindow
from user_window import MainUserWindow
from manufacturer_window import MainManufacturerWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFrame, QApplication, QMessageBox, QHBoxLayout, QScrollArea, QPlainTextEdit, QLabel, QMainWindow, QDesktopWidget, QPushButton, QVBoxLayout, QWidget
import sys
import pymysql
import datetime

class LogInWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LRMainWindow()
        self.ui.setupUi(self)
        self.flag = 0  # 0 for user, 1 for manufacturer

        # Set window properties
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()

        # Add exit button
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

        # Button connections
        self.ui.pushButton_switch.clicked.connect(lambda: self.switch_page(self.flag))
        self.ui.pushButton_LogIn.clicked.connect(lambda: self.ui.stackedWidget_LR.setCurrentIndex(self.flag))
        self.ui.pushButton_Register.clicked.connect(lambda: self.ui.stackedWidget_LR.setCurrentIndex(self.flag + 2))
        self.ui.pushButton_L_Sure.clicked.connect(self.log_in)
        self.ui.pushButton_L_Sure_manufacturer.clicked.connect(self.log_in)
        self.ui.pushButton_User_R_Sure.clicked.connect(self.register)
        self.ui.pushButton_Manufacturer_R_Sure.clicked.connect(self.register)

        # Initialize status
        self.ui.success_error_Type.setCurrentIndex(0)
        self.show()

    def switch_page(self, pageid):
        self.flag = (pageid + 1) % 2
        self.ui.stackedWidget_LR.setCurrentIndex(self.flag)

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def log_in(self):
        self.ui.success_error_Type.setCurrentIndex(0)
        if self.flag == 0:
            account_number = self.ui.lineEdit_L_AccountNumber.text()
            password = self.ui.lineEdit_L_Password.text()
            if account_number:
                try:
                    db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
                    cursor = db.cursor()
                    cursor.execute("SELECT USER_ID, ACCOUNT_NUMBER, PASSWORD FROM user WHERE ACCOUNT_NUMBER = %s",
                                   (account_number,))
                    result = cursor.fetchone()
                    if not result:
                        self.ui.success_error_Type.setCurrentIndex(3)
                    elif result[2] == password:
                        user_id = str(result[0])
                        self.ui.success_error_Type.setCurrentIndex(1)
                        self.win = MainUserWindow(user_id)
                        self.win.show()
                        self.close()
                    else:
                        self.ui.success_error_Type.setCurrentIndex(3)
                except pymysql.MySQLError as e:
                    print(f"Database Error: {e}")
                    self.ui.success_error_Type.setCurrentIndex(3)
                finally:
                    db.close()
        elif self.flag == 1:
            account_number = self.ui.lineEdit_L_AccountNumber_manufacture.text()
            password = self.ui.lineEdit_L_Password_manufacturer.text()
            if account_number:
                try:
                    db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
                    cursor = db.cursor()
                    cursor.execute("SELECT MANUFACTURER_ID, ACCOUNT_NUMBER, PASSWORD FROM manufacturer WHERE ACCOUNT_NUMBER = %s",
                                   (account_number,))
                    result = cursor.fetchone()
                    if not result:
                        self.ui.success_error_Type.setCurrentIndex(3)
                    elif result[2] == password:
                        manufacturer_id = str(result[0])
                        self.ui.success_error_Type.setCurrentIndex(1)
                        self.win = MainManufacturerWindow(manufacturer_id)
                        self.win.show()
                        self.close()
                    else:
                        self.ui.success_error_Type.setCurrentIndex(3)
                except pymysql.MySQLError as e:
                    print(f"Database Error: {e}")
                    self.ui.success_error_Type.setCurrentIndex(3)
                finally:
                    db.close()

    def register(self):
        self.ui.success_error_Type.setCurrentIndex(0)
        if self.flag == 0:
            new_account_number = self.ui.lineEdit_User_R_AccountNumber.text()
            new_password = self.ui.lineEdit_User_R_Password.text()
            new_check_password = self.ui.lineEdit_User_R_CheckPassword.text()
            if len(new_account_number) > 10 or len(new_password) > 20 or not new_account_number or not new_password:
                self.ui.success_error_Type.setCurrentIndex(4)
                return
            elif new_password != new_check_password:
                self.ui.success_error_Type.setCurrentIndex(6)
                return
            try:
                db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
                cursor = db.cursor()
                cursor.execute("SELECT * FROM user WHERE ACCOUNT_NUMBER = %s", (new_account_number,))
                if cursor.fetchall():
                    self.ui.success_error_Type.setCurrentIndex(5)
                else:
                    cursor.execute("INSERT INTO user (ACCOUNT_NUMBER, PASSWORD) VALUES (%s, %s)",
                                   (new_account_number, new_password))
                    db.commit()
                    self.ui.success_error_Type.setCurrentIndex(2)
                    QTimer.singleShot(1000, lambda: self.ui.stackedWidget_LR.setCurrentIndex(0))
            except pymysql.MySQLError as e:
                print(f"Database Error: {e}")
                self.ui.success_error_Type.setCurrentIndex(3)
            finally:
                db.close()
        elif self.flag == 1:
            new_account_number = self.ui.lineEdit_Manufacturer_R_AccountNumber.text()
            new_password = self.ui.lineEdit_Manufacturer_R_Password.text()
            new_check_password = self.ui.lineEdit_Manufacturer_R_CheckPassword.text()
            if len(new_account_number) > 18 or len(new_password) > 20 or not new_account_number or not new_password:
                self.ui.success_error_Type.setCurrentIndex(4)
                return
            elif new_password != new_check_password:
                self.ui.success_error_Type.setCurrentIndex(6)
                return
            try:
                db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
                cursor = db.cursor()
                cursor.execute("SELECT * FROM manufacturer WHERE ACCOUNT_NUMBER = %s", (new_account_number,))
                if cursor.fetchall():
                    self.ui.success_error_Type.setCurrentIndex(5)
                else:
                    cursor.execute("INSERT INTO manufacturer (ACCOUNT_NUMBER, PASSWORD) VALUES (%s, %s)",
                                   (new_account_number, new_password))
                    db.commit()
                    self.ui.success_error_Type.setCurrentIndex(1)
                    QTimer.singleShot(1000, lambda: self.ui.stackedWidget_LR.setCurrentIndex(1))
            except pymysql.MySQLError as e:
                print(f"Database Error: {e}")
                self.ui.success_error_Type.setCurrentIndex(3)
            finally:
                db.close()