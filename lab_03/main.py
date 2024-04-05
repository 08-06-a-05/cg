import sys

from PyQt6 import QtWidgets

from new_interface import *

# TODO: Подписать оси


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(window)
    ui.redraw_scene()
    window.show()
    app.exec()
