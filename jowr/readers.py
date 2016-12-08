from contextlib import contextmanager

import cv2
import os
import jowr


class Capture:
    def __init__(self, source):
        self.source = source
        self.next_frame_number = 0
        self.cap = None

    @contextmanager
    def open(self):
        self.cap = cv2.VideoCapture(self.source)
        yield
        self.cap.release()

    @contextmanager
    def open_frames(self):
        with self.open():
            yield Frames(self)  # an iterable

    def next_frame(self):
        exists, frame = self.cap.read()
        self.next_frame_number += 1
        if exists:
            return frame
        else:
            raise IndexError


class Video(Capture):
    """Class to read video files.

    Wraps the existing VideoCapture class of OpenCV.

    Attributes:
        cap: OpenCV VideoCapture object.

    Raises:
        IOError: Specified video file was not found.
    """

    def __init__(self, source):
        super().__init__(source)
        # Check the file exists
        if not os.path.isfile(source):
            raise FileNotFoundError('File {}, not found'.format(source))

        with self.open():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.resolution = (width, height)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # TODO property
    def get_frame(self, index):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        self.next_frame_number = index
        return self.next_frame()

    def __repr__(self):
        return 'Video({})'.format(self.source)

    def __len__(self):
        return self.frame_count


class Camera(Capture):
    def __init__(self, source):
        super().__init__(source)

        with self.open():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.resolution = (width, height)

    def get_frame(self, index):
        if index == self.next_frame_number:
            return self.next_frame()
        else:
            raise NotImplementedError

    def __repr__(self):
        return 'Camera({})'.format(self.source)

        # @resolution.setter
        # def resolution(self, new_resolution):
        #     (width, height) = new_resolution
        #     self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        #     self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        #
        #     # Check the resolution
        #     if not (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) == width and
        #                     self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) == height):
        #         raise ValueError("Unsupported camera resolution")
        #     else:
        #         self.__resolution = (width, height)
        #


class ImageSequenceReader():
    def __init__(self, source):
        # check that the path exists and has images
        self.path = source
        # make a list of image files in the path
        # TODO a more robust way of parsing image sequences
        self.images = jowr.find_images(self.path)
        self.images.sort()

    def frames(self, start=0, end=-1):
        for image_path in self.images[start:end]:
            yield cv2.imread(image_path)


class Frames:
    """Iterable over frames from a non memory source i.e. a reader

    with video.open_frames() as frames:
        my_frames = list(frames)
        for frame in frames[2:40:2]:
            process(frame)

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

# def make_reader(source):
#     """Helper function to create the appropriate reader from the source"""
#     # If it's a video file make a VideoReader
#     if source.endswith(video_extensions):
#         return VideoReader(source)
#     # If it's a integer make a CamReader
#     elif isinstance(source, int):
#         return CameraReader(source)
#     # If it's a path make a ImageSequenceReader
#     elif os.path.isdir(source):
#         return ImageSequenceReader(source)
#     else:
#         raise TypeError('Unrecognised source type')
