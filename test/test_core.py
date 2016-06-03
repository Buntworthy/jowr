import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import numpy as np


def test_resolution():
    width = 500
    height = 300
    test_image = np.zeros((height, width))
    assert (jowr.resolution(test_image) == (width, height))


def test_channels():
    width = 500
    height = 300
    test_image_bw = np.zeros((height, width))
    test_image_colour = np.zeros((height, width, 3))

    assert (jowr.channels(test_image_bw) == 1)
    assert (jowr.channels(test_image_colour) == 3)
