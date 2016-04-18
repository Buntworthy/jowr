import cv2

# Constants
DEFAULT_WINDOW_NAME = "default"
ESC_CODE = 27 # Key code for Esc


class VideoReader(object):

    def __init__(self, filename):
        """Open a video file."""

        self.cap = cv2.VideoCapture(filename)

    def frames(self, start=0, end=-1):
        """Generator to return frames from the video.

        Keyword arguments:
        start -- 0-index start frame (default 0)
        end -- 0-index end frame, -1 for end of video (default -1)
        """

        # Set the starting frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start)

        # Read the first frame
        ret, frame = self.cap.read()
        while ret:
            yield Image(frame)
            # Check if we have reached the last frame
            if end > 0:
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                if current_frame > end:
                    break
            ret, frame = self.cap.read()

    def __del__(self):
        """Release the video file."""

        self.cap.release()


class Image(object):

    def __init__(self, image_data):
        """Initialise Image object, store data, and extract properties"""
        self.image_data = image_data

        # Extract useful information
        data_shape = self.image_data.shape
        (self.rows, self.cols) = data_shape[0:2]
        if len(data_shape) is 3:
            self.channels = data_shape[2]
        else:
            self.channels = 1

    def show(self, window_name=DEFAULT_WINDOW_NAME, wait_time=0, callbacks=None, esc_close=True, auto_close=True):
        """Show the image. Return False if quit key pressed"""
        # Could have another method e.g. show and close, or flash?
        cv2.imshow(window_name, self.image_data)
        key_code = cv2.waitKey(wait_time)
        if callbacks and (key_code in callbacks):
            callbacks[key_code]()

        # Close the window on Esc
        if esc_close and (key_code is ESC_CODE):
            cv2.destroyWindow(window_name)

        # Close the window on timeout
        if auto_close and (key_code is -1):
            cv2.destroyWindow(window_name)
