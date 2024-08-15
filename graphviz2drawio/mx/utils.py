def adjust_color_opacity(hex_color: str, opacity: float) -> str:
    """Adjust the opacity of a hex color as if it were on a white background."""
    # Remove the '#' if present
    hex_color = hex_color.lstrip("#")

    # Convert hex to RGB
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Apply opacity over white background
    r = int(r * opacity + 255 * (1 - opacity))
    g = int(g * opacity + 255 * (1 - opacity))
    b = int(b * opacity + 255 * (1 - opacity))

    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"
