class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def to_dict_int(self):
        return {
            "x": str(int(self.x)),
            "y": str(int(self.y)),
            "width": str(int(self.width)),
            "height": str(int(self.height)),
        }
