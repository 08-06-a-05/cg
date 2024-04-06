import math
import time
from typing import Type, Callable, Optional

import matplotlib.pyplot as plt
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QMessageBox, QWidget

DrawingFunc = Callable[[int, int, int, int, QPainter], None]


def calc_ladders_wrapper(drawer: DrawingFunc):
    def wrapper(x_1: int, y_1: int, x_2: int, y_2: int, qp: QPainter, calc_ladders: bool = False) -> Optional[int]:
        if calc_ladders:
            return min(abs(x_1 - x_2), abs(y_1 - y_2))
        drawer(x_1, y_1, x_2, y_2, qp)

    return wrapper


class DrawingScene(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines_list: list[tuple[int, int, int, int, QColor, Callable]] = []
        self.initUI()

    def clear_lines_list(self):
        self.lines_list.clear()

    def add_line(self, line: tuple[int, int, int, int, QColor, Callable]):
        self.lines_list.append(line)

    def initUI(self):
        self.setMinimumSize(50, 50)
        self.setGeometry(490, 20, 570, 650)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor("white"))
        self.setPalette(p)
        self.setAutoFillBackground(True)

    def paintEvent(self, e):
        qp = QPainter()
        qp.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        qp.begin(self)
        for line in self.lines_list:
            qp.setPen(line[4])
            if line[5] is None:
                qp.drawLine(line[0], line[1], line[2], line[3])
            else:
                line[5](line[0], line[1], line[2], line[3], qp)
        qp.end()


def sign(x: float) -> int:
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def show_bar(x, y):
    fig2, ax = plt.subplots()
    fig2.set_figwidth(100)
    translate = {"bres_float": "Вещественный\nалг. Брезенхема", "bres_int": "Целочисленный\nалг. Брезенхема",
                 "light_brem": "Алг. Брезенхема\nсо сглаживанием", "alg_vu": "Алг. ВУ", "digital": "Алг. ЦДА"}
    ax.bar(tuple(translate[i] for i in x), y, width=1, edgecolor="white", linewidth=0.7)
    fig2.show()


def show_graph(x, y, name, fig, counter):
    if name == "bres_float":
        counter = 1
        fig.text(0.3, 0.95, "Количество ступенек в зависимости от угла наклона отрезка", fontsize=14)
        fig.text(0.7, 0.4, "Длина линии: 200", fontsize=14)
    ax = fig.add_subplot(2, 3, counter)
    ax.plot(x, y)
    ax.set_title(name)
    counter += 1


@calc_ladders_wrapper
def digital_differential_analyzer(start_x: int, start_y: int, end_x: int, end_y: int, qp: QPainter):
    if start_x == end_x and start_y == end_y:
        qp.drawPoint(start_x, start_y)
        return
    l: int = max(abs(start_x - end_x), abs(start_y - end_y))
    dx: float = (end_x - start_x) / l
    dy: float = (end_y - start_y) / l
    cur_x: float = start_x  # + 0.5 * sign(dx)
    cur_y: float = start_y  # + 0.5 * sign(dy)
    for i in range(l + 1):
        qp.drawPoint(round(cur_x), round(cur_y))
        cur_x += dx
        cur_y += dy


@calc_ladders_wrapper
def bresenham_algorithm_float(start_x: int, start_y: int, end_x: int, end_y: int, qp: QPainter):
    if start_x == end_x and start_y == end_y:
        qp.drawPoint(start_x, start_y)
        return
    cur_x = start_x
    cur_y = start_y
    dx: int = end_x - start_x
    dy: int = end_y - start_y
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)
    trade = False
    if dy >= dx:
        dx, dy = dy, dx
        trade = True
    m: float = dy / dx
    e: float = m - 0.5
    for i in range(dx + 1):
        qp.drawPoint(cur_x, cur_y)
        if e >= 0:
            if trade:
                cur_x += sx
            else:
                cur_y += sy
            e -= 1
        e += m
        if trade:
            cur_y += sy
        else:
            cur_x += sx


