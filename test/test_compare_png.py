from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from PIL import Image


def _load_compare_png() -> object:
    path = Path(__file__).resolve().parents[1] / "scripts" / "compare_png.py"
    spec = importlib.util.spec_from_file_location("compare_png", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPARE_PNG = _load_compare_png()


def test_pillow_decompression_bomb_limit_is_finite() -> None:
    assert Image.MAX_IMAGE_PIXELS == COMPARE_PNG.MAX_IMAGE_PIXELS
    assert isinstance(COMPARE_PNG.MAX_IMAGE_PIXELS, int)


def test_count_mismatches_detects_tiny_channel_difference() -> None:
    expected = Image.new("RGBA", (1, 1), (0, 0, 0, 255))
    actual = Image.new("RGBA", (1, 1), (0, 0, 1, 255))

    assert COMPARE_PNG.count_mismatches(expected, expected) == 0
    assert COMPARE_PNG.count_mismatches(expected, actual) == 1


def test_write_diff_highlights_tiny_channel_difference(tmp_path) -> None:
    expected = Image.new("RGBA", (1, 1), (0, 0, 0, 255))
    actual = Image.new("RGBA", (1, 1), (0, 0, 1, 255))
    actual_path = tmp_path / "actual.png"
    diff_path = tmp_path / "diffs" / "actual_diff.png"
    actual.save(actual_path)

    written = COMPARE_PNG.write_diff(expected, actual, actual_path, diff_path)

    assert written == diff_path.resolve()
    with Image.open(written) as diff:
        assert diff.getpixel((0, 0)) == (255, 0, 255, 255)


def test_write_diff_rejects_path_outside_actual_image_directory(tmp_path) -> None:
    expected = Image.new("RGBA", (1, 1), (0, 0, 0, 255))
    actual = Image.new("RGBA", (1, 1), (0, 0, 1, 255))
    actual_path = tmp_path / "actual.png"
    diff_path = tmp_path.parent / f"{tmp_path.name}-outside" / "actual_diff.png"
    actual.save(actual_path)

    with pytest.raises(ValueError, match="Refusing to write diff"):
        COMPARE_PNG.write_diff(expected, actual, actual_path, diff_path)

    assert not diff_path.exists()
