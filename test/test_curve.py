from graphviz2drawio.mx.Curve import _line


def test_line():
    line = _line(complex(-5, 10), complex(-3, 4))
    assert line(0) == -5
    assert line(1) == -8
    assert line(2) == -11


def test_line_vertical():
    line = _line(complex(1, 10), complex(1, 4))
    assert line is None
