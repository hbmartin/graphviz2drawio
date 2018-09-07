from abc import ABC, abstractmethod


class FromSvgFactory(ABC):
    def __init__(self, coords):
        self.coords = coords

    @abstractmethod
    def from_svg(self, svg_data):
        pass