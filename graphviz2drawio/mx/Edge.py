from graphviz2drawio.models import DotAttr

from ..models.Rect import Rect
from . import MxConst
from .Curve import Curve
from .GraphObj import GraphObj
from .Styles import Styles
from .Text import Text


class Edge(GraphObj):
    """An edge connecting two nodes in the graph."""

    def __init__(
        self,
        sid: str,
        *,
        fr: str,
        to: str,
        is_directed: bool,
        curve: Curve | None,
        labels: list[Text],
    ) -> None:
        super().__init__(sid=sid, gid=f"{fr}->{to}")
        self.fr = fr
        self.to = to
        self.curve = curve
        self.line_style = None
        self.dir = DotAttr.FORWARD if is_directed else DotAttr.NONE
        self.arrowtail = None
        self.arrowhead = None
        self.labels = labels

    def get_edge_style(
        self,
        source_geo: Rect | None,
        target_geo: Rect | None,
    ) -> str:
        dashed = 1 if self.line_style == DotAttr.DASHED else 0

        end_arrow, end_fill = self._get_arrow_shape_and_fill(
            arrow=self.arrowhead,
            active_dirs={DotAttr.FORWARD, DotAttr.BOTH},
        )
        start_arrow, start_fill = self._get_arrow_shape_and_fill(
            self.arrowtail,
            active_dirs={DotAttr.BACK, DotAttr.BOTH},
        )

        if self.curve is not None:
            style = Styles.EDGE.format(
                dashed=dashed,
                end_arrow=end_arrow,
                end_fill=end_fill,
                start_arrow=start_arrow,
                start_fill=start_fill,
            ) + (MxConst.CURVED if self.curve.is_bezier else MxConst.SHARP)

            if source_geo is not None:
                exit_x, exit_y = source_geo.relative_location_along_perimeter(
                    self.curve.start,
                )
                style += f"exitX={exit_x:.4f};exitY={exit_y:.4f};"
            if target_geo is not None:
                entry_x, entry_y = target_geo.relative_location_along_perimeter(
                    self.curve.end,
                )
                style += f"entryX={entry_x:.4f};entryY={entry_y:.4f};"

            return style

        return Styles.EDGE.format(
            end_arrow=end_arrow,
            dashed=dashed,
            end_fill=end_fill,
            start_arrow=start_arrow,
            start_fill=start_fill,
        )

    def _get_arrow_shape_and_fill(
        self,
        arrow: str | None,
        active_dirs: set[str],
    ) -> tuple[str, int]:
        shape = MxConst.BLOCK if self.dir in active_dirs else MxConst.NONE
        fill = 1 if self.dir in active_dirs else 0

        if arrow is not None:
            if arrow == "none":
                shape = MxConst.NONE
                fill = 0
            else:
                if arrow[0] == DotAttr.NO_FILL:
                    fill = 0
                if arrow[1:] == DotAttr.DIAMOND:
                    shape = MxConst.DIAMOND

        return shape, fill

    def curve_start_end(self):
        if self.dir == DotAttr.BACK:
            return self.curve.end, self.curve.start
        return self.curve.start, self.curve.end

    @property
    def key_for_label(self) -> str:
        return f"{self.gid}-{self.curve}-{self.dir}"

    def __repr__(self) -> str:
        return (
            f"{self.fr}->{self.to}: "
            f"{self.labels}, {self.line_style}, {self.dir}, {self.arrowtail}"
        )

    def value_for_labels(self) -> str:
        text = ""
        for i, label in enumerate(self.labels):
            if i == 0:
                text += label.to_simple_value()
            else:
                text += f"<div>{label.to_simple_value()}</div>"
        return text
