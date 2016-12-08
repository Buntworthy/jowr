Basics
======

Working with images
-------------------

To display an image using OpenCV's imshow method, use :py:meth:`~jowr.show`. By default this will display
the image in a window with a default name and then close the window when a key is pressed. By passing in optional
parameters to :py:meth:`~jowr.show`::

    jowr.show(frame,
                window_name='result',                       # Display in window named 'result'
                wait_time=100,                              # Wait for a keypress for 100 ms
                callbacks={ 'h': lambda: print('hello') },  # If key h is pressed, print hello
                esc_close=False,                            # Do not close window on Esc key
                auto_close=False)                           # Do not close window after waiting

Although this method provides a convenient way to show images, for more complex plotting matplotlib is recommended.

Reading video
-------------

The :py:class:`~jowr.VideoReader` provides a wrapper around OpenCV's VideoCapture object for reading from
video files. :py:class:`~jowr.VideoReader` implements some convenience methods to make the interaction
with frames from a video file a little simpler. For example providing generator access to frames::

    eaten_bananas = 0
    vid = jowr.VideoReader('monkey_eating_bananas.mp4')

    # Iterate from frame 100 to 200
    for frame in vid.frames(start=100, end=200):
        eaten_bananas += detect_bananas(frame)

    print("That monkey at %d bananas!" % eaten_bananas)

jowr also provides a convenience method for playing all the frames produced by a generator as a movie::

    def some_processing(frame):
        # Do something interesting
        return processed_frame

    vid = jowr.VideoReader('some_video.mp4')
    jowr.play([some_processing(frame) for frame in vid.frames()])

Reading other things
----------

jowr also provides readers for attached webcams (:py:class:`~jowr.CameraReader`) and folders of sequenctial images
 (:py:class:`~jowr.ImageSequenceReader`). TO help you make the right thing call :py:meth:`~jowr.make_reader` passing
in the video/camera/sequence source and it will return the object you require.