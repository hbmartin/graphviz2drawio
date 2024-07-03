from . import LinearRegression

linear_min_r2 = 0.9


class Curve:
    def __init__(self, start, end, cb, cbset=None) -> None:
        """Takes complex numbers for start, end, and list of 4 Bezier control points."""
        if cbset is None:
            cbset = []
        self.start = start
        self.end = end
        assert cb is None or len(cb) == 4  # TODO: emit value error instead
        self.cb = cb
        self.cbset = cbset

    def __str__(self) -> str:
        control = "[" + (str(self.cb) if self.cb is not None else "None") + "]"
        return f"{self.start} , {control}, {self.end}"

    @staticmethod
    def is_linear(points, threshold=linear_min_r2):
        """Returns a boolean indicating whether a list of complex points is linear.

        Takes a list of complex points and optional minimum R**2 threshold for linear regression.
        """
        r2 = LinearRegression.coefficients(points)[2]
        return r2 > threshold

    def cubic_bezier_coordinates(self, t):
        """Returns a complex number representing the point along the cubic bezier curve.

        Takes parametric parameter t where 0 <= t <= 1
        """
        x = Curve._cubic_bezier(self._cb("real"), t)
        y = Curve._cubic_bezier(self._cb("imag"), t)
        return complex(x, y)

    def _cb(self, prop):
        return [getattr(x, prop) for x in self.cb]

    @staticmethod
    def _cubic_bezier(p, t) -> float:
        """Returns a float representing the point along the cubic Bézier in the given dimension.

        Takes ordered list of 4 control points [P0, P1, P2, P3] and parametric parameter t where 0 <= t <= 1

        implements explicit form of https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
        """
        assert 0 <= t <= 1  # TODO: emit value error instead
        return (
            (((1.0 - t) ** 3) * p[0])
            + (3.0 * t * ((1.0 - t) ** 2) * p[1])
            + (3.0 * (t**2) * (1.0 - t) * p[2])
            + ((t**3) * p[3])
        )
