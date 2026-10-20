import cv2
import sys
import numpy as np
video_path = "input_video.mp4"
#動画を開く
cap = cv2.VideoCapture(video_path)
fgbg = cv2.createBackgroundSubtractorMOG2()
delay=1
window_name = 'frame'
ret,frame = cap.read()
masked_frame = np.zeros_like(frame)
x,y,w,h = 100,100,300,200
masked_frame[y:y+h, x:x+w] = frame[y:y+h, x:x+w]
if not cap.isOpened():
    print("※not open movie")
    sys.exit()


while True:
    ret,frame = cap.read()
    
    fgmask = fgbg.apply(frame)
    cv2.imshow('frame',masked_frame)
    cv2.imshow('fg_mask',fgmask)
    #if ret:
    #    cv2.imshow(window_name, frame)
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)
cap.release()
