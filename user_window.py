from PyQt5.QtCore import QTimer, Qt
from testwindow import Ui_testwindow
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFrame, QApplication, QMessageBox, QHBoxLayout, QScrollArea, QPlainTextEdit, QLabel, QMainWindow, QDesktopWidget, QPushButton, QVBoxLayout, QWidget
import sys
import pymysql
import datetime

class MainUserWindow(QtWidgets.QMainWindow):
    new_game_score = 1  # 新游戏评分默认值
    evaluation_frames = []  # 存储评价框架的列表
    test01 = 0  # 测试变量

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id  # 保存用户ID
        self.ui = Ui_testwindow()  # 初始化UI
        self.ui.setupUi(self)
        self.ui.stackedWidget_Window.setCurrentIndex(0)  # 设置主窗口默认页面

        # 设置无边框窗口并启用透明背景
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()  # 窗口居中

        # 一次性连接所有按钮信号
        self.ui.pushButton_ShowUserFriends.clicked.connect(self.show_personal_friends_page)
        self.ui.pushButton_ShowAddFriend.clicked.connect(
            lambda: self.ui.stackedWidget_userFriendPage.setCurrentIndex(1))
        self.ui.pushButton_search.clicked.connect(self.show_addfriend_page)
        self.ui.pushButton_ShowApplication.clicked.connect(self.show_application_page)
        self.ui.pushButton_SearchGame.clicked.connect(self.show_searchgame_page)
        self.ui.lineEdit_SearchGame.returnPressed.connect(self.show_searchgame_page)
        self.ui.pushButton_GoMainPage.clicked.connect(self.show_allgames_page)
        self.ui.pushButton_GoFriendPage.clicked.connect(self.show_personal_friends_page)
        self.ui.pushButton_GoGameLibraryPage.clicked.connect(self.show_personal_gamelibrary_page)
        self.ui.pushButton_GoShoppingCartPage.clicked.connect(self.show_personal_shoppingcart_page)
        self.ui.pushButton_KeepShopping.clicked.connect(self.show_allgames_page)  # 继续购物按钮
        self.ui.pushButton_Pay.clicked.connect(self.pay_for_game)  # 支付按钮信号连接

        # 创建退出按钮
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

        # 设置滚动区域布局
        self.scrollAreaLayout = QVBoxLayout(self.ui.scrollAreaWidgetContents_3)
        self.ui.scrollAreaWidgetContents_3.setLayout(self.scrollAreaLayout)

        # 获取用户名并设置到个人页面按钮
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT ACCOUNT_NUMBER FROM user WHERE USER_ID = %s", (self.user_id,))
        user_name = cursor.fetchone()
        db.close()

        if user_name:
            self.ui.pushButton_GoPersonalPage.setText(user_name[0])
        else:
            print("未找到对应ID的用户")

        self.show_allgames_page()  # 显示所有游戏页面
        self.show()  # 显示窗口

    def center(self):
        """将窗口居中显示"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def show_allgames_page(self):
        """显示所有游戏页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(0)
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM game")
        game_count = int(cursor.fetchone()[0])
        cursor.execute("SELECT GAME_NAME, introduction, price FROM game")
        all_game = cursor.fetchall()
        db.close()

        x, y = 207, 180
        for i in range(game_count):
            self.add_page(x, y, all_game[i][0], all_game[i][1], all_game[i][2])
            y += 160

    def add_page(self, x, y, name, introduction, cost):
        """添加游戏页面到滚动区域"""
        frame = QFrame(parent=self.ui.scrollAreaWidgetContents)
        frame.move(x, y)
        frame.setMinimumSize(615, 150)
        frame.setMaximumSize(615, 150)
        frame.setStyleSheet("background-color: rgb(59, 59, 89);")
        layoutWidget = QWidget(frame)
        layoutWidget.setGeometry(QtCore.QRect(0, 0, 615, 150))
        game_frame = QVBoxLayout(layoutWidget)
        game_frame.setContentsMargins(3, 3, 3, 3)

        Game_Name = QPushButton(layoutWidget)
        Game_Name.setStyleSheet("""
            QPushButton {
                background-color: rgb(255, 255, 255,20);
                font: 15pt "微软雅黑";
                color: rgb(255, 255, 255);
                text-align: left;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: rgb(200, 200, 255);
                text-decoration: underline;
            }
        """)
        Game_Name.setText(name)
        Game_Name.clicked.connect(lambda: self.evaluate_game_page(name))
        game_frame.addWidget(Game_Name)

        Game_Introduction = QPlainTextEdit(layoutWidget)
        Game_Introduction.setReadOnly(True)
        Game_Introduction.setStyleSheet("""
            background-color: rgb(255, 255, 255,20);
            font: 10pt "微软雅黑";
            color: rgb(255, 255, 255);
            border:none;
        """)
        Game_Introduction.setPlainText(introduction)
        game_frame.addWidget(Game_Introduction)

        horizontalLayout_2 = QHBoxLayout()
        for _ in range(3):
            btn = QPushButton(layoutWidget)
            btn.setStyleSheet("color: rgb(229, 255, 255); background-color: rgba(255, 255, 255, 50);")
            btn.setText("")
            horizontalLayout_2.addWidget(btn)

        label_6 = QLabel(layoutWidget)
        label_6.setStyleSheet("font: 9pt '黑体'; color:rgb(255, 255, 255);")
        label_6.setText(str(cost))
        horizontalLayout_2.addWidget(label_6)

        pushButton = QPushButton(layoutWidget)
        pushButton.setStyleSheet("background-color: rgb(92, 138, 0); color: rgb(255, 255, 255);")
        pushButton.setText("加入购物车")
        pushButton.clicked.connect(lambda: self.add_game_to_shoppingcart(name, self.user_id))
        horizontalLayout_2.addWidget(pushButton)
        game_frame.addLayout(horizontalLayout_2)

    def add_game_to_shoppingcart(self, game_name, user_id):
        """将游戏添加到购物车"""
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            cursor.execute("SELECT GAME_ID FROM having_games WHERE USER_ID = %s", (user_id,))
            all_having_games_ids = [id[0] for id in cursor.fetchall()]
            cursor.execute("SELECT GAME_ID FROM game WHERE GAME_NAME = %s", (game_name,))
            game_id = cursor.fetchone()
            if game_id and game_id[0] in all_having_games_ids:
                QMessageBox.warning(self, "提示", f"游戏 {game_name} 已在您的游戏库中，无法添加至购物车。")
                return
            cursor.execute("SELECT ORDER_ID FROM order_for_goods WHERE USER_ID = %s AND ORDER_STATE = 0", (user_id,))
            order_id = cursor.fetchone()
            if order_id:
                cursor.execute("SELECT 1 FROM order_details WHERE ORDER_ID = %s AND GAME_ID = %s",
                               (order_id[0], game_id[0]))
                if not cursor.fetchone():
                    now_date = datetime.datetime.now()
                    cursor.execute(
                        "INSERT INTO order_details (ORDER_ID, GAME_ID, DETAIL_TIME, BUY_OR_REFUND) VALUES (%s, %s, %s, 0)",
                        (order_id[0], game_id[0], now_date))
                    db.commit()
                    QMessageBox.information(self, "提示", f"游戏 {game_name} 已成功添加到购物车！")
            else:
                now_date = datetime.datetime.now()
                cursor.execute("INSERT INTO order_for_goods (USER_ID, ORDER_STATE, ORDER_TIME) VALUES (%s, 0, %s)",
                               (user_id, now_date))
                cursor.execute(
                    "SELECT ORDER_ID FROM order_for_goods WHERE USER_ID = %s AND ORDER_STATE = 0 ORDER BY ORDER_ID DESC LIMIT 1",
                    (user_id,))
                new_order_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO order_details (ORDER_ID, GAME_ID, DETAIL_TIME, BUY_OR_REFUND) VALUES (%s, %s, %s, 0)",
                    (new_order_id, game_id[0], now_date))
                db.commit()
                QMessageBox.information(self, "提示", f"游戏 {game_name} 已成功添加到购物车！")

    def pay_for_game(self):
        """处理支付逻辑"""
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            try:
                # 检查是否存在未支付订单
                cursor.execute("SELECT ORDER_ID FROM order_for_goods WHERE USER_ID = %s AND ORDER_STATE = 0", (self.user_id,))
                order_id = cursor.fetchone()
                if not order_id:
                    QMessageBox.warning(self, "提示", "没有未支付的订单！")
                    return
                order_id = order_id[0]
                # 检查购物车是否为空
                cursor.execute("SELECT GAME_ID FROM order_details WHERE ORDER_ID = %s AND BUY_OR_REFUND = 0",
                               (order_id,))
                purchased_game_ids = cursor.fetchall()
                if not purchased_game_ids:
                    QMessageBox.warning(self, "提示", "购物车为空，无法支付！")
                    return
                # 更新订单详情和订单状态
                for game_id in purchased_game_ids:
                    cursor.execute(
                        "UPDATE order_details SET BUY_OR_REFUND = 1 WHERE GAME_ID = %s AND BUY_OR_REFUND = 0 AND ORDER_ID = %s",
                        (game_id[0], order_id))
                cursor.execute(
                    "UPDATE order_for_goods SET ORDER_STATE = 1 WHERE USER_ID = %s AND ORDER_STATE = 0 AND ORDER_ID = %s",
                    (self.user_id, order_id))
                # 将游戏添加到用户游戏库
                now_time = datetime.datetime.now()
                for game_id in purchased_game_ids:
                    cursor.execute("INSERT IGNORE INTO having_games (USER_ID, GAME_ID, BUY_TIME) VALUES (%s, %s, %s)",
                                   (self.user_id, game_id[0], now_time))
                db.commit()
                QMessageBox.information(self, "提示", "支付成功，游戏已添加到您的游戏库！")
                # 刷新购物车
                QTimer.singleShot(0, lambda: self.reload_shopping_cart(order_id))
            except Exception as e:
                db.rollback()
                QMessageBox.warning(self, "错误", f"支付失败: {str(e)}")
                print(f"支付过程中发生错误: {e}")

    def remove_games_from_shoppingcart(self, order_id, game_name):
        """从购物车移除游戏"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT GAME_ID FROM game WHERE GAME_NAME = %s", (game_name,))
            game_id_result = cursor.fetchone()
            if game_id_result:
                game_id = game_id_result[0]
                cursor.execute("DELETE FROM order_details WHERE ORDER_ID = %s AND GAME_ID = %s", (order_id, game_id))
                db.commit()
                QMessageBox.information(self, "提示", f"游戏 {game_name} 已从购物车移除！")
        except Exception as e:
            print(f"移除游戏时发生错误: {e}")
            db.rollback()
            QMessageBox.warning(self, "错误", f"移除游戏失败: {e}")
        finally:
            db.close()
        QTimer.singleShot(0, lambda: self.reload_shopping_cart(order_id))

    def remove_games_from_gamelirary(self, game_name):
        """从游戏库移除游戏"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT GAME_ID FROM game WHERE GAME_NAME = %s", (game_name,))
            game_id_result = cursor.fetchone()
            if game_id_result:
                game_id = game_id_result[0]
                cursor.execute("DELETE FROM having_games WHERE USER_ID = %s AND GAME_ID = %s", (self.user_id, game_id))
                now_date = datetime.datetime.now()
                cursor.execute("INSERT INTO order_for_goods (USER_ID, ORDER_STATE, ORDER_TIME) VALUES (%s, 0, %s)",
                               (self.user_id, now_date))
                cursor.execute(
                    "SELECT ORDER_ID FROM order_for_goods WHERE USER_ID = %s AND ORDER_STATE = 0 ORDER BY ORDER_ID DESC LIMIT 1",
                    (self.user_id,))
                new_order_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO order_details (ORDER_ID, GAME_ID, DETAIL_TIME, BUY_OR_REFUND) VALUES (%s, %s, %s, 2)",
                    (new_order_id, game_id, now_date))
                cursor.execute(
                    "UPDATE order_for_goods SET ORDER_STATE = 1 WHERE USER_ID = %s AND ORDER_STATE = 0 AND ORDER_ID = %s",
                    (self.user_id, new_order_id))
                db.commit()
                QMessageBox.information(self, "提示", f"游戏 {game_name} 已从游戏库移除！")
                self.reload_gamelibrary()
        except Exception as e:
            print(f"删除游戏时发生错误: {e}")
            db.rollback()
            QMessageBox.warning(self, "错误", f"移除游戏失败: {e}")
        finally:
            db.close()

    def show_searchgame_page(self):
        """显示搜索游戏页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(1)
        for widget in self.ui.scrollAreaWidgetContents_3.findChildren(QWidget):
            widget.deleteLater()
        QApplication.processEvents()
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            keyword = self.ui.lineEdit_SearchGame.text()
            cursor.execute("SELECT COUNT(*) FROM game WHERE GAME_NAME LIKE %s", ('%' + keyword + '%',))
            game_count = int(cursor.fetchone()[0])
            cursor.execute("SELECT GAME_NAME, introduction, price FROM game WHERE GAME_NAME LIKE %s",
                           ('%' + keyword + '%',))
            all_game = cursor.fetchall()
            nx, ny = 207, 180
            for game in all_game:
                self.add_searched_page(nx, ny, game[0], game[1], game[2])
                ny += 160

    def add_searched_page(self, x, y, name, introduction, cost):
        """添加搜索到的游戏页面"""
        frame = QFrame(parent=self.ui.scrollAreaWidgetContents_3)
        frame.move(x, y)
        frame.setMinimumSize(615, 150)
        frame.setMaximumSize(615, 150)
        frame.setStyleSheet("background-color: rgb(59, 59, 89);")
        layoutWidget = QWidget(frame)
        layoutWidget.setGeometry(QtCore.QRect(0, 0, 615, 150))
        game_frame = QVBoxLayout(layoutWidget)
        game_frame.setContentsMargins(3, 3, 3, 3)

        Game_Name = QPushButton(layoutWidget)
        Game_Name.setStyleSheet("""
            QPushButton {
                background-color: rgb(255, 255, 255,20);
                font: 15pt "微软雅黑";
                color:

 rgb(255, 255, 255);
                text-align: left;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: rgb(200, 200, 255);
                text-decoration: underline;
            }
        """)
        Game_Name.setText(name)
        Game_Name.clicked.connect(lambda: self.evaluate_game_page(name))
        game_frame.addWidget(Game_Name)

        Game_Introduction = QPlainTextEdit(layoutWidget)
        Game_Introduction.setReadOnly(True)
        Game_Introduction.setStyleSheet("""
            background-color: rgb(255, 255, 255,20);
            font: 10pt "微软雅黑";
            color: rgb(255, 255, 255);
            border:none;
        """)
        Game_Introduction.setPlainText(introduction)
        game_frame.addWidget(Game_Introduction)

        horizontalLayout_2 = QHBoxLayout()
        for _ in range(3):
            btn = QPushButton(layoutWidget)
            btn.setStyleSheet("color: rgb(229, 255, 255); background-color: rgba(255, 255, 255, 50);")
            btn.setText("")
            horizontalLayout_2.addWidget(btn)

        label_6 = QLabel(layoutWidget)
        label_6.setStyleSheet("font: 9pt '黑体'; color:rgb(255, 255, 255);")
        label_6.setText(str(cost))
        horizontalLayout_2.addWidget(label_6)

        pushButton = QPushButton(layoutWidget)
        pushButton.setStyleSheet("background-color: rgb(92, 138, 0); color: rgb(255, 255, 255);")
        pushButton.setText("加入购物车")
        pushButton.clicked.connect(lambda: self.add_game_to_shoppingcart(name, self.user_id))
        horizontalLayout_2.addWidget(pushButton)
        game_frame.addLayout(horizontalLayout_2)
        frame.show()

    def show_personal_friends_page(self):
        """显示个人好友页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(2)
        self.ui.stackedWidget_userFriendPage.setCurrentIndex(0)

        for widget in self.ui.scrollAreaWidgetContents_2.findChildren(QWidget):
            widget.deleteLater()

        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT ACCOUNT_NUMBER FROM user WHERE USER_ID = %s", (self.user_id,))
            user_name = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM friend WHERE USER_ID = %s", (self.user_id,))
            friend_count = int(cursor.fetchone()[0])
            cursor.execute(
                "SELECT u.ACCOUNT_NUMBER FROM friend f JOIN user u ON f.FRIEND_ID = u.USER_ID WHERE f.USER_ID = %s AND f.STATE = 1",
                (self.user_id,))
            all_friend = list(cursor.fetchall())

            x, y = 17, 10
            if all_friend:
                for i in range(friend_count):
                    self.add_user_friends(x, y, all_friend[i][0])
                    x += 267
            self.ui.label_Show_UserName.setText(user_name[0] if user_name else "")
        except Exception as e:
            print(f"显示好友页面时出错: {e}")
        finally:
            db.close()

    def add_user_friends(self, x, y, name):
        """添加好友到好友列表"""
        frame_Friend = QFrame(parent=self.ui.scrollAreaWidgetContents_2)
        frame_Friend.move(x, y)
        frame_Friend.setMinimumSize(250, 80)
        frame_Friend.setMaximumSize(250, 80)
        frame_Friend.setStyleSheet("background-color: rgb(128, 134, 255);")

        pushButton_Friend = QPushButton(frame_Friend)
        pushButton_Friend.setGeometry(QtCore.QRect(10, 10, 60, 60))
        pushButton_Friend.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/u=772358879,2131786806&fm=253&fmt=auto&app=138&f=JPEG.webp"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        pushButton_Friend.setIcon(icon)
        pushButton_Friend.setIconSize(QtCore.QSize(60, 60))
        pushButton_Friend.clicked.connect(lambda: self.show_friend_page(name))

        label_FriendName = QLabel(frame_Friend)
        label_FriendName.setGeometry(QtCore.QRect(90, 30, 141, 21))
        label_FriendName.setText(name)

        pushButton_Delete = QPushButton(frame_Friend)
        pushButton_Delete.setGeometry(QtCore.QRect(170, 50, 75, 20))
        pushButton_Delete.setStyleSheet("background-color: rgb(154, 231, 231); color: rgb(255, 255, 255);")
        pushButton_Delete.setText("删除好友")
        pushButton_Delete.clicked.connect(lambda: self.delete_friend(name))

        frame_Friend.show()

    def delete_friend(self, friend_name):
        """删除好友"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT USER_ID FROM user WHERE ACCOUNT_NUMBER = %s", (friend_name,))
            friend_id_result = cursor.fetchone()
            if not friend_id_result:
                QMessageBox.warning(self, "提示", f"用户 {friend_name} 不存在")
                return
            friend_id = friend_id_result[0]
            cursor.execute("DELETE FROM friend WHERE USER_ID = %s AND FRIEND_ID = %s AND STATE = 1",
                           (self.user_id, friend_id))
            cursor.execute("DELETE FROM friend WHERE USER_ID = %s AND FRIEND_ID = %s AND STATE = 1",
                           (friend_id, self.user_id))
            db.commit()
            QMessageBox.information(self, "提示", f"已删除好友 {friend_name}")
        except Exception as e:
            print(f"删除好友时出错: {e}")
            db.rollback()
            QMessageBox.warning(self, "错误", f"删除好友失败: {e}")
        finally:
            db.close()
        QTimer.singleShot(0, self.show_personal_friends_page)

    def show_friend_page(self, friend_name):
        """显示好友详情页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(3)
        self.ui.label_Show_FriendName.setText(friend_name)

    def show_addfriend_page(self):
        """显示添加好友页面"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        new_searched_friendname = self.ui.lineEdit_addSearchName.text()
        cursor.execute("SELECT USER_ID FROM user WHERE ACCOUNT_NUMBER = %s", (new_searched_friendname,))
        new_friend_id = cursor.fetchone()
        if new_friend_id:
            cursor.execute("SELECT COUNT(*) FROM friend WHERE FRIEND_ID = %s AND USER_ID = %s AND STATE = 0",
                           (new_friend_id[0], self.user_id))
            if not cursor.fetchone()[0]:
                x, y = 100, 50
                self.add_searched_friend_page(x, y, new_searched_friendname)
        db.close()

    def add_searched_friend_page(self, x, y, friend_name):
        """添加搜索到的好友页面"""
        frame_Friend = QFrame(parent=self.ui.frame_showSearchedPage)
        frame_Friend.move(x, y)
        frame_Friend.setMinimumSize(440, 200)
        frame_Friend.setMaximumSize(440, 200)
        frame_Friend.setStyleSheet("background-color: rgb(128, 134, 255);")
        pushButton_Friend = QPushButton(frame_Friend)
        pushButton_Friend.setGeometry(QtCore.QRect(310, 50, 100, 100))
        pushButton_Friend.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/u=772358879,2131786806&fm=253&fmt=auto&app=138&f=JPEG.webp"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        pushButton_Friend.setIcon(icon)
        pushButton_Friend.setIconSize(QtCore.QSize(100, 100))
        pushButton_Friend.clicked.connect(lambda: self.safe_add_friend_request(friend_name))
        label_FriendName = QLabel(frame_Friend)
        label_FriendName.setGeometry(QtCore.QRect(30, 50, 300, 100))
        label_FriendName.setText(friend_name)
        frame_Friend.show()

    def safe_add_friend_request(self, friend_name):
        """安全添加好友请求"""
        try:
            self.add_user_friendrequest(friend_name)
        except Exception as e:
            print(f"添加好友请求时出错: {e}")

    def add_user_friendrequest(self, new_friend_name):
        """发送好友请求"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT USER_ID FROM user WHERE ACCOUNT_NUMBER = %s", (new_friend_name,))
        new_friend_id = cursor.fetchone()
        if not new_friend_id:
            QMessageBox.warning(self, "提示", f"用户 {new_friend_name} 不存在")
            return
        new_friend_id = new_friend_id[0]
        cursor.execute("SELECT STATE FROM friend WHERE USER_ID = %s AND FRIEND_ID = %s", (self.user_id, new_friend_id))
        existing_relation = cursor.fetchone()
        if existing_relation:
            if existing_relation[0] == 1:
                QMessageBox.information(self, "提示", "你们已经是好友了")
            elif existing_relation[0] == 0:
                QMessageBox.information(self, "提示", "好友申请已存在")
            return
        cursor.execute("INSERT INTO friend (USER_ID, FRIEND_ID, STATE) VALUES (%s, %s, 0)", (self.user_id, new_friend_id))
        db.commit()
        QMessageBox.information(self, "提示", f"已向 {new_friend_name} 发送好友申请")
        db.close()

    def show_friend_games(self, friend_name):
        """显示好友游戏库"""
        for widget in self.ui.scrollAreaWidgetContents_GameLibrary.findChildren(QWidget):
            widget.deleteLater()
        QApplication.processEvents()
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT USER_ID FROM user WHERE ACCOUNT_NUMBER = %s", (friend_name,))
        friend_id = cursor.fetchone()
        if friend_id:
            cursor.execute("SELECT g.GAME_NAME FROM having_games hg JOIN game g ON hg.GAME_ID = g.GAME_ID WHERE hg.USER_ID = %s", (friend_id[0],))
            friend_games = cursor.fetchall()
            x, y = 20, 20
            for game in friend_games:
                self.add_friend_game(x, y, game[0])
                y += 90
            self.ui.stackedWidget_Window.setCurrentIndex(4)
            self.ui.label_Show_UserName_2.setText(f"{friend_name}的游戏库")
        db.close()

    def add_friend_game(self, x, y, game_name):
        """添加好友游戏到游戏库显示"""
        frame_gamelibrary = QFrame(self.ui.scrollAreaWidgetContents_GameLibrary)
        frame_gamelibrary.move(x, y)
        frame_gamelibrary.setMinimumSize(506, 70)
        frame_gamelibrary.setMaximumSize(506, 70)
        frame_gamelibrary.setStyleSheet("background-color: rgb(59, 59, 89);")
        Game_Name = QLabel(frame_gamelibrary)
        Game_Name.setGeometry(QtCore.QRect(3, 3, 500, 26))
        Game_Name.setStyleSheet("background-color: rgb(255, 255, 255,20); font: 15pt '微软雅黑'; color: rgb(255, 255, 255);")
        Game_Name.setText(game_name)
        frame_gamelibrary.show()

    def show_application_page(self):
        """显示好友申请页面"""
        self.ui.stackedWidget_userFriendPage.setCurrentIndex(2)
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT u.ACCOUNT_NUMBER FROM friend f JOIN user u ON f.USER_ID = u.USER_ID WHERE f.FRIEND_ID = %s AND STATE = 0", (self.user_id,))
        user_names = cursor.fetchall()
        db.close()
        x, y = 40, 20
        for user in user_names:
            self.add_application_user(x, y, user[0])
            y += 80

    def add_application_user(self, x, y, username):
        """添加好友申请用户到显示区域"""
        frame_applicationuser = QFrame(self.ui.scrollAreaWidgetContents_applicationUser)
        frame_applicationuser.move(x, y)
        frame_applicationuser.setMinimumSize(700, 70)
        frame_applicationuser.setMaximumSize(700, 70)
        frame_applicationuser.setStyleSheet("background-color: rgb(59, 59, 89);")
        User_Name = QLabel(frame_applicationuser)
        User_Name.setGeometry(QtCore.QRect(3, 3, 700, 30))
        User_Name.setStyleSheet("background-color: rgb(255, 255, 255,20); font: 15pt '微软雅黑'; color: rgb(255, 255, 255);")
        User_Name.setText(username)
        pushButton_Agree = QPushButton(frame_applicationuser)
        pushButton_Agree.setGeometry(QtCore.QRect(530, 40, 75, 20))
        pushButton_Agree.setStyleSheet("background-color: rgb(92, 138, 0); color: rgb(255, 255, 255);")
        pushButton_Agree.clicked.connect(lambda: self.agree_friend(username))
        pushButton_Agree.setText("通过")
        pushButton_Reject = QPushButton(frame_applicationuser)
        pushButton_Reject.setGeometry(QtCore.QRect(625, 40, 75, 20))
        pushButton_Reject.setStyleSheet("background-color: rgb(154, 231, 231); color: rgb(255, 255, 255);")
        pushButton_Reject.clicked.connect(lambda: self.disagree_friend(username))
        pushButton_Reject.setText("拒绝")
        frame_applicationuser.show()

    def agree_friend(self, friendname):
        """同意好友请求"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT USER_ID FROM user WHERE ACCOUNT_NUMBER = %s", (friendname,))
            friend_id = cursor.fetchone()
            if not friend_id:
                QMessageBox.warning(self, "提示", f"用户 {friendname} 不存在")
                return
            friend_id = friend_id[0]
            cursor.execute("UPDATE friend SET STATE = 1 WHERE FRIEND_ID = %s AND USER_ID = %s",
                           (self.user_id, friend_id))
            cursor.execute("INSERT INTO friend (FRIEND_ID, USER_ID, STATE) VALUES (%s, %s, 1)",
                           (friend_id, self.user_id))
            db.commit()
        except Exception as e:
            print(f"接受好友请求时出错: {e}")
            db.rollback()
        finally:
            db.close()
        QTimer.singleShot(0, self.reload_application)

    def reload_application(self):
        """重新加载好友申请页面"""
        for child in self.ui.scrollAreaWidgetContents_applicationUser.findChildren(QWidget):
            child.deleteLater()

        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT u.ACCOUNT_NUMBER FROM friend f JOIN user u ON f.USER_ID = u.USER_ID WHERE f.FRIEND_ID = %s AND STATE = 0",
                (self.user_id,))
            user_names = cursor.fetchall()
            x, y = 40, 20
            for user in user_names:
                self.add_application_user(x, y, user[0])
                y += 80
        except Exception as e:
            print(f"重新加载申请页面时出错: {e}")
        finally:
            db.close()

    def disagree_friend(self, friendname):
        """拒绝好友请求"""
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT USER_ID FROM user WHERE ACCOUNT_NUMBER = %s", (friendname,))
        friend_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM friend WHERE FRIEND_ID = %s AND USER_ID = %s AND STATE = 0", (self.user_id, friend_id))
        db.commit()
        db.close()
        self.reload_application()

    def show_personal_gamelibrary_page(self):
        """显示个人游戏库页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(4)
        self.ui.listWidget_3.clear()
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            all_item = QtWidgets.QListWidgetItem("全部")
            all_item.setData(QtCore.Qt.UserRole, "all")
            self.ui.listWidget_3.addItem(all_item)
            cursor.execute("SELECT DISTINCT gt.TYPE_NAME FROM having_games hg JOIN GAME_TO_TYPE gt ON hg.GAME_ID = gt.GAME_ID WHERE hg.USER_ID = %s", (self.user_id,))
            game_types = cursor.fetchall()
            for game_type in game_types:
                item = QtWidgets.QListWidgetItem(game_type[0])
                item.setData(QtCore.Qt.UserRole, game_type[0])
                self.ui.listWidget_3.addItem(item)
            try:
                self.ui.listWidget_3.itemClicked.disconnect()
            except:
                pass
            self.ui.listWidget_3.itemClicked.connect(self.filter_games_by_type)
            self.filter_games_by_type(all_item)

    def filter_games_by_type(self, item):
        """按游戏类型过滤游戏"""
        selected_type = item.data(QtCore.Qt.UserRole)
        for widget in self.ui.scrollAreaWidgetContents_GameLibrary.findChildren(QWidget):
            widget.deleteLater()
        QApplication.processEvents()
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            if selected_type == "all":
                cursor.execute("SELECT g.GAME_NAME FROM having_games hg JOIN game g ON hg.GAME_ID = g.GAME_ID WHERE hg.USER_ID = %s", (self.user_id,))
            else:
                cursor.execute("SELECT g.GAME_NAME FROM having_games hg JOIN game g ON hg.GAME_ID = g.GAME_ID JOIN GAME_TO_TYPE gt ON g.GAME_ID = gt.GAME_ID WHERE hg.USER_ID = %s AND gt.TYPE_NAME = %s", (self.user_id, selected_type))
            games = cursor.fetchall()
            x, y = 20, 20
            for game in games:
                self.add_gamelibrary_page(x, y, game[0])
                y += 90

    def add_gamelibrary_page(self, x, y, game_name):
        """添加游戏到游戏库显示"""
        frame_gamelibrary = QFrame(self.ui.scrollAreaWidgetContents_GameLibrary)
        frame_gamelibrary.move(x, y)
        frame_gamelibrary.setMinimumSize(506, 70)
        frame_gamelibrary.setMaximumSize(506, 70)
        frame_gamelibrary.setStyleSheet("background-color: rgb(59, 59, 89);")
        Game_Name = QLabel(frame_gamelibrary)
        Game_Name.setGeometry(QtCore.QRect(3, 3, 500, 26))
        Game_Name.setStyleSheet("background-color: rgb(255, 255, 255,20); font: 15pt '微软雅黑'; color: rgb(255, 255, 255);")
        Game_Name.setText(game_name)
        pushButton_Evaluate = QPushButton(frame_gamelibrary)
        pushButton_Evaluate.setGeometry(QtCore.QRect(340, 40, 75, 23))
        pushButton_Evaluate.setStyleSheet("background-color: rgb(92, 138, 0); color: rgb(255, 255, 255);")
        pushButton_Evaluate.clicked.connect(lambda: self.evaluate_game_page(game_name))
        pushButton_Evaluate.setText("评价")
        pushButton_StartGame = QPushButton(frame_gamelibrary)
        pushButton_StartGame.setGeometry(QtCore.QRect(420, 40, 75, 23))
        pushButton_StartGame.setStyleSheet("background-color: rgb(154, 231, 231); color: rgb(255, 255, 255);")
        pushButton_StartGame.setText("开始游戏")
        pushButton_Remove = QPushButton(frame_gamelibrary)
        pushButton_Remove.setGeometry(QtCore.QRect(260, 40, 75, 23))
        pushButton_Remove.setStyleSheet("background-color: rgb(92, 138, 0); color: rgb(255, 255, 255);")
        pushButton_Remove.clicked.connect(lambda: self.remove_games_from_gamelirary(game_name))
        pushButton_Remove.setText("移出库")
        frame_gamelibrary.show()

    def evaluate_game_page(self, game_name):
        """显示游戏评价页面"""
        for frame in self.evaluation_frames:
            frame.deleteLater()
        self.evaluation_frames.clear()
        self.ui.scrollAreaWidgetContents_5.update()
        self.ui.stackedWidget_Window.setCurrentIndex(7)
        self.ui.success_error_Type.setCurrentIndex(0)
        self.ui.label_show_gameName.setText(game_name)
        self.ui.lineEdit_writeForWhichGame.setText(f"为 {game_name} 写一篇评测")
        self.ui.pushButton_postSure.clicked.connect(lambda: self.post_evaluate(game_name))
        self.ui.pushButton_recommend.clicked.connect(self.clicked_recommend_button)
        self.ui.pushButton_disrecommend.clicked.connect(self.clicked_disrecommend_button)
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT GAME_ID FROM game WHERE GAME_NAME = %s", (game_name,))
        game_id = cursor.fetchone()
        if game_id:
            cursor.execute("SELECT COUNT(*) FROM evaluatetable WHERE GAME_ID = %s", (game_id[0],))
            evaluate_count = int(cursor.fetchone()[0])
            if evaluate_count:
                cursor.execute("SELECT e.EVALUATE, e.EVALUATE_DATE, e.SCORE, u.ACCOUNT_NUMBER FROM evaluatetable e JOIN user u ON e.USER_ID = u.USER_ID WHERE e.GAME_ID = %s", (game_id[0],))
                all_evaluates = cursor.fetchall()
                self.show_game_evaluate(game_id[0])
        db.close()

    def post_evaluate(self, game_name):
        """发布游戏评价"""
        new_game_evaluate = self.ui.textEdit_evaluate.toPlainText()
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT GAME_ID FROM game WHERE GAME_NAME = %s", (game_name,))
        game_id_result = cursor.fetchone()
        if game_id_result:
            game_id = game_id_result[0]
            try:
                now_time = datetime.datetime.now()
                cursor.execute(
                    "INSERT INTO evaluatetable (USER_ID, GAME_ID, EVALUATE, EVALUATE_DATE, SCORE) VALUES (%s, %s, %s, %s, %s)",
                    (self.user_id, game_id, new_game_evaluate, now_time, self.new_game_score))
                db.commit()
                self.ui.success_error_Type.setCurrentIndex(1)
                self.show_game_evaluate(game_id)
            except pymysql.MySQLError as e:
                print(f"数据库错误: {e}")
                db.rollback()
                self.ui.success_error_Type.setCurrentIndex(2)
        db.close()

    def clicked_recommend_button(self):
        """点击推荐按钮"""
        self.new_game_score = 1

    def clicked_disrecommend_button(self):
        """点击不推荐按钮"""
        self.new_game_score = 0

    def show_game_evaluate(self, game_id):
        """显示游戏评价"""
        self.ui.stackedWidget_Window.setCurrentIndex(7)
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM evaluatetable WHERE GAME_ID = %s", (game_id,))
        evaluate_count = int(cursor.fetchone()[0])
        cursor.execute("SELECT e.EVALUATE, e.EVALUATE_DATE, e.SCORE, u.ACCOUNT_NUMBER FROM evaluatetable e JOIN user u ON e.USER_ID = u.USER_ID WHERE e.GAME_ID = %s", (game_id,))
        all_evaluate = list(cursor.fetchall())
        db.close()
        x, y = 53, 630
        for i in range(evaluate_count):
            frame = self.add_game_evaluate(x, y, all_evaluate[i][3], all_evaluate[i][0], all_evaluate[i][2])
            self.evaluation_frames.append(frame)
            y += 230

    def add_game_evaluate(self, x, y, user_name, evaluate, score):
        """添加游戏评价到显示区域"""
        frame = QFrame(parent=self.ui.scrollAreaWidgetContents_5)
        frame.move(x, y)
        frame.setMinimumSize(900, 200)
        frame.setMaximumSize(900, 200)
        frame.setStyleSheet("background-color: rgb(59, 59, 89);")
        layoutWidget = QWidget(frame)
        layoutWidget.setGeometry(QtCore.QRect(0, 0, 900, 200))
        frame_evaluate = QVBoxLayout(layoutWidget)
        frame_evaluate.setContentsMargins(3, 3, 3, 3)
        User_Name = QPushButton(layoutWidget)
        User_Name.setStyleSheet("background-color: rgb(255, 255, 255,20); font: 15pt '微软雅黑'; color: rgb(255, 255, 255);")
        User_Name.setText(user_name)
        User_Name.clicked.connect(lambda: self.show_user_page(user_name))
        frame_evaluate.addWidget(User_Name)
        Game_Evaluate = QPlainTextEdit(layoutWidget)
        Game_Evaluate.setReadOnly(True)
        Game_Evaluate.setStyleSheet("background-color: rgb(255, 255, 255,20); font: 10pt '微软雅黑'; color: rgb(255, 255, 255); border:none;")
        Game_Evaluate.setPlainText(evaluate)
        frame_evaluate.addWidget(Game_Evaluate)
        Game_Score = QLabel(layoutWidget)
        Game_Score.setStyleSheet("background-color: rgb(255, 255, 255,20); font: 10pt '微软雅黑'; color: rgb(255, 255, 255); border:none;")
        Game_Score.setText("推荐" if score == 1 else "不推荐")
        frame_evaluate.addWidget(Game_Score)
        frame.show()
        return frame

    def show_user_page(self, user_name):
        """显示用户页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(3)
        self.ui.label_Show_FriendName.setText(user_name)

    def reload_gamelibrary(self):
        """重新加载游戏库"""
        for child in self.ui.scrollAreaWidgetContents_GameLibrary.findChildren(QWidget):
            child.deleteLater()
        QApplication.processEvents()
        db = pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system')
        cursor = db.cursor()
        cursor.execute("SELECT game_id FROM having_games WHERE USER_ID = %s", (self.user_id,))
        game_ids = cursor.fetchall()
        game_info_list = []
        for game_id in game_ids:
            cursor.execute("SELECT GAME_NAME FROM game WHERE GAME_ID = %s", (game_id[0],))
            game_detail = cursor.fetchone()
            if game_detail:
                game_info_list.append(game_detail)
        db.close()
        x, y = 20, 20
        for game_info in game_info_list:
            self.add_gamelibrary_page(x, y, game_info[0])
            y += 90

    def show_personal_shoppingcart_page(self):
        """显示个人购物车页面"""
        self.ui.stackedWidget_Window.setCurrentIndex(5)
        for child in self.ui.scrollAreaWidgetContents_Shoppingcart.findChildren(QWidget):
            if child.objectName() != "emptyCartLabel":
                child.deleteLater()
        self.ui.label_showAllPrice.clear()
        QApplication.processEvents()
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            cursor.execute("SELECT ORDER_ID FROM order_for_goods WHERE USER_ID = %s AND ORDER_STATE = 0", (self.user_id,))
            order_id = cursor.fetchone()
            if order_id:
                cursor.execute("SELECT GAME_ID FROM order_details WHERE ORDER_ID = %s AND BUY_OR_REFUND = 0", (order_id[0],))
                game_already_in_cart_id = cursor.fetchall()
                game_ids_str = ', '.join(str(id[0]) for id in game_already_in_cart_id) if game_already_in_cart_id else ''
                if game_ids_str:
                    cursor.execute(f"SELECT GAME_NAME, PRICE FROM game WHERE GAME_ID IN ({game_ids_str})")
                    game_already_in_cart = cursor.fetchall()
                    x, y = 10, 10
                    all_price = 0
                    for game in game_already_in_cart:
                        self.add_shoppingcartgame_page(x, y, order_id[0], game[0], game[1])
                        all_price += float(game[1])
                        y += 110
                    self.ui.label_showAllPrice.setText(str(all_price))
                else:
                    self.ui.label_showAllPrice.setText("0")
            else:
                self.ui.label_showAllPrice.setText("0")

    def add_shoppingcartgame_page(self, x, y, order_id, game_name, game_price):
        """添加购物车游戏到显示区域"""
        frame_shopingcartgame = QFrame(parent=self.ui.scrollAreaWidgetContents_Shoppingcart)
        frame_shopingcartgame.move(x, y)
        frame_shopingcartgame.setMinimumSize(565, 100)
        frame_shopingcartgame.setMaximumSize(565, 100)
        frame_shopingcartgame.setStyleSheet("background-color: rgb(255, 255, 255,80);")
        pushButton_game = QPushButton(frame_shopingcartgame)
        pushButton_game.setGeometry(QtCore.QRect(20, 20, 400, 50))
        pushButton_game.setStyleSheet("background-color: rgb(59, 59, 100,0);")
        pushButton_game.setText(game_name)
        label_ShowPrice = QLabel(frame_shopingcartgame)
        label_ShowPrice.setGeometry(QtCore.QRect(483, 50, 71, 20))
        label_ShowPrice.setStyleSheet("background-color: rgb(59, 59, 100,0);")
        label_ShowPrice.setText(str(game_price))
        pushButton_Remove = QPushButton(frame_shopingcartgame)
        pushButton_Remove.setGeometry(QtCore.QRect(484, 73, 71, 20))
        pushButton_Remove.setStyleSheet("background-color: rgb(59, 59, 100,0);")
        pushButton_Remove.clicked.connect(lambda: self.remove_games_from_shoppingcart(order_id, game_name))
        pushButton_Remove.setText("移出购物车")
        frame_shopingcartgame.show()

    def reload_shopping_cart(self, order_id):
        """重新加载购物车"""
        for child in self.ui.scrollAreaWidgetContents_Shoppingcart.findChildren(QWidget):
            if child.objectName() != "emptyCartLabel":
                child.deleteLater()
        self.ui.label_showAllPrice.clear()
        QApplication.processEvents()
        with pymysql.connect(host="localhost", user="root", password='123456', port=3306, db='game_system') as db:
            cursor = db.cursor()
            cursor.execute("SELECT ORDER_ID FROM order_for_goods WHERE USER_ID = %s AND ORDER_STATE = 0", (self.user_id,))
            order_id = cursor.fetchone()
            all_price = 0
            if order_id:
                cursor.execute("SELECT GAME_ID FROM order_details WHERE ORDER_ID = %s AND BUY_OR_REFUND = 0", (order_id[0],))
                game_already_in_cart_id = cursor.fetchall()
                game_ids_str = ', '.join(str(id[0]) for id in game_already_in_cart_id) if game_already_in_cart_id else ''
                if game_ids_str:
                    cursor.execute(f"SELECT GAME_NAME, PRICE FROM game WHERE GAME_ID IN ({game_ids_str})")
                    game_already_in_cart = cursor.fetchall()
                    x, y = 10, 10
                    for game_info in game_already_in_cart:
                        self.add_shoppingcartgame_page(x, y, order_id[0], game_info[0], game_info[1])
                        all_price += float(game_info[1])
                        y += 110
                    self.ui.label_showAllPrice.setText(str(all_price))
                else:
                    self.ui.label_showAllPrice.setText("0")
            else:
                self.ui.label_showAllPrice.setText("0")

    def test(self, testname):
        """测试方法"""
        print(testname)
