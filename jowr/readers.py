import cv2
import os

class VideoReader(object):
    """Class to read video files.

    Wraps the existing VideoCapture class of OpenCV.

    Attributes:
        cap: OpenCV VideoCapture object.

    Raises:
        IOError: Specified video file was not found.
    """

    # TODO make superclass for both camera and video sources

    def __init__(self, filename):
        """Open a video file."""
        self.cap = None
        self.filename = ''

        if os.path.isfile(filename):
            self.cap = cv2.VideoCapture(filename)
            self.filename = filename
        else:
            del self
            raise IOError('File not found')

    def __repr__(self):
        return ("VideoReader(%s)", self.filename)

    def frames(self, start=0, end=-1):
        """Generator to return frames from the video.

        Args
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

    def __del__(self):
        """Release the video file."""
        if self.cap:
            self.cap.release()
