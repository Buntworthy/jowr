Welcome to jowr's documentation!
================================

jowr is a bunch of helper functions and utilities which make using the OpenCV
Python interface a bit friendlier.

Introduction
------------

jowr is a work in progress, currently it only really covers reading frames from
a video or camera source, and camera calibration.

Things to do next:

- Pipelines (Stringing together multiple image processing operations)
- Image transforms (Common transform helper functions)
- Feature extraction and matching
- Line detection (Plotting function, representation transforms, filtering)
- Edge detection (Automatic threshold guessing and parameter checking)

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
      jowr.show(frame, wait_time=frame_time, auto_close=False)

Contents:

.. toctree::
   :maxdepth: 2

   intro
   basics
   calibration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

