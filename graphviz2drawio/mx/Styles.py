from enum import Enum

from . import Shape


class Styles(Enum):
    NODE = "verticalAlign=top;align=left;overflow=fill;html=1;rounded=0;shadow=0;comic=0;labelBackgroundColor=none;strokeColor={stroke};strokeWidth=1;fillColor={fill};"
    EDGE = "rounded=1;html=1;exitX={exit_x:.3g};exitY={exit_y:.3g};entryX={entry_x:.3g};entryY={entry_y:.3g};jettySize=auto;curved={curved};endArrow={end_arrow};dashed={dashed};endFill={end_fill};"
    TEXT = "margin:0px;text-align:{align};{margin};font-size:{size}px;font-family:{family};color:{color};"

    ELLIPSE = "ellipse;" + NODE
    CIRCLE = "ellipse;aspect=fixed;" + NODE
    HEXAGON = "shape=hexagon;perimeter=hexagonPerimeter2;" + NODE
    EGG = "shape=mxgraph.flowchart.display;direction=south;" + NODE
    TRIANGLE = "triangle;direction=north;" + NODE
    LINE = (
        "line;strokeWidth=2;verticalAlign=bottom;labelPosition=center;verticalLabelPosition=top;align=center;"
        + NODE
    )
    DIAMOND = "rhombus;" + NODE
    TRAPEZOID = "shape=trapezoid;perimeter=trapezoidPerimeter;" + NODE
    PARALLELOGRAM = "shape=parallelogram;perimeter=parallelogramPerimeter;" + NODE
    HOUSE = "shape=offPageConnector;direction=west;" + NODE
    PENTAGON = "shape=mxgraph.basic.pentagon;" + NODE
    OCTAGON = (
        "shape=mxgraph.basic.octagon2;align=center;verticalAlign=middle;dx=15;" + NODE
    )
    DOUBLE_CIRCLE = "ellipse;shape=doubleEllipse;aspect=fixed;" + NODE
    DOUBLE_OCTAGON = (
        "shape=image;html=1;verticalAlign=middle;verticalLabelPosition=middle;imageAspect=0;aspect=fixed;image=https://cdn4.iconfinder.com/data/icons/feather/24/octagon-128.png;labelPosition=center;align=center;"
        + NODE
    )
    INV_TRIANGLE = "triangle;direction=south;" + NODE
    INV_TRAPEZOID = (
        "shape=trapezoid;perimeter=trapezoidPerimeter;direction=west;" + NODE
    )
    INV_HOUSE = "shape=offPageConnector;direction=east;" + NODE
    SQUARE = "aspect=fixed;" + NODE
    STAR = (
        "shape=mxgraph.basic.star;labelPosition=center;align=center;verticalLabelPosition=middle;verticalAlign=middle;"
        + NODE
    )
    UNDERLINE = "line;strokeWidth=2;verticalAlign=bottom;labelPosition=center;verticalLabelPosition=top;align=center;"
    CYLINDER = "shape=cylinder;boundedLbl=1;backgroundOutline=1;" + NODE
    NOTE = "shape=note;backgroundOutline=1;" + NODE
    TAB = "shape=folder;tabWidth=40;tabHeight=14;tabPosition=left;" + NODE
    FOLDER = (
        "shape=mxgraph.office.concepts.folder;outlineConnect=0;align=center;verticalLabelPosition=middle;verticalAlign=middle;labelPosition=center;shadow=0;dashed=0;"
        + NODE
    )
    CUBE = "shape=cube;boundedLbl=1;backgroundOutline=1;" + NODE
    COMPONENT = (
        "shape=component;align=center;spacingLeft=36;verticalAlign=bottom;" + NODE
    )
    RPROMOTER = (
        "shape=mxgraph.arrows2.bendArrow;dy=15;dx=38;notch=0;arrowHead=55;rounded=0;shadow=0;dashed=0;align=center;verticalAlign=middle;"
        + NODE
    )
    LPROMOTER = "flipH=1;" + RPROMOTER
    CDS = (
        "shape=mxgraph.arrows2.arrow;dy=0;dx=10;notch=0;shadow=0;dashed=0;align=center;verticalAlign=middle;"
        + NODE
    )
    RARROW = (
        "shape=mxgraph.arrows2.arrow;dy=0.6;dx=40;align=center;labelPosition=center;notch=0;strokeWidth=2;verticalLabelPosition=middle;verticalAlign=middle;"
        + NODE
    )
    LARROW = "flipH=1;" + RARROW

    @staticmethod
    def get_for_shape(dot_shape):
        if dot_shape in (None, Shape.ELLIPSE, Shape.OVAL):
            return Styles.ELLIPSE
        elif dot_shape in (Shape.BOX, Shape.RECT, Shape.RECTANGLE):
            return Styles.NODE
        elif dot_shape in (Shape.HEXAGON, Shape.POLYGON):
            return Styles.HEXAGON
        elif dot_shape == Shape.CIRCLE:
            return Styles.CIRCLE
        elif dot_shape == Shape.EGG:
            return Styles.EGG
        elif dot_shape == Shape.TRIANGLE:
            return Styles.TRIANGLE
        elif dot_shape == Shape.PLAIN:
            return Styles.LINE
        elif dot_shape == Shape.DIAMOND:
            return Styles.DIAMOND
        elif dot_shape == Shape.TRAPEZIUM:
            return Styles.TRAPEZOID
        elif dot_shape == Shape.PARALLELOGRAM:
            return Styles.PARALLELOGRAM
        elif dot_shape == Shape.HOUSE:
            return Styles.HOUSE
        elif dot_shape == Shape.PENTAGON:
            return Styles.PENTAGON
        elif dot_shape == Shape.OCTAGON:
            return Styles.OCTAGON
        elif dot_shape == Shape.DOUBLE_CIRCLE:
            return Styles.DOUBLE_CIRCLE
        elif dot_shape == Shape.DOUBLE_OCTAGON:
            return Styles.DOUBLE_OCTAGON
        elif dot_shape == Shape.INV_TRIANGLE:
            return Styles.INV_TRIANGLE
        elif dot_shape == Shape.INV_TRAPEZIUM:
            return Styles.INV_TRAPEZOID
        elif dot_shape == Shape.INV_HOUSE:
            return Styles.INV_HOUSE
        elif dot_shape == Shape.SQUARE:
            return Styles.SQUARE
        elif dot_shape == Shape.STAR:
            return Styles.STAR
        elif dot_shape == Shape.UNDERLINE:
            return Styles.UNDERLINE
        elif dot_shape == Shape.CYLINDER:
            return Styles.CYLINDER
        elif dot_shape == Shape.NOTE:
            return Styles.NODE
        elif dot_shape == Shape.TAB:
            return Styles.TAB
        elif dot_shape == Shape.FOLDER:
            return Styles.FOLDER
        elif dot_shape == Shape.BOX_3D:
            return Styles.CUBE
        elif dot_shape == Shape.COMPONENT:
            return Styles.COMPONENT
        elif dot_shape in (Shape.PROMOTER, Shape.RPROMOTER):
            return Styles.RPROMOTER
        elif dot_shape == Shape.LPROMOTER:
            return Styles.LPROMOTER
        elif dot_shape == Shape.CDS:
            return Styles.CDS
        elif dot_shape == Shape.RARROW:
            return Styles.RARROW
        elif dot_shape == Shape.LARROW:
            return Styles.LARROW
        else:
            return Styles.NODE

    def format(self, **values):
        return self.value.format(**values)
