from enum import Enum


class Styles(Enum):
    NODE = "verticalAlign=top;align=left;overflow=fill;fontSize=10;fontFamily=Helvetica;html=1;rounded=0;shadow=0;comic=0;labelBackgroundColor=none;strokeColor=#000000;strokeWidth=1;fillColor=#ffffff;"
    EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=0.5;exitY=0;entryX={entry_x:.3g};entryY=1;jettySize=auto;orthogonalLoop=1;endArrow={end_arrow};dashed={dashed};endFill={end_fill};"

    def format(self, **values):
        return self.value.format(**values)
