import cv2
import os
import abc
import time


# TODO give the source a name
# TODO file sequence reader?


class BaseReader(metaclass=abc.ABCMeta):
    """Base class for reading from video sources."""

    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.source = source

        if not self.cap.isOpened():
            del self
            raise IOError('Could not open specified source')

    @abc.abstractproperty
    def resolution(self):
        pass

    def __bool__(self):
        return self.cap.isOpened

    def __del__(self):
        """Release the video file."""
        if self.cap:
            self.cap.release()

    @abc.abstractmethod
    def frames(self):
        pass


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

        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.__native_resolution = (width, height)
        self.__resolution = self.__native_resolution

    def __repr__(self):
        return "VideoReader(%s)" % self.source

    @property
    def resolution(self):
        return self.__resolution

    @resolution.setter
    def resolution(self, new_resolution):
        self.__resolution = new_resolution

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
            if self.__resolution == self.__native_resolution:
                yield frame
            else:
                # Resize the frame
                # TODO option to preserve aspect
                yield cv2.resize(frame, self.__resolution)
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

        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.__resolution = (width, height)

    def __repr__(self):
        return "CameraReader(%s)" % self.source

    @property
    def resolution(self):
        return self.__resolution

    @resolution.setter
    def resolution(self, new_resolution):
        (width, height) = new_resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Check the resolution
        if not (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) == width and
                        self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) == height):
            raise ValueError("Unsupported camera resolution")
        else:
            self.__resolution = (width, height)

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


if __name__ == '__main__':
    import jowr

    c = VideoReader('..\\data\\sun.mp4')
    c.resolution = (100, 300)
    jowr.play(c.frames(1, 200))
