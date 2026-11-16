# -*- coding: utf-8 -*-

# Issue #2: transparent round_corner draws a dark ring on the curve.

from thumbor.ext.filters import _round_corner

WIDTH = 100
HEIGHT = 100
RADIUS = 30
COLOR = (200, 100, 50)


def test_transparent_round_corner_keeps_color_and_fades_alpha():
    pixel = bytes(COLOR) + bytes([255])
    data = bytes(bytearray(pixel * (WIDTH * HEIGHT)))

    result = _round_corner.apply(
        1, "RGBA", RADIUS, RADIUS, 255, 255, 255, WIDTH, HEIGHT, data, 1
    )

    pixels = [
        tuple(result[i : i + 4]) for i in range(0, len(result), 4)
    ]
    visible = [pix for pix in pixels if pix[3] > 0]
    partial = [pix for pix in pixels if 0 < pix[3] < 255]

    darkened = [pix for pix in visible if pix[:3] != COLOR]
    assert not darkened, (
        f"{len(darkened)} visible pixels lost their color, "
        f"for example {darkened[0]}"
    )
    assert partial, "no edge pixel is partly transparent"
