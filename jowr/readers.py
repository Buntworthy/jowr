import cv2
import os

import time

# TODO make boolean return false if camera not open
# TODO give the source a name
# TODO resolution field
# TODO file sequence reader?


class BaseReader(object):
    """Base class for reading from video sources."""

    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.source = source

        if not self.cap.isOpened():
            del self
            raise IOError('Could not open specified source')

    def __del__(self):
        """Release the video file."""
        if self.cap:
            self.cap.release()


class VideoReader(BaseReader):
    """Class to read video files.

    Wraps the existing VideoCapture class of OpenCV.

    Attributes:
        cap: OpenCV VideoCapture object.

    Raises:
        IOError: Specified video file was not found.
    """

    def __init__(self, source):
        """Open a video file."""
        super(VideoReader, self).__init__(source)

        # Check the file exists
        if not os.path.isfile(source):
            del self
            raise IOError('File not found')

    def __repr__(self):
        return "VideoReader(%s)" % self.source

    def frames(self, start=0, end=-1):
        """Generator to return frames from the video.

        Args:
            start: 0-index start frame (default 0).
            end: 0-index end frame, -1 for end of video (default -1).

        """

        # Set the starting frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        # Read the first frame
        ret, frame = self.cap.read()
        while ret:
            yield frame
            # Check if we have reached the last frame
            if end > 0:
                frame_number = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                if frame_number > end:
                    break
            ret, frame = self.cap.read()


class CameraReader(BaseReader):
    """Class to read from an attached Camera.

    Wraps the existing VideoCapture class of OpenCV.

    Attributes:
        cap: OpenCV VideoCapture object.

    """
    def __init__(self, source):
        super(CameraReader, self).__init__(source)
        ## temp
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.resolution = (1920, 1080)

    def __repr__(self):
        return "CameraReader(%s)" % self.source

    def frames(self, duration=-1):
        """Generator to return frames from the video.

        Args:
            duration: length of video in seconds to capture (default -1).

        """

        start_time = time.time()
        # Read the first frame
        ret, frame = self.cap.read()
        while ret:
            yield frame
            # Check if we have reached the last frame
            if 0 < duration < (time.time() - start_time):
                    break
            ret, frame = self.cap.read()
