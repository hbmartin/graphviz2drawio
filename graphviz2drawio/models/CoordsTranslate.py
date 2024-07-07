class CoordsTranslate:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def complex_translate(self, cnum: complex) -> complex:
        return complex(cnum.real + self.x, cnum.imag + self.y)

    def translate(self, x: float | str, y: float | str) -> tuple[float, float]:
        return float(x) + self.x, float(y) + self.y

    @staticmethod
    def from_svg_transform(transform: str) -> "CoordsTranslate":
        x, y = transform.split("translate(")[1].split(")")[0].split(" ")
        return CoordsTranslate(x=float(x), y=float(y))
