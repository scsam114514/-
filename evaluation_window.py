from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFrame, QApplication, QMessageBox, QHBoxLayout, QScrollArea, QPlainTextEdit, QLabel, QMainWindow, QDesktopWidget, QPushButton, QVBoxLayout, QWidget
import sys
import pymysql
import datetime

class GameEvaluationWindow(QtWidgets.QMainWindow):
    def __init__(self, game_id, game_name):
        super().__init__()
        self.game_id = game_id
        self.game_name = game_name

        self.setWindowTitle(f"{game_name} - 游戏评价")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel(f"《{game_name}》的游戏评价")
        title_label.setStyleSheet("font: 20pt '微软雅黑'; color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: rgb(59, 59, 89);")
        stats_layout = QHBoxLayout(stats_frame)
        self.total_reviews_label = QLabel("总评价数: 0")
        self.total_reviews_label.setStyleSheet("color: white;")
        stats_layout.addWidget(self.total_reviews_label)
        self.positive_rate_label = QLabel("好评率: 0%")
        self.positive_rate_label.setStyleSheet("color: white;")
        stats_layout.addWidget(self.positive_rate_label)
        stats_layout.addStretch()
        main_layout.addWidget(stats_frame)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)

        self.load_evaluations()
        self.setStyleSheet("background-color: rgb(38, 38, 38);")

    def load_evaluations(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().deleteLater()
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN SCORE = 1 THEN 1 ELSE 0 END) as positive, SUM(CASE WHEN SCORE = 0 THEN 1 ELSE 0 END) as negative FROM evaluatetable WHERE GAME_ID = %s", (self.game_id,))
        stats = cursor.fetchone()
        total = stats[0]
        positive = stats[1]
        positive_rate = round(positive / total * 100, 1) if total > 0 else 0
        self.total_reviews_label.setText(f"总评价数: {total}")
        self.positive_rate_label.setText(f"好评率: {positive_rate}%")
        cursor.execute("SELECT e.EVALUATE, e.EVALUATE_DATE, e.SCORE, u.ACCOUNT_NUMBER FROM evaluatetable e JOIN user u ON e.USER_ID = u.USER_ID WHERE e.GAME_ID = %s ORDER BY e.EVALUATE_DATE DESC", (self.game_id,))
        evaluations = cursor.fetchall()
        for eval in evaluations:
            self.add_evaluation_item(eval[3], eval[0], eval[1], eval[2])
        db.close()

    def add_evaluation_item(self, username, content, date, score):
        frame = QFrame()
        frame.setStyleSheet("background-color: rgb(59, 59, 89); border-radius: 5px;")
        frame.setMinimumHeight(120)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        user_layout = QHBoxLayout()
        user_label = QLabel(username)
        user_label.setStyleSheet("color: white; font-weight: bold;")
        user_layout.addWidget(user_label)
        user_layout.addStretch()
        date_label = QLabel(date.strftime("%Y-%m-%d %H:%M"))
        date_label.setStyleSheet("color: #AAAAAA;")
        user_layout.addWidget(date_label)
        layout.addLayout(user_layout)
        content_text = QPlainTextEdit()
        content_text.setPlainText(content)
        content_text.setReadOnly(True)
        content_text.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); color: white; border: none; padding: 5px;")
        content_text.setMaximumHeight(80)
        layout.addWidget(content_text)
        score_label = QLabel("推荐" if score == 1 else "不推荐")
        score_label.setStyleSheet("color: {};".format("#4CAF50" if score == 1 else "#F44336"))
        layout.addWidget(score_label)
        self.scroll_layout.addWidget(frame)