import copy
from typing import Optional

import logic


class SceneObjects:
    def __init__(self):
        self.points: dict[int, logic.Point] = {}
        self.edges: dict[int, logic.Edge] = {}
        self.polygons: dict[int, logic.Polygon] = {}
        self.circles: dict[int, logic.Circle] = {}

    def add_point(self, x: float, y: float) -> int:
        new_point = logic.Point(x, y)
        self.points[id(new_point)] = new_point
        return id(new_point)

    def set_point_pos(self, point_id: int, x: Optional[float] = None, y: Optional[float] = None):
        self.points[point_id].set_pos(x, y)

    def get_point_pos(self, point_id: int) -> tuple[float, float]:
        return self.points[point_id].get_pos()

    def move_point(self, point_id: int, dx: float, dy: float):
        self.points[point_id].move(dx, dy)

    def remove_point(self, point_id: int) -> bool:
        self.points.pop(point_id)
        return True

    def polygon_square(self, polygon_id: int) -> float:
        return self.polygons[polygon_id].square()

    def polygon_circumcircle_radius(self, polygon_id: int) -> float:
        return self.polygons[polygon_id].circumcircle_radius()

    def polygon_circumcircle_square(self, polygon_id: int) -> float:
        return self.polygons[polygon_id].circumcircle_square()

    def remove_polygon(self, polygon_id: int):
        self.polygons.pop(polygon_id)

    def move_polygon(self, polygon_id: int, dx: float, dy: float):
        self.polygons[polygon_id].move(dx, dy)

    def scale_polygon(self, polygon_id: int, scale_x: float, scale_y: float):
        self.polygons[polygon_id].scale(scale_x, scale_y)

    def add_circumcircle(self, polygon_id: int) -> int:
        new_circle: logic.Circle = self.polygons[polygon_id].circumcircle()
        self.circles[id(new_circle)] = new_circle
        return id(new_circle)

    def scale_circle(self, circle_id: int, scale: float):
        self.circles[circle_id].scale(scale)

    def remove_circle(self, circle_id: int):
        self.circles.pop(circle_id)

    def circle_center(self, circle_id: int) -> tuple[float, float]:
        return self.circles[circle_id].center.render()

    def circle_radius(self, circle_id: int) -> float:
        return self.circles[circle_id].radius

    def circle_square(self, circle_id: int) -> float:
        return self.circles[circle_id].square()

    def polygon_points(self, polygon_id: int) -> tuple[tuple[float, float], ...]:
        return self.polygons[polygon_id].get_points()

    def move_circle(self, circle_id: int, dx: float, dy: float):
        self.circles[circle_id].move(dx, dy)

    def points_num(self) -> int:
        return len(self.points)

    def render_point(self, point_id: int) -> tuple[float, float]:
        return self.points[point_id].render()

    def render_circle(self, circle_id: int) -> tuple[float, float, float, float]:
        return self.circles[circle_id].render()

    def render_polygon(self, polygon_id: int) -> tuple[tuple[tuple[float, float], tuple[float, float]], ...]:
        return self.polygons[polygon_id].render()

    def remove_edge(self, edge_id: int):
        self.edges.pop(edge_id)

    def remove_object(self, object_id: int):
        if object_id in self.points:
            self.remove_point(object_id)
        elif object_id in self.edges:
            self.remove_edge(object_id)
        elif object_id in self.polygons:
            self.remove_polygon(object_id)
        elif object_id in self.circles:
            self.remove_circle(object_id)

    def find_selected_triangle(self) -> id:
        max_range: float = 0.0
        selected_triangle: Optional[logic.Triangle] = None
        points_id_list: list[int] = list(self.points.keys())
        for i in range(len(points_id_list) - 2):
            p1: logic.Point = self.points[points_id_list[i]]
            for k in range(i + 1, len(points_id_list) - 1):
                p2: logic.Point = self.points[points_id_list[k]]
                for z in range(k + 1, len(points_id_list)):
                    p3: logic.Point = self.points[points_id_list[z]]
                    try:
                        current_triangle: logic.Triangle = logic.Triangle(logic.Edge(p1, p2), logic.Edge(p1, p3),
                                                                          logic.Edge(p2, p3))
                    except ValueError:
                        continue
                    if current_triangle.circumcircle_square() - current_triangle.square() > max_range:
                        max_range = current_triangle.circumcircle_square() - current_triangle.square()
                        selected_triangle = current_triangle
        if selected_triangle is None:
            return None
        cp_triangle: logic.Triangle = copy.deepcopy(selected_triangle)
        self.polygons[id(cp_triangle)] = cp_triangle
        return id(cp_triangle)
