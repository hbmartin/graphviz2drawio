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
        parts = translation.replace(",", " ").split()
        x = float(parts[0])
        y = float(parts[1]) if len(parts) > 1 else 0.0
        return CoordsTranslate(x=x, y=y)
