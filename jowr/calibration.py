import os
import zipfile
import pickle
import glob

import jowr
import cv2
import numpy as np


# TODO method to write the calibration to plain text

class Calibrator(object):
    """ Class to help with camera calibration.

    Run calibration using a chequerboard pattern calibration can be performed
    on a jowr reader (typically a CameraReader).

    Examples:

        Calibrate an attached camera, save the raw image files, and save the
        calibration result:

        >>> calibrator = jowr.Calibrator()
        >>> calibration = calibrator.calibrate(jowr.CameraReader(0),
        ...                                    save_name='my_images.zip')
        >>> calibrator.save('my_calibration.p')

        Load an existing calibration from a file:

        >>> calibrator = jowr.Calibrator()
        >>> calibration = calibrator.load('my_calibration.p')

        Run calibration from existing image zip file

        >>> calibrator = jowr.Calibrator()
        >>> calibration = calibrator.calibrate('my_images.zip')

    """

    def __init__(self,
                 chequer_size=(9, 6),
                 chequer_scale=25.0):
        """ Create the Calibrator object.

        Optionally specify the chequerboard size to be used. Download one here:
        http://docs.opencv.org/2.4/_downloads/pattern.png

        Args:
            chequer_size (Tuple[int]): The (columns, rows) of the chequerboard
            chequer_scale (int): The size of a square in mm
        """

        # TODO show result option

        self.calibration = {}
        self.object_points = []  # 3d point in real world space
        self.img_points = []  # 2d points in image plane.
        self.resolution = None  # resolution of the images used for calibration
        self.showFrames = True # Display frames being processed

        self.chequer_size = chequer_size
        self.chequer_scale = chequer_scale

        self.chequer_points = self.generate_chequer_points(self.chequer_size,
                                                           self.chequer_scale)

    def calibrate(self, cam, save_name=''):
        """ Calibrate a camera, video, zipfile, or directory of images.

        Args:
            cam: Source for calibration, this could be a jowr.BaseReader, path
                to a zipfile, or a directory.
            save_name (Optional[str]): Path to zipfile to save images. If empty
                no images are saved.
        """
        # A camera/video
        if isinstance(cam, jowr.BaseReader):
            self.calibrate_reader(cam, save_name)
        # An existing zip file of images
        elif zipfile.is_zipfile(cam):
            self.calibrate_zip(cam)
        # An existing folder of images
        elif os.path.isdir(cam):
            self.calibrate_folder(cam)
        # I don't know what this is
        else:
            raise TypeError("Unknown input type, "
                            "not a camera, video, zipfile or directory.")

        return self.calibration

    def calibrate_zip(self, cam):
        """ Calibrate all the png files in a zip archive.

        Args:
            cam (str): Path to the zipfile.

        """
        with zipfile.ZipFile(cam, 'r') as zip_file:
            zip_members = [f.filename for f in zip_file.filelist]
            # TODO add other extension
            is_png = [this_file.endswith('.png')
                      for this_file in zip_members]

            # Check there are some png files
            if not any(is_png):
                raise TypeError("No png files found in zip")

            # Loop over files in zip file
            for zipinfo, filename, png in \
                    zip(zip_file.filelist, zip_members, is_png):
                if png:
                    # cv2's imread expect a file, so we extract
                    zip_file.extract(zipinfo)
                    image = cv2.imread(filename)
                    # TODO be careful here!
                    os.remove(filename)
                    self.check_resolution(image)
                    self.process(image, '')

            self.calculate_calibration()

    def calibrate_reader(self, cam, save_name):
        """ Calibrate images selected from a camera or video.

        Args:
            cam (jowr.BaseReader): Image source.
            save_name (str): Path to zipfile to save images.

        """
        print("Press s key to capture an image. Press Esc to finish.")
        self.resolution = cam.resolution
        for frame in cam.frames():
            # Detect corners for each image during acquisition
            stop = jowr.show(frame, 'Camera',
                             wait_time=1,
                             callbacks={
                                 # Process a frame on s key pressed
                                 's': lambda: self.process(frame,
                                                           save_name)
                             },
                             auto_close=False)
            if stop:
                break
        self.calculate_calibration()

    def calibrate_folder(self, folder):
        """ Calibrate all the png files in a directory.

        Args:
            folder (str): directory to search for images (not including
                subdirectories).

        """
        for filename in jowr.find_images(folder):
            image = cv2.imread(filename)
            self.check_resolution(image)
            self.process(image, '')
        self.calculate_calibration()

    def save(self, filename):
        """ Save the current calibration to a file.

        Args:
            filename (str): path to save file.
        """
        # I'd like to use json to make it readable, but numpy arrays are awkward
        with open(filename, 'wb') as cal_file:
            pickle.dump(self.calibration, cal_file)

    # TODO some sort of validation
    def load(self, filename):
        """ Load a calibration from file.

        Args:
            filename (str): path to the previously pickled file.
        """
        with open(filename, 'rb') as cal_file:
            self.calibration = pickle.load(cal_file)
            if not isinstance(self.calibration, dict):
                raise TypeError("Loaded calibation is not a dictionary")
            elif not all([this_key in self.calibration.keys()
                          for this_key in ('error', 'matrix', 'distortion')]):
                raise TypeError("Calibration dictionary "
                                "doesn't have all the information I need")
            return self.calibration

    def process(self, frame, save_name):
        """ Find the chessboard corners in a single image.

        Args:
            frame Colour image with channel ordering BGR
             save_name Name of zip file to save image to
        """
        if jowr.channels(frame) is 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()

        # Find the chess board corners
        ret, corners = \
            cv2.findChessboardCorners(gray,
                                      (self.chequer_size[0],
                                       self.chequer_size[1]),
                                      cv2.CALIB_CB_FAST_CHECK)

        # If found, add object points, image points (after refining them)
        if not ret:
            print("Failed to find chequerboard points")
        else:
            self.object_points.append(self.chequer_points)
            self.img_points.append(corners)

            # Draw and display the corners
            modified_frame = frame.copy()
            modified_frame = cv2.drawChessboardCorners(modified_frame,
                                                       (self.chequer_size[0],
                                                        self.chequer_size[1]),
                                                       corners, ret)
            if self.showFrames:
                jowr.show(modified_frame,
                          window_name='Detected_corners',
                          wait_time=500)

            if save_name:
                # Add to the zip file
                jowr.add_to_zip(frame, save_name)
        return ret

    def check_resolution(self, image):
        resolution = jowr.resolution(image)
        if self.resolution and self.resolution != resolution:
            raise IOError(
                "Calibration images are different resolutions.")
        self.resolution = resolution

    def calculate_calibration(self):

        # Check we have everything we need
        if not self.object_points:
            raise ValueError("No chessboard points to work with.")
        if not self.img_points:
            raise ValueError("No image points to work with.")
        if not self.resolution:
            raise ValueError("Image resolution not detected")

        # Could use a namedtuple, but then a simple dict is a bit more
        # convenient for external use?
        (self.calibration['error'],
         self.calibration['matrix'],
         self.calibration['distortion'],
         _, _) = cv2.calibrateCamera(self.object_points,
                                     self.img_points,
                                     self.resolution,
                                     None, None)
        self.calibration['resolution'] = self.resolution

    def print_to_file(self, filename):
        # if not self.calibration:
        # TODO raise an error
        with open(filename, 'w') as cal_file:
            for key, val in self.calibration.items():
                cal_file.write('{}:\n'.format(key))
                cal_file.write('{}\n'.format(val))

    @staticmethod
    def generate_chequer_points(chequer_size, chequer_scale):
        """Generate an array of corner point positions."""
        chequer_points = np.zeros((chequer_size[0] * chequer_size[1], 3),
                                  np.float32)
        chequer_points[:, :2] = np.mgrid[0:chequer_size[0],
                                0:chequer_size[1]].T.reshape(-1, 2)
        # adjust scale
        chequer_points *= chequer_scale
        return chequer_points


def undistort(frame, calibration):
    if not jowr.resolution(frame) == calibration['resolution']:
        raise ValueError("Resolution of image not equal to that of calibration")
    return cv2.undistort(frame,
                         calibration['matrix'],
                         calibration['distortion'])


if __name__ == '__main__':
    reader = jowr.CameraReader(0)

    c = Calibrator(chequer_scale=50)
    c.calibrate(reader, 'test.zip')
    c.save('test_cal.p')
    # c.calibrate('test.zip')
