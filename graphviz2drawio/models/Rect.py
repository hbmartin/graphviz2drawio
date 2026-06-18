_ANCHOR_EPSILON = 1e-6
_ZERO_DIRECTION_EPSILON = 1e-12


class Rect:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        image: str | None = None,
    ) -> None:
        # x,y is the top left corner
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bottom = y + height
        self.right = x + width
        self.image = image

    def x_ratio(self, search: float) -> float:
        if search < self.x:
            return 0
        if search > self.x + self.width:
            return 1
        return (search - self.x) / self.width

    def y_ratio(self, search: float) -> float:
        if search < self.y:
            return 0
        if search > self.y + self.height:
            return 1
        return (search - self.y) / self.height

    def to_dict_str(self) -> dict[str, str]:
        return {
            "x": str(self.x),
            "y": str(self.y),
            "width": str(self.width),
            "height": str(self.height),
        }

    def anchor_fraction_along_line(
        self,
        point: complex,
        direction: complex,
    ) -> tuple[float, float] | None:
        if abs(direction) <= _ZERO_DIRECTION_EPSILON:
            return None

        candidates: list[tuple[float, float, float]] = []
        if abs(direction.real) > _ZERO_DIRECTION_EPSILON:
            self._add_vertical_hit(candidates, point, direction, self.x)
            self._add_vertical_hit(candidates, point, direction, self.right)
        if abs(direction.imag) > _ZERO_DIRECTION_EPSILON:
            self._add_horizontal_hit(candidates, point, direction, self.y)
            self._add_horizontal_hit(candidates, point, direction, self.bottom)

        if not candidates:
            return None

        _distance, hit_x, hit_y = min(candidates, key=lambda candidate: candidate[0])
        if _distance > max(self.width, self.height):
            return None

        x_fraction = (hit_x - self.x) / self.width
        y_fraction = (hit_y - self.y) / self.height
        if not _is_fraction_in_bounds(x_fraction) or not _is_fraction_in_bounds(
            y_fraction,
        ):
            return None
        return _clamp_fraction(x_fraction), _clamp_fraction(y_fraction)

    def _add_vertical_hit(
        self,
        candidates: list[tuple[float, float, float]],
        point: complex,
        direction: complex,
        x: float,
    ) -> None:
        t = (x - point.real) / direction.real
        y = point.imag + t * direction.imag
        if self.y - _ANCHOR_EPSILON <= y <= self.bottom + _ANCHOR_EPSILON:
            candidates.append((abs(t) * abs(direction), x, y))

    def _add_horizontal_hit(
        self,
        candidates: list[tuple[float, float, float]],
        point: complex,
        direction: complex,
        y: float,
    ) -> None:
        t = (y - point.imag) / direction.imag
        x = point.real + t * direction.real
        if self.x - _ANCHOR_EPSILON <= x <= self.right + _ANCHOR_EPSILON:
            candidates.append((abs(t) * abs(direction), x, y))


def _is_fraction_in_bounds(value: float) -> bool:
    return -_ANCHOR_EPSILON <= value <= 1 + _ANCHOR_EPSILON


def _clamp_fraction(value: float) -> float:
    return min(max(value, 0), 1)
