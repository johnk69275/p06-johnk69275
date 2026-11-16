# -*- coding: utf-8 -*-

# Issue #4: a size far from the source's aspect ratio gives an empty image.

from tests.fixtures import transformer_test_data as fixtures
from thumbor.threadpool import ThreadPool
from thumbor.transformer import Transformer

# (name, source size, requested size, fit_in)
CASES = [
    ("800x20 of a 16x16 image", (16, 16), (800, 20), False),
    ("fit-in 1x1 of a 940x2 image", (940, 2), (1, 1), True),
    ("fit-in 100x0 of a 940x2 image", (940, 2), (100, 0), True),
]


def run_transform(source, target, fit_in):
    test_data = fixtures.TestData(
        source_width=source[0],
        source_height=source[1],
        target_width=target[0],
        target_height=target[1],
        halign="center",
        valign="middle",
        focal_points=[],
        crop_left=None,
        crop_top=None,
        crop_right=None,
        crop_bottom=None,
        fit_in=fit_in,
    )
    ThreadPool.instance(0)  # the fixture's reset() needs _instance to exist
    context = test_data.to_context()
    Transformer(context).img_operation_worker()

    return test_data.engine.calls


def test_size_of_at_least_one_pixel_never_gives_an_empty_image():
    problems = []

    for name, source, target, fit_in in CASES:
        calls = run_transform(source, target, fit_in)

        for crop in calls["crop"]:
            width = crop["right"] - crop["left"]
            height = crop["bottom"] - crop["top"]
            if width < 1 or height < 1:
                problems.append(f"{name}: crop of {width}x{height}")

        for resize in calls["resize"]:
            if resize["width"] < 1 or resize["height"] < 1:
                problems.append(
                    f"{name}: resize to "
                    f"{resize['width']}x{resize['height']}"
                )

    assert not problems, "; ".join(problems)
