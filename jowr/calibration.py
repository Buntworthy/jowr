import os

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

        self.calibration = {}
        self.object_points = []  # 3d point in real world space
        self.img_points = []  # 2d points in image plane.

        self.chequer_size = chequer_size
        self.chequer_scale = chequer_scale

        self.chequer_points = self.generate_chequer_points(self.chequer_size,
                                                           self.chequer_scale)

    def calibrate(self, cam, save_name=''):
        # Arrays to store object points and image points from all the images.
        # TODO check if this is a reader, or a zip file
        if cam:
            # Take some images with the camera
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
            #TODO check we have some points
            self.calculate_calibration(cam.resolution)
            print('Camera matrix:')
            print(self.calibration['A'])
            print('Distortion coefficients')
            print(self.calibration['dist'])

    def save(self, filename):
        with open(filename, 'wb') as cal_file:
            pickle.dump(self.calibration, cal_file)

    # TODO some sort of validation
    def load(self, filename):
        with open(filename, 'rb') as cal_file:
            self.calibration = pickle.load(cal_file)

    def process(self, frame, save_name):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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
            modified_frame = cv2.drawChessboardCorners(frame,
                                                       (self.chequer_size[0],
                                                        self.chequer_size[1]),
                                                       corners, ret)
            jowr.show(modified_frame,
                      window_name='Detected_corners',
                      wait_time=500)

            if save_name:
                with zipfile.ZipFile(save_name, 'a') as cal_file:
                    # Make the filename
                    datestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                    temp_filename = datestr + '_calibration.png'
                    # Write image
                    cv2.imwrite(temp_filename, frame)
                    # Add to zip
                    cal_file.write(temp_filename)
                    # Delete the temporary file
                    os.remove(temp_filename)

    def calculate_calibration(self, resolution):

        (self.calibration['error'],
         self.calibration['A'],
         self.calibration['dist'],
         self.calibration['rvecs'],
         self.calibration['tvecs']) = cv2.calibrateCamera(self.object_points,
                                                          self.img_points,
                                                          resolution,
                                                          None, None)

    @staticmethod
    def generate_chequer_points(chequer_size, chequer_scale):
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
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
    c.save('test_cal.p')