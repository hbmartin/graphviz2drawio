from enum import Enum
from graphviz2drawio.gv import GvShape


class Styles(Enum):
    NODE = "verticalAlign=top;align=left;overflow=fill;html=1;rounded=0;shadow=0;comic=0;labelBackgroundColor=none;strokeColor={stroke};strokeWidth=1;fillColor={fill};"
    EDGE = "rounded=1;html=1;exitX={exit_x:.3g};exitY={exit_y:.3g};entryX={entry_x:.3g};entryY={entry_y:.3g};jettySize=auto;orthogonalLoop=1;endArrow={end_arrow};dashed={dashed};endFill={end_fill};"
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
        if dot_shape is None or dot_shape == GvShape.ELLIPSE or dot_shape == GvShape.OVAL:
            return Styles.ELLIPSE
        elif (
                dot_shape == GvShape.BOX
                or dot_shape == GvShape.RECT
                or dot_shape == GvShape.RECTANGLE
        ):
            return Styles.NODE
        elif dot_shape == GvShape.HEXAGON or dot_shape == GvShape.POLYGON:
            return Styles.HEXAGON
        elif dot_shape == GvShape.CIRCLE:
            return Styles.CIRCLE
        elif dot_shape == GvShape.EGG:
            return Styles.EGG
        elif dot_shape == GvShape.TRIANGLE:
            return Styles.TRIANGLE
        elif dot_shape == GvShape.PLAIN:
            return Styles.LINE
        elif dot_shape == GvShape.DIAMOND:
            return Styles.DIAMOND
        elif dot_shape == GvShape.TRAPEZIUM:
            return Styles.TRAPEZOID
        elif dot_shape == GvShape.PARALLELOGRAM:
            return Styles.PARALLELOGRAM
        elif dot_shape == GvShape.HOUSE:
            return Styles.HOUSE
        elif dot_shape == GvShape.PENTAGON:
            return Styles.PENTAGON
        elif dot_shape == GvShape.OCTAGON:
            return Styles.OCTAGON
        elif dot_shape == GvShape.DOUBLE_CIRCLE:
            return Styles.DOUBLE_CIRCLE
        elif dot_shape == GvShape.DOUBLE_OCTAGON:
            return Styles.DOUBLE_OCTAGON
        elif dot_shape == GvShape.INV_TRIANGLE:
            return Styles.INV_TRIANGLE
        elif dot_shape == GvShape.INV_TRAPEZIUM:
            return Styles.INV_TRAPEZOID
        elif dot_shape == GvShape.INV_HOUSE:
            return Styles.INV_HOUSE
        elif dot_shape == GvShape.SQUARE:
            return Styles.SQUARE
        elif dot_shape == GvShape.STAR:
            return Styles.STAR
        elif dot_shape == GvShape.UNDERLINE:
            return Styles.UNDERLINE
        elif dot_shape == GvShape.CYLINDER:
            return Styles.CYLINDER
        elif dot_shape == GvShape.NOTE:
            return Styles.NODE
        elif dot_shape == GvShape.TAB:
            return Styles.TAB
        elif dot_shape == GvShape.FOLDER:
            return Styles.FOLDER
        elif dot_shape == GvShape.BOX_3D:
            return Styles.CUBE
        elif dot_shape == GvShape.COMPONENT:
            return Styles.COMPONENT
        elif dot_shape == GvShape.PROMOTER or dot_shape == GvShape.RPROMOTER:
            return Styles.RPROMOTER
        elif dot_shape == GvShape.LPROMOTER:
            return Styles.LPROMOTER
        elif dot_shape == GvShape.CDS:
            return Styles.CDS
        elif dot_shape == GvShape.RARROW:
            return Styles.RARROW
        elif dot_shape == GvShape.LARROW:
            return Styles.LARROW
        else:
            return Styles.NODE

    def format(self, **values):
        return self.value.format(**values)
