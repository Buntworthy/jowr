import sys, os
from zipfile import ZipFile

import cv2

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import numpy as np
import tempfile
from unittest.mock import patch, Mock
import pytest

# TODO use fixtures to provide test image and videos
# TODO test window closing in show

@patch('cv2.imshow')
@patch('cv2.waitKey')
def test_show(mock_waitKey, mock_imshow):
    mock_waitKey.return_value = ord('k')
    width = 500
    height = 300
    test_image = np.zeros((height, width))

    jowr.show(test_image)
    mock_imshow.assert_called_once_with(jowr.core.DEFAULT_WINDOW_NAME,
                                        test_image)
    mock = Mock()
    mock.callback()
    jowr.show(test_image, callbacks={'k': lambda: mock.callback})
    mock.callback.assert_any_call()


@patch('cv2.imshow')
@patch('cv2.waitKey')
def test_play(mock_waitKey, mock_imshow):
    video_file = 'data/videos/gray_sweep.avi'
    video = jowr.Video(video_file)
    with video.open_frames() as frames:
        jowr.play(frames)
    mock_imshow.call_count == len(video)
    mock_waitKey.call_count == len(video)


def test_resolution():
    width = 500
    height = 300
    test_image = np.zeros((height, width))

    assert (jowr.resolution(test_image) == (width, height))
    with pytest.raises(TypeError):
        jowr.resolution('An image')


def test_channels():
    width = 500
    height = 300
    test_image_bw = np.zeros((height, width))
    test_image_colour = np.zeros((height, width, 3))
    test_non_array = 'image.jpg'
    test_wrong_rank = np.zeros((1,1,1,1))

    assert (jowr.channels(test_image_bw) == 1)
    assert (jowr.channels(test_image_colour) == 3)
    with pytest.raises(TypeError):
        jowr.channels(test_non_array)
    with pytest.raises(ValueError):
        jowr.channels(test_wrong_rank)


def test_find_images():
    folder = 'data/images'
    files = ('monkey_Luc_Viatour.jpg',
             'penguin_Gorfou_Sauteur.jpg')

    found_images = [os.path.split(this_file)[1] for this_file in
                    jowr.find_images(folder)]

    assert set(found_images) == set(files)


def test_scale():
    width = 500
    height = 300
    scale = 0.5
    test_image = np.zeros((height, width))

    scaled_image = jowr.scale(test_image, scale)

    im_shape = scaled_image.shape
    assert im_shape[0] == scale * height
    assert im_shape[1] == scale * width


def test_add_to_zip():
    width = 500
    height = 300
    test_image = np.ones((height, width))

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, 'tmp.zip')
        jowr.add_to_zip(test_image, tmp_file)

        with ZipFile(tmp_file) as tmp_zip:
            contents = tmp_zip.namelist()
            assert len(contents) == 1
            tmp_zip.extract(contents[0], path=tmp_dir)
            image = cv2.imread(os.path.join(tmp_dir, contents[0]))
            assert np.sum(image[:, :, 0]) == width * height
