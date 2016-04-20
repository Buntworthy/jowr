Basics
======

Working with images
-------------------

To display an image using OpenCV's imshow method, use :py:method:`~jowr.core.show`. By default this will display
the image in a window with a default name and then close the window when a key is pressed. By passing in optional
parameters to :py:method:`~jowr.core.show`::

    image.show(frame,
                window_name='result',                       # Display in window named 'result'
                wait_time=100,                              # Wait for a keypress for 100 ms
                callbacks={ 'h': lambda: print('hello') },  # If key h is pressed, print hello
                esc_close=False,                            # Do not close window on Esc key
                auto_close=False)                           # Do not close window after waiting

Although this method provides a convenient way to show images, for more complex plotting matplotlib is recommended.

Reading video
-------------

The :py:class:`~jowr.readers.VideoReader` provides a wrapper around OpenCV's VideoCapture object for reading from
video files. :py:class:`~jowr.readers.VideoReader` implements some convenience methods to make the interaction
with frames from a video file a little simpler.