import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import numpy as np
import pytest


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


def test_cal_from_zip():
    expected_cal = None
    zip_filename = 'test\\data\\saved_cal.zip'

    calibrator = jowr.Calibrator()
    calibration = calibrator.calibrate(zip_filename)
    assert (calibration == expected_cal)


def test_cal_from_folder():
    expected_cal = None
    foldername = 'test\\data\\example_cal'

    calibrator = jowr.Calibrator()
    calibration = calibrator.calibrate(foldername)
    assert (calibration == expected_cal)


def test_save_load():
    expected_cal = None
    cal_filename = 'filename.p'

    calibrator = jowr.Calibrator()
    calibration = calibrator.load(cal_filename)
    assert(calibration == expected_cal)


def test_bad_images():
    bad_folder = 'test\\data\\bad_cal'

    calibrator = jowr.Calibrator()
    with pytest.raises(IOError):
        calibrator.calibrate(bad_folder)


def test_no_images():
    no_image_folder = 'test\\data\\empty'

    calibrator = jowr.Calibrator()
    with pytest.raises(ValueError):
        calibrator.calibrate(no_image_folder)
