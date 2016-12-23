import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import jowr
import pytest
import random


# Test opening camera - open, not connected, closed
# Test file formats

def test_video_frames():
    n_frames = 255
    video_file = 'data/videos/gray_sweep.avi'

    video = jowr.Video(video_file)
    assert len(video) == n_frames

    with video.open_frames() as frames:
        assert sum(1 for _ in frames) == n_frames


def test_no_video():
    no_video = 'nothing.mp4'
    with pytest.raises(FileNotFoundError):
        jowr.Video(no_video)


def test_random_frame_access():
    # Each frame in the video is a solid gray with value = frame number
    video_file = 'data/videos/gray_sweep.avi'

    video = jowr.Video(video_file)
    with video.open_frames() as frames:
        indexes = list(range(255))
        random.shuffle(indexes)
        for frame1, index in [(frames[i], i) for i in indexes]:
            assert frame1[0, 0, 0] == index


def test_independant_frame_access():
    # Each frame in the video is a solid gray with value = frame number
    video_file = 'data/videos/gray_sweep.avi'

    video = jowr.Video(video_file)
    with video.open_frames() as frames:
        r1 = range(0, 100, 2)
        r2 = range(1, 100, 2)
        for frame1, i1, frame2, i2 in zip(frames[r1.start:r1.stop:r1.step],
                                          r1,
                                          frames[r2.start:r2.stop:r2.step],
                                          r2):
            assert frame1[0, 0, 0] == i1
            assert frame2[0, 0, 0] == i2
