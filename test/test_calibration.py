import shutil
import sys, os
from zipfile import ZipFile

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import numpy as np
import pytest
import pickle


def test_generate_chequer_points():
    chequer_size = (2, 3)
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


def test_cal_from_zip_save_load():
    with open('data/example_cal/test_cal.p', 'rb') as f:
        expected_cal = pickle.load(f)
    zip_filename = 'data/example_cal/test.zip'

    calibrator = jowr.Calibrator()
    calibration = calibrator.calibrate(zip_filename)
    assert np.allclose(calibration['matrix'], expected_cal['matrix'])
    assert np.allclose(calibration['distortion'],
                       expected_cal['distortion'])

    # Test save/load
    save_cal = 'my_cal.p'
    calibrator.save(save_cal)
    loaded_calibration = calibrator.load(save_cal)
    assert np.allclose(loaded_calibration['matrix'], expected_cal['matrix'])
    assert np.allclose(loaded_calibration['distortion'],
                       expected_cal['distortion'])
    os.remove(save_cal)


def test_cal_from_folder():
    with open('data/example_cal/test_cal.p', 'rb') as f:
        expected_cal = pickle.load(f)
    zip_filename = 'data/example_cal/test.zip'
    folder_name = 'data/example_cal/extracted'

    # Extract the images to a folder
    with ZipFile(zip_filename, 'r') as myzip:
        myzip.extractall(folder_name)

    calibrator = jowr.Calibrator()
    calibration = calibrator.calibrate(folder_name)

    # Clean up
    shutil.rmtree(folder_name)

    assert np.allclose(calibration['matrix'], expected_cal['matrix'])
    assert np.allclose(calibration['distortion'],
                       expected_cal['distortion'])


def test_bad_images():
    bad_folder = 'data/images'
    calibrator = jowr.Calibrator()
    with pytest.raises(IOError):
        calibrator.calibrate(bad_folder)


def test_no_images():
    no_image_folder = 'data/empty'
    calibrator = jowr.Calibrator()
    with pytest.raises(ValueError):
        calibrator.calibrate(no_image_folder)
