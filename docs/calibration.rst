Calibration
===========

Camera calibration is a really common thing to want to do when thinking about
computer vision applications: distortion correction, structure from motion,
stereo camera rigs etc. OpenCV provides everything you need to calibrate your
camera, and jowr wraps that all up into the friendly
:py:class:`~jowr.Calibrator` class.

Calibrating your camera
-----------------------

First step, make yourself a calibration pattern. You can download one from the
`OpenCV website <http://docs.opencv.org/2.4/_downloads/pattern.png>`_.

Next create an instance of the Calibrator object::

    calibrator = jowr.Calibrator()

if you've printed off the pattern linked above, the default chequer_size, and
chequer_scale will hopefully be ok, if not pass them in as arguments::

    calibrator = jowr.Calibrator(chequer_size=(8, 8), chequer_scale=50)

Now calibrate your webcam::

    calibration = calibrator.calibrate(jowr.CameraReader(0))

Here we pass in a :py:class:`~jowr.CameraReader` instance as the calibration
image source. The camera view will be displayed on screen, hold up the
calibration pattern and press the `s` key to capture a frame and detect the
corners. Do this a bunch of times a different angles, then press `Esc` to
finish and calculate the calibration.

Other options
-------------

Image sources
^^^^^^^^^^^^^

The Calibrator will accept any :py:class:`~jowr.BaseReader` as an image source
for calibration, so for example you could pass a :py:class:`~jowr.VideoReader`,
but you still need to press *s* to capture frames.

Saving data
^^^^^^^^^^^

To save the calibration to file, simply call :py:meth:`~jowr.Calibrator.save` to
pickle the calibration to a file, this can then later be loaded using the
Calibrator. When calibration from Camera or Video image source, pass in the
optional argument `save_name` when calling `calibrate` to save all the images
to a zip file `save_name.zip`::

    # Calibrate a camera and save images
    calibrator.calibrate(jowr.CameraReader(0), save_name='my_images.zip')
    # Save the calibration file
    calibrator.save('calibration_file.p')
    #
    # Some time later...
    #
    # Load the calibratione file again
    calibrator.load('calibration_file.p')
