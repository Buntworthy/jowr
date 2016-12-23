import cv2
import os
import zipfile
import datetime
import numpy as np
import glob

# Constants
DEFAULT_WINDOW_NAME = "default"
ESC_CODE = 27
"""Key code for Esc """


def show(frame, window_name=DEFAULT_WINDOW_NAME, wait_time=0, callbacks=None,
         esc_close=True, auto_close=True):
    """Show the image. Return False if quit key pressed."""
    # Could have another method e.g. show and close, or flash?
    # TODO deal with different data types
    # TODO seems natural for someone to pass in a generator of frames?
    cv2.imshow(window_name, frame)
    key_code = cv2.waitKey(wait_time)
    if callbacks and key_code>0 and (chr(key_code) in callbacks):
        callbacks[chr(key_code)]()

    # Close the window on Esc
    if esc_close and (key_code is ESC_CODE):
        cv2.destroyWindow(window_name)
        return True

    # Close the window on timeout
    if auto_close and (key_code is -1):
        cv2.destroyWindow(window_name)


def play(frame_generator):
    """Convenience method to play all the frames in a iterable."""
    for frame in frame_generator:
        stop = show(frame, wait_time=30, auto_close=False)
        if stop:
            break
    close()


def close(window_name=DEFAULT_WINDOW_NAME):
    cv2.destroyWindow(window_name)


def add_to_zip(image, filename):
    """ Add an image to zip file with datestamp."""
    # TODO use a temporary directory
    with zipfile.ZipFile(filename, 'a') as zip_file:
        # Make the filename
        temp_filename = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')\
                        + ".png"
        # Write image
        cv2.imwrite(temp_filename, image)
        # Add to zip
        zip_file.write(temp_filename)
        # Delete the temporary file
        os.remove(temp_filename)


def resolution(image):
    """Return the image resolution as a tuple (width, height)"""
    if not isinstance(image, np.ndarray):
        raise TypeError("Image is not a Numpy array.")
    im_shape = image.shape
    # TODO named tuple
    width = im_shape[1]
    height = im_shape[0]
    return width, height


def channels(image):
    """Return the number of channels in an image"""
    if not isinstance(image, np.ndarray):
        raise TypeError("Image is not a Numpy array.")
    im_shape = image.shape
    if len(im_shape) is 2:
        return 1
    elif len(im_shape) is 3:
        return im_shape[2]
    else:
        raise ValueError("Array rank is not 2 or 3.")


def find_images(folder):
    """Find all image types in a folder."""
    image_types = ('.tiff', '.tif', '.png', 'jpg', 'jpeg', 'bmp')
    images = []
    for image_type in image_types:
        images.extend(glob.glob(os.path.join(folder, '*' + image_type)))
    return images

def scale(image, scale):
    return cv2.resize(image, None, fx=scale, fy=scale)