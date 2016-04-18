import cv2
import numpy as np
import jowr

# Shared stuff
filename = "C:\\Data\\prototype demo LQ.mp4"
start_frame = 100
end_frame = 150

# OpenCV
vid = cv2.VideoCapture(filename)
vid.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
ret, frame = vid.read()

while ret:
    ret, frame = vid.read()
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(30)
    frame_number = vid.get(cv2.CAP_PROP_POS_FRAMES)
    if frame_number > end_frame or key is 27:
        break

cv2.destroyAllWindows()


# jowr
vid = jowr.VideoReader(filename)
for frame in vid.frames(start_frame,end_frame):
    frame.show(wait_time=30, auto_close=False)
