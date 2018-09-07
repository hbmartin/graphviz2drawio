from . import LinearRegression


class Curve:
    def __init__(self, start, end, cb):
        super(Curve, self).__init__()
        self.start = start
        self.end = end
        self.cb = cb

    def __str__(self):
        control = "[" + (str(self.cb) if self.cb is not None else "None") + "]"
        return str(self.start) + ", " + control + ", " + str(self.end)

    @staticmethod
    def is_linear(points):
        r2 = LinearRegression.coefficients(points)[2]
        return r2 > 0.9

    def cubic_bezier_coordinates(self, t):
        x = Curve.cubic_bezier(
            [self.cb[0].real, self.cb[1].real, self.cb[2].real, self.cb[3].real], t
        )
        y = Curve.cubic_bezier(
            [self.cb[0].imag, self.cb[1].imag, self.cb[2].imag, self.cb[3].imag], t
        )
        return complex(x, y)

    @staticmethod
    def cubic_bezier(p, t):
        return (
            (((1.0 - t) ** 3) * p[0])
            + (3 * t * ((1.0 - t) ** 2) * p[1])
            + (3.0 * (t ** 2) * (1.0 - t) * p[2])
            + ((t ** 3) * p[3])
        )
