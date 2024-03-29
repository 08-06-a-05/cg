import math
import typing

import logic
import copy


class SceneObjects:
    def __init__(self, screen_center: tuple[float, float]):
        self.screen_center = logic.Point(*screen_center)
        self.objects: list[logic.DrawingObject] = [logic.House(logic.Point(*screen_center))]
        self.states: list[typing.Optional[logic.House]] = [None] * 1000
        self.states[0] = copy.deepcopy(self.objects[0])
        self.index_state: int = -1

    def is_prev_state_reacheble(self):
        return self.index_state >= 0

    def get_prev_state(self):
        self.objects[0] = self.states[self.index_state]
        self.index_state -= 1

    def get_reset_state(self):
        self.objects[0] = self.states[0]
        self.index_state = -1

    def move_objects(self, x_offset: float, y_offset: float):
        self.index_state += 1
        self.states[self.index_state] = copy.deepcopy(self.objects[0])
        for cur_object in self.objects:
            cur_object.move(x_offset, y_offset)

    def scale_objects(self, center: tuple[float, float], scale_x: float, scale_y: float):
        self.index_state += 1
        self.states[self.index_state] = copy.deepcopy(self.objects[0])
        for cur_object in self.objects:
            cur_object.scale(logic.Point(*center), scale_x, scale_y)

    def rotate_objects(self, center: tuple[float, float], angle: float):
        self.index_state += 1
        self.states[self.index_state] = copy.deepcopy(self.objects[0])
        angle = angle / 180 * math.pi
        for cur_object in self.objects:
            cur_object.rotate(logic.Point(*center), angle)

    def render_objects(self) -> ...:
        rendered_objects = {"polygons": [], "circles": []}
        for cur_object in self.objects:
            cur_render = cur_object.render()
            rendered_objects["polygons"].extend(cur_render["polygons"])
            rendered_objects["circles"].extend(cur_render["circles"])
        return rendered_objects

    def center_objects(self):
        self.index_state += 1
        self.states[self.index_state] = copy.deepcopy(self.objects[0])
        self.objects[0].center()

    def get_center(self):
        res = [self.objects[0].safe_point.x, self.objects[0].safe_point.y]
        res[1] = 2 * self.objects[0].init_center.y - res[1]
        return res

