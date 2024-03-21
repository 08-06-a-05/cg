import copy
from typing import Optional
import sys

import logic


class SceneObjects:
    def __init__(self, screen_center: tuple[float, float]):
        self.objects: tuple[logic.DrawingObject] = logic.House(logic.Point(*screen_center)),

    def move_objects(self, x_offset: float, y_offset: float):
        for cur_object in self.objects:
            cur_object.move(x_offset, y_offset)

    def scale_objects(self, center: tuple[float, float], scale: float):
        for cur_object in self.objects:
            cur_object.scale(logic.Point(*center), scale)

    def rotate_objects(self, center: tuple[float, float], angle: float):
        for cur_object in self.objects:
            cur_object.rotate(logic.Point(*center), angle)
