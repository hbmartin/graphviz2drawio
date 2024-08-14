from enum import Enum

from . import Shape


# Make this subclass StrEnum when dropping Py 3.10 support
class Styles(Enum):
    NODE = (
        "verticalAlign={vertical_align};html=1;rounded=0;labelBackgroundColor=none;strokeColor={stroke};"
        "strokeWidth=1;fillColor={fill};"
    )
    EDGE = (
        "html=1;endArrow={end_arrow};dashed={dashed};endFill={end_fill};startArrow={start_arrow};"
        "startFill={start_fill};fillColor={stroke};strokeColor={stroke};"
    )
    EDGE_LABEL = (
        "edgeLabel;html=1;align=center;verticalAlign=bottom;resizable=0;points=[];"
    )
    EDGE_INVIS = (
        "rounded=1;html=1;exitX={exit_x:.3g};exitY={exit_y:.3g};jettySize=auto;curved={curved};"
        "endArrow={end_arrow};dashed={dashed};endFill={end_fill};"
    )

    TEXT_VALUE = (
        "{open_tags}<font style='font-size: {size}px;' face='{family}' color='{color}'>"
        "{text}</font>{close_tags}"
    )

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
    OCTAGON = "shape=mxgraph.basic.octagon2;align=center;dx=15;" + NODE
    DOUBLE_CIRCLE = "ellipse;shape=doubleEllipse;aspect=fixed;" + NODE
    DOUBLE_OCTAGON = (
        "shape=image;html=1;verticalLabelPosition=middle;imageAspect=0;aspect=fixed;"
        "image=https://cdn4.iconfinder.com/data/icons/feather/24/octagon-128.png;labelPosition=center;align=center;"
        + NODE
    )
    INV_TRIANGLE = "triangle;direction=south;" + NODE
    INV_TRAPEZOID = (
        "shape=trapezoid;perimeter=trapezoidPerimeter;direction=west;" + NODE
    )
    INV_HOUSE = "shape=offPageConnector;direction=east;" + NODE
    SQUARE = "aspect=fixed;" + NODE
    STAR = (
        "shape=mxgraph.basic.star;labelPosition=center;align=center;verticalLabelPosition=middle;"
        + NODE
    )
    UNDERLINE = (
        "line;strokeWidth=2;verticalAlign=bottom;labelPosition=center;"
        "verticalLabelPosition=top;align=center;"
    )
    CYLINDER = "shape=cylinder;boundedLbl=1;backgroundOutline=1;" + NODE
    NOTE = "shape=note;backgroundOutline=1;" + NODE
    TAB = "shape=folder;tabWidth=40;tabHeight=14;tabPosition=left;" + NODE
    FOLDER = (
        "shape=mxgraph.office.concepts.folder;outlineConnect=0;align=center;verticalLabelPosition=middle;"
        "labelPosition=center;shadow=0;dashed=0;" + NODE
    )
    CUBE = "shape=cube;boundedLbl=1;backgroundOutline=1;" + NODE
    COMPONENT = "shape=component;align=center;spacingLeft=36;" + NODE
    RPROMOTER = (
        "shape=mxgraph.arrows2.bendArrow;dy=15;dx=38;notch=0;arrowHead=55;rounded=0;shadow=0;dashed=0;align=center;"
        + NODE
    )
    LPROMOTER = "flipH=1;" + RPROMOTER
    CDS = (
        "shape=mxgraph.arrows2.arrow;dy=0;dx=10;notch=0;shadow=0;dashed=0;align=center;"
        + NODE
    )
    RARROW = (
        "shape=mxgraph.arrows2.arrow;dy=0.6;dx=40;align=center;labelPosition=center;notch=0;strokeWidth=2;"
        "verticalLabelPosition=middle;" + NODE
    )
    LARROW = "flipH=1;" + RARROW
    IMAGE = (
        "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;"
        "imageAspect=0;image={image};" + NODE
    )

    @staticmethod
    def get_for_shape(dot_shape: str | None) -> "Styles":
        if dot_shape is None:
            return Styles.ELLIPSE
        if dot_shape.startswith("M") and dot_shape[1:] in _shape_to_style:
            return _shape_to_style[dot_shape[1:]]
        if dot_shape in _shape_to_style:
            return _shape_to_style[dot_shape]
        return Styles.NODE

    def format(self, **values) -> str:  # noqa: ANN003
        return self.value.format(**values)


_shape_to_style: dict[str, "Styles"] = {
    Shape.BOX: Styles.NODE,
    Shape.BOX_3D: Styles.CUBE,
    Shape.CDS: Styles.CDS,
    Shape.CIRCLE: Styles.CIRCLE,
    Shape.COMPONENT: Styles.COMPONENT,
    Shape.CYLINDER: Styles.CYLINDER,
    Shape.DIAMOND: Styles.DIAMOND,
    Shape.DOUBLE_CIRCLE: Styles.DOUBLE_CIRCLE,
    Shape.DOUBLE_OCTAGON: Styles.DOUBLE_OCTAGON,
    Shape.EGG: Styles.EGG,
    Shape.ELLIPSE: Styles.ELLIPSE,
    Shape.FOLDER: Styles.FOLDER,
    Shape.HEXAGON: Styles.HEXAGON,
    Shape.HOUSE: Styles.HOUSE,
    Shape.IMAGE: Styles.IMAGE,
    Shape.INV_HOUSE: Styles.INV_HOUSE,
    Shape.INV_TRAPEZIUM: Styles.INV_TRAPEZOID,
    Shape.INV_TRIANGLE: Styles.INV_TRIANGLE,
    Shape.LARROW: Styles.LARROW,
    Shape.LPROMOTER: Styles.LPROMOTER,
    Shape.NOTE: Styles.NOTE,
    Shape.OCTAGON: Styles.OCTAGON,
    Shape.OVAL: Styles.ELLIPSE,
    Shape.PARALLELOGRAM: Styles.PARALLELOGRAM,
    Shape.PENTAGON: Styles.PENTAGON,
    Shape.PLAIN: Styles.LINE,
    Shape.POLYGON: Styles.HEXAGON,
    Shape.PROMOTER: Styles.RPROMOTER,
    Shape.RARROW: Styles.RARROW,
    Shape.RECT: Styles.NODE,
    Shape.RECTANGLE: Styles.NODE,
    Shape.RPROMOTER: Styles.RPROMOTER,
    Shape.SQUARE: Styles.SQUARE,
    Shape.STAR: Styles.STAR,
    Shape.TAB: Styles.TAB,
    Shape.TRAPEZIUM: Styles.TRAPEZOID,
    Shape.TRIANGLE: Styles.TRIANGLE,
    Shape.UNDERLINE: Styles.UNDERLINE,
}
