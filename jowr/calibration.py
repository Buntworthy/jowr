import os

import time

import jowr
import cv2
import numpy as np
import zipfile
import pickle
import datetime


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
                 chequer_scale=25):
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

        self.chequer_size = chequer_size
        self.chequer_scale = chequer_scale

        self.chequer_points = self.generate_chequer_points(self.chequer_size,
                                                           self.chequer_scale)

    def calibrate(self, cam, save_name=''):
        # A camera/video
        if isinstance(cam, jowr.BaseReader):
            self.calibrate_reader(cam, save_name)

        # An existing zip file of images
        elif zipfile.is_zipfile(cam):
            self.calibrate_zip(cam)

        # An existing folder of images
        elif os.path.isdir(cam):
            # TODO read from image file
            # Loop over files in folder
            pass
        # I don't know what this is
        else:
            raise TypeError("Unknown input type, "
                            "not a camera, video, or images.")

        print('Camera matrix:')
        print(self.calibration['A'])
        print('Distortion coefficients')
        print(self.calibration['dist'])

    def calibrate_zip(self, cam):
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
                    # Check the resolution
                    resolution = jowr.resolution(image)
                    if self.resolution and self.resolution != resolution:
                            raise IOError(
                                "Calibration images are different resolutions.")
                    self.process(image, '')

            self.calculate_calibration()

    def calibrate_reader(self, cam, save_name):
        # Take some images with the camera
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

    def save(self, filename):
        with open(filename, 'wb') as cal_file:
            pickle.dump(self.calibration, cal_file)

    # TODO some sort of validation
    def load(self, filename):
        with open(filename, 'rb') as cal_file:
            self.calibration = pickle.load(cal_file)

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
            jowr.show(modified_frame,
                      window_name='Detected_corners',
                      wait_time=500)

            if save_name:
                # Add to the zip file
                jowr.add_to_zip(frame, save_name)

    def calculate_calibration(self):

        # Check we have everything we need
        if not self.object_points:
            raise ValueError("No chessboard points to work with.")
        if not self.img_points:
            raise ValueError("No image points to work with.")
        if not self.resolution:
            raise ValueError("Image resolution not detected")

        (self.calibration['error'],
         self.calibration['A'],
         self.calibration['dist'],
         self.calibration['rvecs'],
         self.calibration['tvecs']) = cv2.calibrateCamera(self.object_points,
                                                          self.img_points,
                                                          self.resolution,
                                                          None, None)

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


if __name__ == '__main__':
    c = Calibrator()
    c.calibrate(jowr.CameraReader(0), 'test.zip')
    # c.save('test_cal.p')
    # c.calibrate('test.zip')
