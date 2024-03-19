from __future__ import annotations

import copy
import math
from typing import Final, Optional


class Point:
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


class Vector:
    """
    Вектор. Представлен координатами своего конца. Координаты начала всегда (0, 0). Не нормализован.

    :param x: Координата конца
    :param y: Координата конца
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def normal(self) -> Vector:
        return Vector(self.y, -self.x)


class Edge:

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

    def dir_vector(self) -> Vector:
        return Vector(self.p1.x - self.p2.x, self.p1.y - self.p2.y)

    def length(self) -> float:
        return ((self.p1.x - self.p2.x) ** 2 + (self.p1.y - self.p2.y) ** 2) ** 0.5

    def render(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return self.p1.render(), self.p2.render()

    def move(self, dx: float, dy: float):
        self.p1.move(dx, dy)
        self.p2.move(dx, dy)


class Polygon:

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

    def render(self) -> tuple[tuple[tuple[float, float], tuple[float, float]], ...]:
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

    def scale(self, scale_x: float, scale_y: float):
        for p in self.points:
            p.x *= scale_x
            p.y *= scale_y

    def square(self) -> float:
        return 0

    def circumcircle_square(self) -> float:
        return 0

    def circumcircle_radius(self) -> float:
        return 0

    def circumcircle(self) -> Optional[Circle]:
        return None


class Triangle(Polygon):

    def __init__(self, e1: Edge, e2: Edge, e3: Edge):
        super().__init__((e1, e2, e3))

    def square(self) -> float:
        semiperimeter: float = 0
        for edge in self.edges:
            semiperimeter += edge.length() / 2
        square: float = 1
        for edge in self.edges:
            square *= semiperimeter - edge.length()
        return (square * semiperimeter) ** 0.5

    @classmethod
    def _determinant(cls, matrix: tuple[tuple[float, ...], ...] | list[list[float]]) -> float:
        if len(matrix) == 1:
            return matrix[0][0]
        split_matrix: tuple[tuple[float, ...], ...] = tuple(el[1:] for el in matrix)
        res: float = 0
        sign: int = 1
        for i in range(len(matrix)):
            res += matrix[i][0] * cls._determinant(split_matrix[:i] + split_matrix[i + 1:]) * sign
            sign *= -1
        return res

    @classmethod
    def _crammer(cls, matrix: tuple[tuple[float, ...], ...], values: tuple[float, ...]) -> tuple[float, ...]:
        common_determinant: float = cls._determinant(matrix)
        ans: list[float] = []
        for i in range(len(matrix)):
            updated_matrix: list[list[float]] = [list(el) for el in matrix]
            for k in range(len(matrix)):
                updated_matrix[k][i] = values[k]
            individual_determinant: float = cls._determinant(updated_matrix)
            ans.append(individual_determinant / common_determinant)
        return tuple(ans)

    def circumcircle_center(self) -> Point:
        e1_center: Point = self.edges[0].center()
        e1_dir: Vector = self.edges[0].dir_vector()
        e2_center: Point = self.edges[1].center()
        e2_dir: Vector = self.edges[1].dir_vector()
        normal_e1: Vector = e1_dir.normal()
        normal_e2: Vector = e2_dir.normal()
        matrix = ((normal_e1.x, -normal_e2.x), (normal_e1.y, -normal_e2.y))
        values = (e2_center.x - e1_center.x, e2_center.y - e1_center.y)
        coefs = self._crammer(matrix, values)
        center = (e1_center.x + coefs[0] * normal_e1.x, e1_center.y + coefs[0] * normal_e1.y)
        return Point(*center)

    def circumcircle_radius(self) -> float:
        sides_product: float = 1
        for edge in self.edges:
            sides_product *= edge.length()
        return sides_product / self.square() / 4

    def circumcircle_square(self) -> float:
        return self.circumcircle_radius() ** 2 * math.pi

    def circumcircle(self) -> Circle:
        return Circle(self.circumcircle_center(), self.circumcircle_radius())


class Circle:

    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius

    def square(self) -> float:
        return math.pi * self.radius * self.radius

    def render(self) -> tuple[float, float, float, float]:
        return self.center.x - self.radius, self.center.y - self.radius, self.radius * 2, self.radius * 2

    def move(self, x_offset: float, y_offset: float):
        self.center.x += x_offset
        self.center.y += y_offset

    def scale(self, scale: float):
        self.radius *= scale

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memodict))
        return result


def main():
    p1: Point = Point(60, 100)
    p2: Point = Point(60, 80)
    p3: Point = Point(70, 0)
    e1: Edge = Edge(p1, p2)
    e2: Edge = Edge(p1, p3)
    e3: Edge = Edge(p2, p3)
    triangle: Triangle = Triangle(e1, e2, e3)
    print(triangle.square())


if __name__ == '__main__':
    main()
