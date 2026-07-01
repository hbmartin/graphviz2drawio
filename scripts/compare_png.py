from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops

Image.MAX_IMAGE_PIXELS = None

TRANSPARENT = (0, 0, 0, 0)
DIFF_HIGHLIGHT = (255, 0, 255, 160)
FULL_ALPHA = 255
RGBA_CHANNELS = 4


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


def count_mismatches(expected: Image.Image, actual: Image.Image) -> int:
    size = expanded_size(expected, actual)
    expected_canvas = rgba_canvas(expected, size)
    actual_canvas = rgba_canvas(actual, size)
    expected_bytes = expected_canvas.tobytes()
    actual_bytes = actual_canvas.tobytes()

    return sum(
        expected_bytes[index : index + RGBA_CHANNELS]
        != actual_bytes[index : index + RGBA_CHANNELS]
        for index in range(
            0,
            len(expected_bytes),
            RGBA_CHANNELS,
        )
    )


def write_diff(expected: Image.Image, actual: Image.Image, diff_path: Path) -> None:
    size = expanded_size(expected, actual)
    expected_canvas = rgba_canvas(expected, size)
    actual_canvas = rgba_canvas(actual, size)
    diff = ImageChops.difference(expected_canvas, actual_canvas)
    mask = diff.convert("L").point(lambda value: FULL_ALPHA if value else 0)
    highlight = Image.new("RGBA", size, DIFF_HIGHLIGHT)
    highlight.putalpha(mask)
    visual_diff = Image.alpha_composite(actual_canvas, highlight)

    diff_path.parent.mkdir(parents=True, exist_ok=True)
    visual_diff.save(diff_path)


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

    write_diff(expected, actual, args.diff)
    report_difference(
        args.expected,
        args.actual,
        args.diff,
        expected,
        actual,
        mismatches,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