@calc_ladders_wrapper
def bresenham_algorithm_int(start_x: int, start_y: int, end_x: int, end_y: int, qp: QPainter):
    if start_x == end_x and start_y == end_y:
        qp.drawPoint(start_x, start_y)
        return
    cur_x: int = start_x
    cur_y: int = start_y
    dx: int = end_x - start_x
    dy: int = end_y - start_y
    sx: int = sign(dx)
    sy: int = sign(dy)
    dx = abs(dx)
    dy = abs(dy)
    trade: bool = False
    if dy >= dx:
        dx, dy = dy, dx
        trade = True
    c_dx: int = dx << 1
    c_dy: int = dy << 1
    e: int = 2 * dy - dx
    for i in range(dx + 1):
        qp.drawPoint(cur_x, cur_y)
        if e >= 0:
            if trade:
                cur_x += sx
            else:
                cur_y += sy
            e -= c_dx
        if trade:
            cur_y += sy
        else:
            cur_x += sx
        e += c_dy


@calc_ladders_wrapper
def alg_vu(start_x: int, start_y: int, end_x: int, end_y: int, qp: QPainter):
    if start_x == end_x and start_y == end_y:
        qp.drawPoint(start_x, start_y)
        return
    if start_x == end_x:
        ds = sign(end_y - start_y)
        dy = abs(end_y - start_y)
        for i in range(dy + 1):
            qp.drawPoint(start_x, start_y)
            start_y += ds
        return
    if start_y == end_y:
        ds = sign(end_x - start_x)
        dx = abs(end_x - start_x)
        for i in range(dx + 1):
            qp.drawPoint(start_x, start_y)
            start_x += ds
        return

    cur_color = qp.pen().color().rgba()
    save_color = cur_color
    colors = [0] * 3
    colors[2] = cur_color % 256
    cur_color //= 256
    colors[1] = cur_color % 256
    cur_color //= 256
    colors[0] = cur_color % 256

    dx = end_x - start_x
    dy = end_y - start_y
    trade = False
    if abs(dy) > abs(dx):
        trade = True
        dy, dx = dx, dy
        if end_y < start_y:
            start_x, end_x = end_x, start_x
            start_y, end_y = end_y, start_y
    else:
        if end_x < start_x:
            start_x, end_x = end_x, start_x
            start_y, end_y = end_y, start_y
    grad = dy / dx
    qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], 255))
    qp.drawPoint(start_x, start_y)
    if not trade:
        intery = start_y + grad
        for cur_x in range(start_x + 1, end_x):
            qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], round(255 * (1 - intery + int(intery)))))
            qp.drawPoint(cur_x, int(intery))
            qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], round(255 * (intery - int(intery)))))
            qp.drawPoint(cur_x, int(intery) + 1)
            intery += grad
    else:
        interx = start_x + grad
        for cur_y in range(start_y + 1, end_y):
            qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], round(255 * (1 - interx + int(interx)))))
            qp.drawPoint(int(interx), cur_y)
            qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], round(255 * (interx - int(interx)))))
            qp.drawPoint(int(interx) + 1, cur_y)
            interx += grad

    qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], 255))
    qp.drawPoint(end_x, end_y)

    qp.setPen(QtGui.QColor(save_color))


@calc_ladders_wrapper
def light_brem(start_x: int, start_y: int, end_x: int, end_y: int, qp: QPainter):
    if start_x == end_x and start_y == end_y:
        qp.drawPoint(start_x, start_y)
        return
    cur_x = start_x
    cur_y = start_y
    dx: int = end_x - start_x
    dy: int = end_y - start_y
    sx = sign(dx)
    sy = sign(dy)
    dx = abs(dx)
    dy = abs(dy)
    trade = False
    if dy >= dx:
        dx, dy = dy, dx
        trade = True
    m: float = dy / dx
    w: float = 1 - m
    e: float = 0.5

    cur_color = qp.pen().color().rgba()
    save_color = cur_color
    colors = [0] * 3
    colors[2] = cur_color % 256
    cur_color //= 256
    colors[1] = cur_color % 256
    cur_color //= 256
    colors[0] = cur_color % 256
    qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], round(255 * m / 2)))
    qp.drawPoint(cur_x, cur_y)
    for i in range(dx + 1):
        if e < w:
            if trade:
                cur_y += sy
            else:
                cur_x += sx
            e += m
        else:
            cur_x += sx
            cur_y += sy
            e -= w
        if abs(w - 1) < 1e-6:
            qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], 255))
        else:
            qp.setPen(QtGui.QColor(colors[0], colors[1], colors[2], round(255 * e)))
        qp.drawPoint(cur_x, cur_y)
    qp.setPen(QtGui.QColor(save_color))


