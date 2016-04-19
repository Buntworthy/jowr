.. jowr documentation master file, created by
   sphinx-quickstart on Fri Apr 15 16:44:46 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jowr's documentation!
================================

*jowr = Justin's OpenCV Wrapper*

jowr is a bunch of helper functions which make using OpenCV python interface a bit friendlier.

An example
----------

Set up some variables::

   filename = "some_video.mp4"
   start_frame = 100
   end_frame = 150
   frame_time = 30

Sequentially display some frames from the video with OpenCV's native Python bindings::

   # OpenCV only
   vid = cv2.VideoCapture(filename)
   vid.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
   ret, frame = vid.read()

   while ret:
       ret, frame = vid.read()
       cv2.imshow("Frame", frame)
       key = cv2.waitKey(frame_time)
       frame_number = vid.get(cv2.CAP_PROP_POS_FRAMES)
       if frame_number > end_frame or key is 27:
           break

   cv2.destroyAllWindows()

Do the same with jowr's help::

   # jowr
   vid = jowr.VideoReader(filename)
   for frame in vid(start_frame,end_frame):
      frame.show(wait_time=frame_time, auto_close=False)

Contents:

.. toctree::
   :maxdepth: 2

   intro
   basics

.. automodule:: jowr.data
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

