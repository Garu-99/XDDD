from typing import Tuple


Vector2 = Tuple[float, float]


class AlgebraService:

    @staticmethod
    def normalize(v: Vector2) -> Vector2:
        max_coord = max(abs(v[0]), abs(v[1]))
        return v[0] / max_coord, v[1] / max_coord

    @staticmethod
    def add(v1: Vector2, v2: Vector2):
        return v1[0] + v2[0], v1[1] + v2[1]

    @staticmethod
    def sub(v1: Vector2, v2: Vector2):
        return v1[0] - v2[0], v1[1] - v2[1]

    @staticmethod
    def mult(v: Vector2, scalar: float):
        return v[0] * scalar, v[1] * scalar

    @staticmethod
    def get_direction(v1: Vector2, v2: Vector2):
        abs_dir = AlgebraService.sub(v2, v1)
        return AlgebraService.normalize(abs_dir)

    @staticmethod
    def to_int_vector(v: Vector2) -> Tuple[int, int]:
        return int(v[0]), int(v[1])
