from enum import Enum


class Styles(Enum):
    NODE = "verticalAlign=top;align=left;overflow=fill;html=1;rounded=0;shadow=0;comic=0;labelBackgroundColor=none;strokeColor={stroke};strokeWidth=1;fillColor={fill};"
    EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=0.5;exitY=0;entryX={entry_x:.3g};entryY=1;jettySize=auto;orthogonalLoop=1;endArrow={end_arrow};dashed={dashed};endFill={end_fill};"
    TEXT = "margin:0px;text-align:{align};{margin};font-size:{size}px;font-family:{family};color:{color};"

    def format(self, **values):
        return self.value.format(**values)
