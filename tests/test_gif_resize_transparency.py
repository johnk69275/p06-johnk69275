# -*- coding: utf-8 -*-

# Issue #3: a resized palette GIF loses its transparent background.

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

STICKER = abspath(
    join(dirname(__file__), "..", "course", "images", "sticker.gif")
)


def count_transparent(img):
    alpha = img.convert("RGBA").getchannel("A")

    return sum(1 for value in alpha.getdata() if value == 0)


def test_resized_palette_gif_keeps_transparent_pixels():
    with open(STICKER, "rb") as image_file:
        buffer = image_file.read()

    with Image.open(BytesIO(buffer)) as source:
        assert source.mode == "P"
        assert count_transparent(source) > 0, "source must be transparent"

    config = Config(
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
        ALLOW_ANIMATED_GIFS=False,
    )
    engine = Engine(Context(config=config))
    engine.load(buffer, ".gif")
    assert engine.original_mode == "P"

    engine.resize(240, 160)

    with Image.open(BytesIO(engine.read(".gif"))) as output:
        assert output.format == "GIF"
        transparent = count_transparent(output)
        assert "transparency" in output.info, (
            "output GIF has no transparency index, "
            f"{transparent} transparent pixels"
        )
        assert transparent > 0, "no transparent pixels in output GIF"
