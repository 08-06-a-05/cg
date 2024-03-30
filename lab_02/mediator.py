import math

import logic
import copy


class SceneState:
    def __init__(self, center: logic.Point, objects: list[logic.ComplexDrawingObject]):
        self.scene_center: logic.Point = logic.Point(*center.render())
        self.objects: list[logic.ComplexDrawingObject] = copy.deepcopy(objects)


class SceneStatesHolder:

    def __init__(self, zero_state: SceneState):
        self.zero_state = zero_state
        self.states: list[SceneState] = [self.zero_state]

    def is_prev_state_reachable(self):
        return len(self.states) > 1

    def get_prev_state(self) -> SceneState:
        return self.states.pop()

    def get_reset_state(self) -> SceneState:
        self.states.clear()
        self.states.append(self.zero_state)
        return copy.deepcopy(self.states[0])

    def add_state(self, new_state: SceneState) -> None:
        self.states.append(new_state)


class SceneObjects:
    def __init__(self, scene_center: tuple[float, float]):
        self._scene_center: logic.Point = logic.Point(*scene_center)
        self.objects: list[logic.ComplexDrawingObject] = [logic.House(logic.Point(*scene_center))]
        self.states: SceneStatesHolder = SceneStatesHolder(SceneState(self._scene_center, self.objects))

    @property
    def scene_center(self) -> tuple[float, float]:
        return self._scene_center.render()

    def move(self, x_offset: float, y_offset: float):
        self.states.add_state(SceneState(self._scene_center, self.objects))
        self._scene_center.move(x_offset, y_offset)
        for cur_object in self.objects:
            cur_object.move(x_offset, y_offset)

    def scale(self, center: tuple[float, float], scale_x: float, scale_y: float):
        self.states.add_state(SceneState(self._scene_center, self.objects))
        self._scene_center.scale(logic.Point(*center), scale_x, scale_y)
        for cur_object in self.objects:
            cur_object.scale(logic.Point(*center), scale_x, scale_y)

    def rotate(self, center: tuple[float, float], angle: float):
        angle = angle / 180 * math.pi
        self.states.add_state(SceneState(self._scene_center, self.objects))
        self._scene_center.rotate(logic.Point(*center), angle)
        for cur_object in self.objects:
            cur_object.rotate(logic.Point(*center), angle)

    def render(self) -> ...:
        rendered_objects = {"polygons": []}
        for cur_object in self.objects:
            cur_render = cur_object.render()
            rendered_objects["polygons"].extend(cur_render["polygons"])
        return rendered_objects

    def move_to_center(self, screen_center: tuple[float, float]):
        x_offset: float = self.scene_center[0] - screen_center[0]
        y_offset: float = self.scene_center[1] - screen_center[1]
        self.move(x_offset, y_offset)

    def get_scene_center(self) -> tuple[float, float]:
        return self.scene_center

    def is_prev_state_reachable(self):
        return self.states.is_prev_state_reachable()

    def get_prev_state(self) -> None:
        new_state = self.states.get_prev_state()
        self.objects = new_state.objects
        self._scene_center = new_state.scene_center

    def get_reset_state(self) -> None:
        new_state = self.states.get_reset_state()
        self.objects = new_state.objects
        self._scene_center = new_state.scene_center


if __name__ == "__main__":
    SceneObjects((0, 0))
