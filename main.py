import sys
from PyQt5 import QtCore, QtWidgets
from login_window import LogInWindow

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    win = LogInWindow()
    win.show()
    sys.exit(app.exec_())