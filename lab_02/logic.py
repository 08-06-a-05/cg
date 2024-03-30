from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from math import sin, cos, pi
from typing import Final, Optional, NewType, override


class DrawingObject(ABC):
    RenderedLine = NewType('RenderedLine', tuple[tuple[float, float], tuple[float, float]])
    RenderedCircle = NewType('RenderedCircle', tuple[float, float, float, float])

    @abstractmethod
    def move(self, x_offset: float, y_offset: float) -> None:
        pass

    @abstractmethod
    def scale(self, center: Point, scale_x: float, scale_y: float) -> None:
        pass

    @abstractmethod
    def rotate(self, center: Point, angle: float) -> None:
        pass

    @abstractmethod
    def render(self) -> (RenderedLine | RenderedCircle | tuple[RenderedLine, ...]):
        pass


class ComplexDrawingObject(DrawingObject):
    @abstractmethod
    @override
    def render(self) -> dict[str, tuple[DrawingObject.RenderedLine, ...]]:
        pass

    @abstractmethod
    def __deepcopy__(self, memodict={}):
        pass


class Point(DrawingObject):
    """
    Точка. Содержит координаты.

    :param x: Координата точки
    :param y: Координата точки
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def set_pos(self, x: Optional[float], y: Optional[float]):
        if x is None:
            self.y = y
        elif y is None:
            self.x = x
        else:
            self.x = x
            self.y = y

    def get_pos(self) -> tuple[float, float]:
        return self.x, self.y

    def __eq__(self, other) -> bool:
        """
        Сравнение точек. Две точки равны, если их соответствующие координаты различаются меньше чем на 1e-6.

        :param other: Вторая точка, с которой происходит сравнение
        :return: Результат сравнения
        """

        def is_equal(a: float, b: float) -> bool:
            """
            Сравнение двух вещественных чисел. Два вещественных числа равны, если они различаются меньше чем на 1e-6.

            :param a: Первое число
            :param b: Второе число
            :return: Результат сравнения
            """
            eps: Final[float] = 1e-6
            return abs(a - b) < eps

        return is_equal(self.x, other.x) and is_equal(self.y, other.y)

    def __repr__(self):
        return f"{self.x, self.y}"

    def __str__(self):
        return f"{self.x, self.y}"

    def __hash__(self):
        return hash((self.x, self.y))

    def render(self) -> tuple[float, float]:
        """
        Представление точки в виде, удобном для отрисовки. Точка представляется как кортеж своих координат

        :return: Полученный кортеж
        """
        return self.x, self.y

    def move(self, x_offset: float, y_offset: float) -> None:
        """
        Перемещение точки.

        :param x_offset: Смещение по x
        :param y_offset: Смещение по y
        :return: None
        """
        self.x += x_offset
        self.y += y_offset

    def scale(self, center: Point, scale_x: float, scale_y: float) -> None:
        cp_x = self.x
        cp_y = self.y
        self.x = (cp_x - center.x) * scale_x + center.x
        self.y = (-center.y + cp_y) * scale_y + center.y

    def rotate(self, center: Point, angle: float) -> None:
        cp_x = self.x
        cp_y = self.y
        self.x = (cp_x - center.x) * cos(angle) + (cp_y - center.y) * sin(angle) + center.x
        self.y = (cp_x - center.x) * -sin(angle) + (cp_y - center.y) * cos(angle) + center.y


class Edge(DrawingObject):

    def __init__(self, p1: Point, p2: Point):
        if p1 == p2:
            raise ValueError
        self.p1 = p1
        self.p2 = p2

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def __repr__(self):
        return f"{self.p1.__repr__(), self.p2.__repr__()}"

    def __str__(self):
        return f"{self.p1.__str__(), self.p2.__str__()}"

    def center(self) -> Point:
        return Point((self.p1.x + self.p2.x) / 2, (self.p1.y + self.p2.y) / 2)

    def length(self) -> float:
        return ((self.p1.x - self.p2.x) ** 2 + (self.p1.y - self.p2.y) ** 2) ** 0.5

    def render(self) -> DrawingObject.RenderedLine:
        return self.RenderedLine((self.p1.render(), self.p2.render()))

    def move(self, dx: float, dy: float):
        self.p1.move(dx, dy)
        self.p2.move(dx, dy)

    def scale(self, center: Point, scale_x: float, scale_y: float) -> None:
        self.p1.scale(center, scale_x, scale_y)
        self.p2.scale(center, scale_x, scale_y)

    def rotate(self, center: Point, angle: float) -> None:
        self.p1.rotate(center, angle)
        self.p2.rotate(center, angle)


class Polygon(DrawingObject):

    @staticmethod
    def is_point_on_the_same_line(x, y, e1):
        return (e1.p2.y - e1.p1.y) * (x - e1.p1.x) == (e1.p2.x - e1.p1.x) * (y - e1.p1.y)

    def __init__(self, edges: tuple[Edge, ...]):
        for i in range(len(edges) - 1):
            for k in range(i + 1, len(edges)):
                e1: Edge = edges[i]
                e2: Edge = edges[k]
                if e1.p1 == e2.p1:
                    if self.is_point_on_the_same_line(e2.p2.x, e2.p2.y, e1):
                        raise ValueError
                elif e1.p2 == e2.p1:
                    if self.is_point_on_the_same_line(e2.p2.x, e2.p2.y, e1):
                        raise ValueError
                elif e1.p1 == e2.p2:
                    if self.is_point_on_the_same_line(e2.p1.x, e2.p1.y, e1):
                        raise ValueError
                elif e1.p2 == e2.p2:
                    if self.is_point_on_the_same_line(e2.p1.x, e2.p1.y, e1):
                        raise ValueError
        self.edges = edges
        self.points: set[Point] = set()
        for edge in self.edges:
            self.points.add(edge.p1)
            self.points.add(edge.p2)

    def render(self) -> tuple[DrawingObject.RenderedLine, ...]:
        return tuple(edge.render() for edge in self.edges)

    def get_points(self) -> tuple[tuple[float, float], ...]:
        return tuple(el.render() for el in self.points)

    def __deepcopy__(self, memodict):
        if memodict is None:
            memodict = dict()
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))
        return result

    def move(self, x_offset: float, y_offset: float):
        for p in self.points:
            p.move(x_offset, y_offset)

    def scale(self, center: Point, scale_x: float, scale_y: float):
        for p in self.points:
            p.scale(center, scale_x, scale_y)

    def rotate(self, center: Point, angle: float) -> None:
        for p in self.points:
            p.rotate(center, angle)


class Triangle(Polygon):

    def __init__(self, p1: Point, p2: Point, p3: Point):
        super().__init__((Edge(p1, p2), Edge(p2, p3), Edge(p1, p3)))


class Ellipse(DrawingObject):

    def __init__(self, top_left_p: Point, width: float, height: float) -> None:
        self.top_left_p = top_left_p
        self.points = []
        step = width / 1000
        x = -width / 2
        a_a = width * width / 4
        b_b = height * height / 4
        for i in range(1000):
            self.points.append(
                Point(x + top_left_p.x + width / 2, (b_b - b_b * x * x / a_a) ** 0.5 + top_left_p.y + height / 2))
            x += step
        for i in range(1000):
            self.points.append(
                Point(x + top_left_p.x + width / 2, height / 2 + top_left_p.y - ((b_b - b_b * x * x / a_a) ** 0.5)))
            x -= step

    def render(self) -> tuple[DrawingObject.RenderedLine, ...]:
        res = []
        for i in range(len(self.points)):
            res.append(Edge(self.points[i], self.points[(i + 1) % len(self.points)]).render())
        return tuple(res)

    def move(self, x_offset: float, y_offset: float) -> None:
        for p in self.points:
            p.move(x_offset, y_offset)

    def scale(self, center, scale_x, scale_y) -> None:
        for p in self.points:
            p.scale(center, scale_x, scale_y)

    def rotate(self, center, angle) -> None:
        for p in self.points:
            p.rotate(center, angle)


class Circle(DrawingObject):

    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius

    def square(self) -> float:
        return pi * self.radius * self.radius

    def render(self) -> DrawingObject.RenderedCircle:
        return DrawingObject.RenderedCircle(
            (self.center.x - self.radius, self.center.y - self.radius, self.radius * 2, self.radius * 2, 0))

    def move(self, x_offset: float, y_offset: float) -> None:
        self.center.x += x_offset
        self.center.y += y_offset

    def rotate(self, center: Point, angle: float) -> None:
        self.center.rotate(center, angle)

    def scale(self, center: Point, scale_x: float, scale_y: float) -> None:
        # self.
        self.radius *= scale_x

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))
        return result


class House(ComplexDrawingObject):
    _initial_width: float = 200
    _initial_height: float = 150

    def __init__(self, center: Point):
        self._polygons: list[Polygon] = []
        self._lines: list[Edge] = []
        self._ellipses: list[Ellipse] = []
        self._objects: list[DrawingObject] = []
        self._create_house(center)

    def _create_house(self, center: Point):
        self.init_center = Point(*center.render())
        self.safe_point: Point = Point(*center.render())
        self._objects.append(self.safe_point)
        initial_point: Point = Point(*center.render())
        initial_point.move(self._initial_width / 2, self._initial_height / 2)
        p1: Point = Point(*initial_point.render())
        initial_point.move(-self._initial_width, 0)
        p2: Point = Point(*initial_point.render())
        initial_point.move(0, -self._initial_height)
        p3: Point = Point(*initial_point.render())
        initial_point.move(self._initial_width, 0)
        p4: Point = Point(*initial_point.render())
        points: tuple[Point, ...] = p1, p2, p3, p4
        edges: list[Edge] = []
        for i in range(4):
            edges.append(Edge(points[i], points[(i + 1) % 4]))
        self._polygons.append(Polygon(tuple(edges)))
        initial_point.move(-self._initial_width / 2, -50)
        p5: Point = Point(*initial_point.render())
        edges.clear()
        p6: Point = Point(*p3.render())
        p7: Point = Point(*p4.render())
        self._polygons.append(Triangle(p5, p6, p7))
        initial_point.move(-self._initial_width / 2, 50)
        initial_point.move(self._initial_width / 6, 30)
        center: Point = Point(*initial_point.render())
        center.move(-20, -20)
        initial_point.move(0, -20)
        up_point: Point = Point(*initial_point.render())
        initial_point.move(0, 40)
        down_point: Point = Point(*initial_point.render())
        initial_point.move(-20, -20)
        left_point: Point = Point(*initial_point.render())
        initial_point.move(40, 0)
        right_point: Point = Point(*initial_point.render())
        initial_point.move(self._initial_width / 2, self._initial_height / 2 - 50)
        initial_point.move(-30, -40)
        self._ellipses.append(Ellipse(Point(*initial_point.render()), 60, 120))
        initial_point.move(30, 0)
        rhombus_p1: Point = Point(*initial_point.render())
        initial_point.move(30, 60)
        rhombus_p2: Point = Point(*initial_point.render())
        initial_point.move(-30, 60)
        rhombus_p3: Point = Point(*initial_point.render())
        initial_point.move(-30, -60)
        rhombus_p4: Point = Point(*initial_point.render())
        self._polygons.append(Polygon((Edge(rhombus_p1, rhombus_p2), Edge(rhombus_p1, rhombus_p4),
                                       Edge(rhombus_p2, rhombus_p3), Edge(rhombus_p3, rhombus_p4))))
        lp1 = Point(*rhombus_p1.render())
        lp2 = Point(*rhombus_p2.render())
        lp3 = Point(*rhombus_p3.render())
        lp4 = Point(*rhombus_p4.render())
        initial_point.move(-25, -85)
        lp5 = Point(*initial_point.render())
        initial_point.move(0, -20)
        lp6 = Point(*initial_point.render())
        initial_point.move(15, 10)
        lp7: Point = Point(*initial_point.render())
        initial_point.move(-30, 0)
        lp8: Point = Point(*initial_point.render())
        initial_point.move(0, -10)
        lp9: Point = Point(*initial_point.render())
        initial_point.move(30, 0)
        lp10: Point = Point(*initial_point.render())
        initial_point.move(0, 20)
        lp11: Point = Point(*initial_point.render())
        initial_point.move(-30, 0)
        lp12: Point = Point(*initial_point.render())
        self._polygons.append(Polygon((Edge(lp9, lp10), Edge(lp10, lp11), Edge(lp11, lp12), Edge(lp9, lp12))))
        self._lines.append(Edge(lp7, lp8))
        self._lines.append(Edge(lp5, lp6))
        self._lines.append(Edge(lp1, lp3))
        self._lines.append(Edge(lp2, lp4))
        self._lines.append(Edge(up_point, down_point))
        self._lines.append(Edge(left_point, right_point))
        self._ellipses.append(Ellipse(center, 40, 40))
        self._objects.extend(self._polygons)
        self._objects.extend(self._ellipses)
        self._objects.extend(self._lines)

    def move(self, x_offset: float, y_offset: float) -> None:
        for cur_object in self._objects:
            cur_object.move(x_offset, y_offset)

    def scale(self, center: Point, scale_x: float, scale_y: float) -> None:
        for cur_object in self._objects:
            cur_object.scale(center, scale_x, scale_y)

    def rotate(self, center: Point, angle: float) -> None:
        for cur_object in self._objects:
            cur_object.rotate(center, angle)

    def render(self) -> dict[str, tuple[DrawingObject.RenderedLine, ...]]:
        rendered_polygons: list[DrawingObject.RenderedLine] = []
        for cur_object in self._polygons:
            rendered_polygons.extend(cur_object.render())
        for cur_object in self._lines:
            rendered_polygons.append(cur_object.render())
        for cur_object in self._ellipses:
            rendered_polygons.extend(cur_object.render())
        res: dict[str, tuple[DrawingObject.RenderedLine, ...]] = {
            "polygons": tuple(rendered_polygons),
        }
        return res

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))
        return result


def main():
    pass
    # p1: Point = Point(60, 100)
    # p2: Point = Point(60, 80)
    # p3: Point = Point(70, 0)
    # triangle: Triangle = Triangle(p1, p2, p3)


if __name__ == '__main__':
    main()
