class CoordsTranslate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, x, y):
        return float(x) + self.x, float(y) + self.y

    @staticmethod
    def from_svg_transform(transform):
        x, y = transform.split("translate(")[1].split(")")[0].split(" ")
        return CoordsTranslate(x=float(x), y=float(y))
