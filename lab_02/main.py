import sys

from PyQt6 import QtWidgets

import interface
import mediator

if __name__ == '__main__':
    scene_objects = mediator.SceneObjects((280, 155))
    app = QtWidgets.QApplication(sys.argv)
    # app.setFont(QFont("Times", 15))
    window = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow(window, scene_objects)
    ui.redraw_scene()
    window.show()
    app.exec()
