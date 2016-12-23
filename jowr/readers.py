from contextlib import contextmanager

import cv2
import os
import jowr


class Capture:
    """Base class for readers that interact with OpenCVs VideoCapture object.

    Args:
        source: Video source, either an index to webcam or path to video file

    Attributes:
        source
        next_frame_number (int): 0-based index of the next frame to be called
            using `next_frame`
        cap: OpenCV VideoCapture object, this should be accessed using the
            `open` context manager
        resolution (int, int): Native resolution of the source.
        frame_count (int): Total number of frames, 0 if a webcam

    """
    def __init__(self, source):
        self.source = source
        self.next_frame_number = 0
        self.cap = None

        with self.open():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.resolution = (width, height)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @contextmanager
    def open(self):
        """Opens the `VideoCapture` object and releases when done."""
        self.cap = cv2.VideoCapture(self.source)
        yield
        self.cap.release()

    @contextmanager
    def open_frames(self):
        """Returns a `Frames` object to iterate over the video."""
        with self.open():
            yield Frames(self)

    def next_frame(self):
        """Returns the next frame.

        Raises:
            IndexError: I   f the end of the source has been reached.

        """
        if not self.cap:
            raise jowr.CaptureNotOpenError
        exists, frame = self.cap.read()
        self.next_frame_number += 1
        if exists:
            return frame
        else:
            raise IndexError


class Video(Capture):
    """Class to read video files.

    jowr's `Video` class wraps the existing `VideoCapture` class of OpenCV when
    the specified source is a path to a video file.

    Args:
        source (str): Path to video file.

    Raises:
        IOError: Specified video file was not found.
    """

    def __init__(self, source):
        super().__init__(source)
        if not os.path.isfile(source):
            raise FileNotFoundError('File {}, not found'.format(source))

    def get_frame(self, index):
        """Get a frame from the Video.

        Args:
            index (int): 0-based index to the frame to get.

        Note:
            It is not recommended to call this method directly, frames from the
            webcam should be accessed using the `Frames` object returned by the
            `open_frames` method.

        """
        if not self.cap:
            raise jowr.CaptureNotOpenError
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        self.next_frame_number = index
        return self.next_frame()

    def __repr__(self):
        return 'Video({})'.format(self.source)

    def __len__(self):
        return self.frame_count


class Camera(Capture):
    """Class to read an attached webcam.

        jowr's `Video` class wraps the existing `VideoCapture` class of OpenCV when
        the specified source is a path to a video file.

        Args:
            source (str): Path to video file.

        Raises:
            IOError: Specified video file was not found.
        """
    def __init__(self, source):
        super().__init__(source)

    def get_frame(self, index):
        """Get a frame from the Webcam.

        Args:
            index (int): 0-based index to the frame to get.

        Raises:
            NotImplementedError: If the requested index does not match the
            next_frame_number.

        Note:
            This method only returns a frame if the requested index matches the
            `next_frame_number` of the `Camera`, i.e. duplicating the
            `next_frame` method.

        Note:
            It is not recommended to call this method directly, frames from the
            webcam should be accessed using the `Frames` object returned by the
            `open_frames` method.

        """
        if index == self.next_frame_number:
            return self.next_frame()
        else:
            raise NotImplementedError

    def __repr__(self):
        return 'Camera({})'.format(self.source)


class Frames:
    """Iterable over frames from a non-memory source i.e. a reader.

    Args:
        reader: `Video` or `Camera` object
        start (int): Start frame.
        stop (int): End frame.
        step (int): Increment between frames

    """

    def __init__(self, reader, start=0, stop=0, step=1):
        self.reader = reader
        self.stop = stop
        self.step = step
        self.next_frame_number = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_frame_number >= self.stop > 0:
            raise StopIteration

        try:
            if self.next_frame_number != self.reader.next_frame_number:
                frame = self.reader.get_frame(self.next_frame_number)
            else:
                frame = self.reader.next_frame()
        except IndexError:
            raise StopIteration
        self.next_frame_number += self.step
        return frame

    def __getitem__(self, item):
        if isinstance(item, int):
            if item < self.reader.frame_count:
                return self.reader.get_frame(item)
        elif isinstance(item, slice):
            return Frames(self.reader,
                          0 if item.start is None else item.start,
                          item.stop,
                          0 if item.step is None else item.step)
        else:
            raise TypeError