def clear_scene(x: int, y: int, w: int, h: int, qp: QPainter):
    qp.eraseRect(x, y, w, h)


class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        self.main_window = MainWindow
        self.setupUi(MainWindow)
        # self.scene_objects: mediator.SceneObjects = scene_objects

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1074, 740)

        font = QtGui.QFont()
        font.setPointSize(13)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ex = DrawingScene(parent=self.centralwidget)
        self.alg_choose_1 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.alg_choose_1.setGeometry(QtCore.QRect(10, 10, 421, 81))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.alg_choose_1.sizePolicy().hasHeightForWidth())
        self.alg_choose_1.setSizePolicy(sizePolicy)
        self.alg_choose_1.setMaximumSize(QtCore.QSize(421, 16777215))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.alg_choose_1.setFont(font)
        self.alg_choose_1.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.alg_choose_1.setModelColumn(0)
        self.alg_choose_1.setObjectName("alg_choose_1")
        self.alg_choose_1.addItem("")
        self.alg_choose_1.addItem("")
        self.alg_choose_1.addItem("")
        self.alg_choose_1.addItem("")
        self.alg_choose_1.addItem("")
        self.alg_choose_1.addItem("")
        self.color_choose_1 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.color_choose_1.setGeometry(QtCore.QRect(10, 100, 421, 41))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.color_choose_1.sizePolicy().hasHeightForWidth())
        self.color_choose_1.setSizePolicy(sizePolicy)
        self.color_choose_1.setMaximumSize(QtCore.QSize(421, 16777215))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.color_choose_1.setFont(font)
        self.color_choose_1.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.color_choose_1.setModelColumn(0)
        self.color_choose_1.setObjectName("color_choose_1")
        self.color_choose_1.addItem("")
        self.color_choose_1.addItem("")
        self.color_choose_1.addItem("")
        self.clear_scene_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.clear_scene_button.setGeometry(QtCore.QRect(60, 640, 320, 28))
        self.clear_scene_button.setObjectName("clear_scene_button")
        self.draw_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.draw_button.setGeometry(QtCore.QRect(30, 270, 390, 28))
        self.draw_button.setObjectName("draw_button")
        self.center_label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.center_label_2.setGeometry(QtCore.QRect(50, 320, 320, 20))
        self.center_label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.center_label_2.setObjectName("center_label_2")
        self.draw_spectrum_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.draw_spectrum_button.setGeometry(QtCore.QRect(60, 520, 320, 28))
        self.draw_spectrum_button.setObjectName("draw_spectrum_button")
        self.angle_value = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.angle_value.setGeometry(QtCore.QRect(160, 350, 191, 28))
        self.angle_value.setObjectName("angle_value")
        self.length_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.length_label.setGeometry(QtCore.QRect(9, 390, 141, 28))
        self.length_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.length_label.setObjectName("length_label")
        self.angle_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.angle_label.setGeometry(QtCore.QRect(9, 350, 141, 28))
        self.angle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.angle_label.setObjectName("angle_label")
        self.length_value = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.length_value.setGeometry(QtCore.QRect(160, 390, 191, 28))
        self.length_value.setObjectName("length_value")
        self.graph_ladders_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.graph_ladders_button.setGeometry(QtCore.QRect(30, 560, 401, 28))
        self.graph_ladders_button.setObjectName("graph_ladders_button")
        self.graph_avg_time_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.graph_avg_time_button.setGeometry(QtCore.QRect(20, 600, 420, 28))
        self.graph_avg_time_button.setObjectName("graph_avg_time_button")
        self.p1_x_value = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.p1_x_value.setGeometry(QtCore.QRect(120, 190, 113, 28))
        self.p1_x_value.setObjectName("p1_x_value")
        self.p1_y_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.p1_y_label.setGeometry(QtCore.QRect(30, 230, 80, 28))
        self.p1_y_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.p1_y_label.setObjectName("p1_y_label")
        self.p1_x_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.p1_x_label.setGeometry(QtCore.QRect(30, 190, 80, 28))
        self.p1_x_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.p1_x_label.setObjectName("p1_x_label")
        self.p1_y_value = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.p1_y_value.setGeometry(QtCore.QRect(120, 230, 113, 28))
        self.p1_y_value.setObjectName("p1_y_balue")
        self.p2_x_value = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.p2_x_value.setGeometry(QtCore.QRect(350, 190, 113, 28))
        self.p2_x_value.setObjectName("p2_x_value")
        self.p2_y_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.p2_y_label.setGeometry(QtCore.QRect(260, 230, 80, 28))
        self.p2_y_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.p2_y_label.setObjectName("p2_y_label")
        self.p2_x_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.p2_x_label.setGeometry(QtCore.QRect(260, 190, 80, 28))
        self.p2_x_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.p2_x_label.setObjectName("p2_x_label")
        self.p2_y_value = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.p2_y_value.setGeometry(QtCore.QRect(350, 230, 113, 28))
        self.p2_y_value.setObjectName("p2_y_value")
        self.p1_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.p1_label.setGeometry(QtCore.QRect(0, 150, 250, 28))
        self.p1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.p1_label.setObjectName("p1_label")
        self.p2_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.p2_label.setGeometry(QtCore.QRect(250, 150, 240, 28))
        self.p2_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.p2_label.setObjectName("p2_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1074, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.alg_choose_1.setCurrentIndex(0)
        self.color_choose_1.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.make_connects()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.alg_choose_1.setItemText(0, _translate("MainWindow", "Алгоритм Брезенхема с\nдействительными данными"))
        self.alg_choose_1.setItemText(1, _translate("MainWindow", "Алгоритм Брезенхема с\nцелочисленными данными"))
        self.alg_choose_1.setItemText(2, _translate("MainWindow", "Алгоритм Брезенхема с\nустранением ступенчатости"))
        self.alg_choose_1.setItemText(3, _translate("MainWindow", "Алгоритм ВУ"))
        self.alg_choose_1.setItemText(4, _translate("MainWindow", "Алгоритм ЦДА"))
        self.alg_choose_1.setItemText(5, _translate("MainWindow", "Библиотечный алгоритм"))
        self.color_choose_1.setItemText(0, _translate("MainWindow", "Черный"))
        self.color_choose_1.setItemText(1, _translate("MainWindow", "Белый"))
        self.color_choose_1.setItemText(2, _translate("MainWindow", "Красный"))
        self.clear_scene_button.setText(_translate("MainWindow", "Очистить холст"))
        self.draw_button.setText(_translate("MainWindow", "Нарисовать"))
        self.center_label_2.setText(_translate("MainWindow", "Построение спектра"))
        self.draw_spectrum_button.setText(_translate("MainWindow", "Построить спектр"))
        self.length_label.setText(_translate("MainWindow", "Длина отрезка:"))
        self.angle_label.setText(_translate("MainWindow", "Угол поворота:"))
        self.graph_ladders_button.setText(_translate("MainWindow", "Построить графики ступенек от угла наклона"))
        self.graph_avg_time_button.setText(_translate("MainWindow", "Построить графики среднего времени по спектру"))
        self.p1_x_label.setText(_translate("MainWindow", "x1:"))
        self.p1_y_label.setText(_translate("MainWindow", "y1:"))
        self.p2_x_label.setText(_translate("MainWindow", "x2:"))
        self.p2_y_label.setText(_translate("MainWindow", "y2:"))
        self.p1_label.setText(_translate("MainWindow", "Координаты первой точки:"))
        self.p2_label.setText(_translate("MainWindow", "Координаты второй точки:"))

    def make_connects(self):
        self.clear_scene_button.clicked.connect(self.clear_scene_button_handler)
        self.draw_button.clicked.connect(self.draw_button_handler)
        self.draw_spectrum_button.clicked.connect(self.draw_spectrum_button_handler)
        self.graph_ladders_button.clicked.connect(self.graph_ladders_button_handler)
        self.graph_avg_time_button.clicked.connect(self.graph_avg_time_button_handler)

    def clear_scene_button_handler(self):
        self.ex.clear_lines_list()
        self.ex.add_line((490, 20, 570, 700, QtGui.QColor("black"), clear_scene))
        self.ex.update()

    @staticmethod
    def validate(req_type: Type[float], s: str) -> bool:
        """
        Проверяет, что функция соответствует переданному типу.

        :param req_type: Ожидаемый тип, к которому должна быть приводима строка.
        :param s: Строка.
        :return: Является ли строка корректным значением.
        """
        try:
            req_type(s)
        except ValueError:
            return False
        else:
            return True

    def draw_button_handler(self):
        if not self.alg_choose_1.currentText():
            self.show_error("Ошибка отрисовки", "Не выбран алгоритм отрисовки")
            return
        if not self.color_choose_1.currentText():
            self.show_error("Ошибка отрисовки", "Не выбран цвет отрисовки")
            return
        if not self.validate(int, self.p1_x_value.text()):
            self.show_error("Ошибка отрисовки", "Не задана координата x начала отрезка")
            return
        if not self.validate(int, self.p1_y_value.text()):
            self.show_error("Ошибка отрисовки", "Не задана координата y начала отрезка")
            return
        if not self.validate(int, self.p2_x_value.text()):
            self.show_error("Ошибка отрисовки", "Не задана координата x конца отрезка")
            return
        if not self.validate(int, self.p2_y_value.text()):
            self.show_error("Ошибка отрисовки", "Не задана координата y конца отрезка")
            return
        text_to_func: dict[str, Callable[[int, int, int, int, QPainter], None]] = {
            "алгоритм брезенхема с\nдействительными данными": bresenham_algorithm_float,
            "алгоритм брезенхема с\nцелочисленными данными": bresenham_algorithm_int,
            "алгоритм брезенхема с\nустранением ступенчатости": light_brem,
            "алгоритм ву": alg_vu,
            "алгоритм цда": digital_differential_analyzer,
            "библиотечный алгоритм": None
        }
        drawer = text_to_func[self.alg_choose_1.currentText().lower()]
        translate_text: dict[str, str] = {"черный": "black", "красный": "red", "белый": "white"}
        color: QtGui.QColor = QtGui.QColor(translate_text[self.color_choose_1.currentText().lower()])
        x1: int = int(self.p1_x_value.text())
        y1: int = int(self.p1_y_value.text())
        x2: int = int(self.p2_x_value.text())
        y2: int = int(self.p2_y_value.text())
        len_info: tuple[int, int, int, int, QtGui.QColor, DrawingFunc] = (x1, y1, x2, y2, color, drawer)
        self.ex.clear_lines_list()
        self.ex.add_line(len_info)
        self.ex.update()

    def draw_spectrum_button_handler(self):
        if not self.alg_choose_1.currentText():
            self.show_error("Ошибка отрисовки спектра", "Не выбран алгоритм основным цветом")
            return
        if not self.validate(float, self.angle_value.text()):
            self.show_error("Ошибка отрисовки спектра", "Задан некорректный угол")
            return
        if not self.validate(float, self.length_value.text()):
            self.show_error("Ошибка отрисовки спектра", "Задана некорректная длина")
            return
        if not self.color_choose_1.currentText():
            self.show_error("Ошибка отрисовки", "Не выбран цвет отрисовки")
            return
        text_to_func: dict[str, Callable[[int, int, int, int, QPainter], None]] = {
            "алгоритм брезенхема с\nдействительными данными": bresenham_algorithm_float,
            "алгоритм брезенхема с\nцелочисленными данными": bresenham_algorithm_int,
            "алгоритм брезенхема с\nустранением ступенчатости": light_brem,
            "алгоритм ву": alg_vu,
            "алгоритм цда": digital_differential_analyzer,
            "библиотечный алгоритм": None
        }
        drawer = text_to_func[self.alg_choose_1.currentText().lower()]
        translate_text: dict[str, str] = {"черный": "black", "красный": "red", "белый": "white"}
        color: QtGui.QColor = QtGui.QColor(translate_text[self.color_choose_1.currentText().lower()])
        angle = float(self.angle_value.text())
        length = float(self.length_value.text())

        res = self._gen_lines_spectrum((285, 325), angle, 180, length)
        for line in res:
            self.ex.add_line((line[0], line[1], line[2], line[3], color, drawer))
        self.ex.update()

    def graph_ladders_button_handler(self):
        res = self.calc_ladders()
        fig: plt.Figure = plt.figure(figsize=(100, 100))
        counter = 1
        for el in res:
            show_graph(tuple(x for x in range(0, 90)), res[el], el, fig, counter)
            counter += 1
        fig.show()

    def graph_avg_time_button_handler(self):
        res = self.calc_build_time()
        show_bar(res.keys(), res.values())

    def show_error(self, title: str, message: str) -> None:
        """
        Отображение сообщения об ошибке.

        :param title: Заголовок сообщения
        :param message: Текст сообщения
        :return: None
        """
        QMessageBox.critical(self.main_window, title, message)

    @staticmethod
    def _gen_lines_spectrum(center: tuple[int, int], rot_angle: float, max_angle: float, length: float) -> \
            list[tuple[int, int, int, int]]:
        res: list[tuple[int, int, int, int]] = []
        cur_angle = 0
        start_x = center[0]
        start_y = center[1] - length // 2
        end_x = center[0]
        end_y = center[1] + (length + 1) // 2
        math_rot_angle = rot_angle / 180 * math.pi
        for i in range(int(max_angle) // int(rot_angle)):
            build_x1 = (start_x - center[0]) * math.cos(cur_angle) + (start_y - center[1]) * math.sin(
                cur_angle) + center[0]
            build_y1 = -(start_x - center[0]) * math.sin(cur_angle) + (start_y - center[1]) * math.cos(
                cur_angle) + center[1]
            build_x2 = (end_x - center[0]) * math.cos(cur_angle) + (end_y - center[1]) * math.sin(cur_angle) + \
                       center[0]
            build_y2 = -(end_x - center[0]) * math.sin(cur_angle) + (end_y - center[1]) * math.cos(cur_angle) + \
                       center[1]
            res.append((int(build_x1), int(build_y1), int(build_x2), int(build_y2)))
            cur_angle += math_rot_angle
        return res

    def calc_ladders(self):
        algorithms = (
            bresenham_algorithm_float,
            bresenham_algorithm_int,
            light_brem,
            alg_vu,
            digital_differential_analyzer,
        )
        alg_names = ("bres_float", "bres_int", "light_brem", "alg_vu", "digital")
        ladders_dict = dict.fromkeys(alg_names, 0)
        draw_lines = self._gen_lines_spectrum((285, 325), 1, 90, 200)
        for num, alg in enumerate(algorithms):
            data = []
            for line in draw_lines:
                data.append(alg(*line, QPainter(), calc_ladders=True))
            ladders_dict[alg_names[num]] = data
        return ladders_dict

    def calc_build_time(self):
        algorithms = (
            bresenham_algorithm_float,
            bresenham_algorithm_int,
            light_brem,
            alg_vu,
            digital_differential_analyzer,
        )
        alg_names = ("bres_float", "bres_int", "light_brem", "alg_vu", "digital")
        starts_arr = (12, 9, 10, 15, 11)
        alg_work_times = dict.fromkeys(alg_names, 0)
        draw_lines = self._gen_lines_spectrum((285, 325), 30, 180, 200)
        for num, alg in enumerate(algorithms):
            starts = starts_arr[num]
            start = time.perf_counter()
            for i in range(starts):
                for line in draw_lines:
                    alg(line[0], line[1], line[2], line[3], QPainter())
            end = time.perf_counter()
            alg_work_times[alg_names[num]] = (end - start) / 10
        return alg_work_times
