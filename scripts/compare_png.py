from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops

MAX_IMAGE_PIXELS = 200_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

TRANSPARENT = (0, 0, 0, 0)
DIFF_HIGHLIGHT = (255, 0, 255, 160)
FULL_ALPHA = 255


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two PNGs by decoded pixels and write a visual diff.",
    )
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("diff", type=Path)
    return parser.parse_args(argv)


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as image:
        image.load()
        return image.copy()


def expanded_size(expected: Image.Image, actual: Image.Image) -> tuple[int, int]:
    return max(expected.width, actual.width), max(expected.height, actual.height)


def rgba_canvas(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", size, TRANSPARENT)
    canvas.paste(image.convert("RGBA"), (0, 0))
    return canvas


def difference_mask(diff: Image.Image) -> Image.Image:
    r, g, b, a = diff.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), ImageChops.lighter(b, a))


def count_mismatches(expected: Image.Image, actual: Image.Image) -> int:
    size = expanded_size(expected, actual)
    expected_canvas = rgba_canvas(expected, size)
    actual_canvas = rgba_canvas(actual, size)
    mask = difference_mask(ImageChops.difference(expected_canvas, actual_canvas))
    if mask.getbbox() is None:
        return 0
    return (size[0] * size[1]) - mask.histogram()[0]


def validated_diff_path(diff_path: Path, actual_path: Path) -> Path:
    resolved_diff = diff_path.resolve()
    allowed_root = actual_path.resolve().parent
    if not (
        resolved_diff == allowed_root or resolved_diff.is_relative_to(allowed_root)
    ):
        msg = (
            "Refusing to write diff outside the actual image directory: "
            f"{resolved_diff}"
        )
        raise ValueError(msg)
    return resolved_diff


def write_diff(
    expected: Image.Image,
    actual: Image.Image,
    actual_path: Path,
    diff_path: Path,
) -> Path:
    size = expanded_size(expected, actual)
    expected_canvas = rgba_canvas(expected, size)
    actual_canvas = rgba_canvas(actual, size)
    diff = ImageChops.difference(expected_canvas, actual_canvas)
    mask = difference_mask(diff).point(lambda value: FULL_ALPHA if value else 0)
    highlight = Image.new("RGBA", size, DIFF_HIGHLIGHT)
    highlight.putalpha(mask)
    visual_diff = Image.alpha_composite(actual_canvas, highlight)

    safe_diff_path = validated_diff_path(diff_path, actual_path)
    safe_diff_path.parent.mkdir(parents=True, exist_ok=True)
    visual_diff.save(safe_diff_path)
    return safe_diff_path


def report_difference(
    expected_path: Path,
    actual_path: Path,
    diff_path: Path,
    expected: Image.Image,
    actual: Image.Image,
    mismatches: int,
) -> None:
    sys.stdout.write("PNG differences found\n")
    sys.stdout.write(f"Expected: {expected_path}\n")
    sys.stdout.write(f"Actual:   {actual_path}\n")
    sys.stdout.write(
        f"Size:     expected {expected.size}, actual {actual.size}\n",
    )
    sys.stdout.write(
        f"Mode:     expected {expected.mode}, actual {actual.mode}\n",
    )
    sys.stdout.write(f"Pixels:   {mismatches} mismatched\n")
    sys.stdout.write(f"Diff:     {diff_path}\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    expected = load_image(args.expected)
    actual = load_image(args.actual)
    mismatches = count_mismatches(expected, actual)

    if (
        expected.size == actual.size
        and expected.mode == actual.mode
        and mismatches == 0
    ):
        return 0

    diff_path = write_diff(expected, actual, args.actual, args.diff)
    report_difference(
        args.expected,
        args.actual,
        diff_path,
        expected,
        actual,
        mismatches,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
