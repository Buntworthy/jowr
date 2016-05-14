import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import numpy as np


def test_generate_chequer_points():

    chequer_size = (2,3)
    chequer_scale = 2
    generated_points = \
        jowr.Calibrator.generate_chequer_points(chequer_size, chequer_scale)

    expected_points = np.array([[0, 0, 0],
                                [2, 0, 0],
                                [0, 2, 0],
                                [2, 2, 0],
                                [0, 4, 0],
                                [2, 4, 0]])
    assert np.array_equal(generated_points, expected_points)