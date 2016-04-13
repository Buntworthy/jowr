# Jowr - Justin's OpenCV Wrapper

## JCV
```python
vid = jcv.VideoReader(filename)
start_frame = 100
end_frame = 200

for frame in vid(start_frame,end_frame):
	frame.show()
```

## OpenCV

```python
vid = cv2.VideoCapture(filename)
start_frame = 100
end_frame = 200
self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
ret, frame = vid.read()

while ret:
  ret, frame = vid.read()
  cv2.imshow("frame", frame)
  cv2.waitKey(1)
  frame_number = vid.get(cv2.CAP_PROP_POS_FRAMES)
  if frame_number > end_frame:
    break
```


vid.resolution = (1920, 1080)

for frame in vid:
	blurred_frame = jcv.gaussian_blur(frame, sigma=10)
	blurred_frame.show()

vid = jcv.VideoReader(filename, resolution=(240, 480))
vid_writer = jcv.VideoWriter("out.mp4")
for frame in vid:
	edge_image = jcv.canny(frame)
	vid_writer.write(edge_image)
