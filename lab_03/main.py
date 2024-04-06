import sys

from PyQt6 import QtWidgets

from interface import *

# TODO: Подписать оси


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(window)
    window.show()
    app.exec()
