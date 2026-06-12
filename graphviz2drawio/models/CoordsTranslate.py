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
        translation = transform.split("translate(", maxsplit=1)[1].split(
            ")",
            maxsplit=1,
        )[0]
        x, y = translation.split(" ", maxsplit=1)
        return CoordsTranslate(x=float(x), y=float(y))
