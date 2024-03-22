import sys

from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont

import new_interface
import mediator

if __name__ == '__main__':
    scene_objects = mediator.SceneObjects((300, 300))
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QFont("Times", 15))
    window = QtWidgets.QMainWindow()
    ui = new_interface.Ui_MainWindow(window, scene_objects)
    window.show()
    app.exec()
