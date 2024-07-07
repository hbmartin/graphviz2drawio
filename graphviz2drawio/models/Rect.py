class Rect:
    def __init__(self, x: float, y: float, width: float, height: float, image: str | None = None) -> None:
        # x,y is the top left corner
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bottom = y + height
        self.right = x + width
        self.image = image

    def x_ratio(self, search):
        if search < self.x:
            return 0
        if search > self.x + self.width:
            return 1
        ratio = (search - self.x) / self.width
        return self._approx(ratio, 0.5, 0.1)

    def y_ratio(self, search):
        if search < self.y:
            return 0
        if search > self.y + self.height:
            return 1
        ratio = (search - self.y) / self.height
        return self._approx(ratio, 0.5, 0.1)

    @staticmethod
    def _approx(value, center, delta):
        if abs(value - center) < delta:
            return center
        return value

    def to_dict_str(self):
        return {
            "x": str(self.x),
            "y": str(self.y),
            "width": str(self.width),
            "height": str(self.height),
        }

    def closest_point_along_perimeter(self, x: float, y: float):
        x = clamp(x, self.x, self.right)
        y = clamp(y, self.y, self.bottom)

        dl = abs(x - self.x)
        dr = abs(x - self.right)
        dt = abs(y - self.y)
        db = abs(y - self.bottom)
        m = min(dl, dr, dt, db)

        if m == dt:
            return x, self.y
        if m == db:
            return x, self.bottom
        if m == dl:
            return self.x, y

        return self.right, y

    def relative_location_along_perimeter(self, point: complex) -> tuple[float, float]:
        p = self.closest_point_along_perimeter(point.real, point.imag)
        return self.x_ratio(p[0]), self.y_ratio(p[1])


def clamp(value, min_v, max_v):
    return max(min(value, max_v), min_v)
