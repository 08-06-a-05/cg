import sys

from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont

import interface
import mediator

if __name__ == '__main__':
    scene_objects = mediator.SceneObjects()
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QFont("Times", 15))
    window = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow(window, scene_objects)
    window.show()
    app.exec()
