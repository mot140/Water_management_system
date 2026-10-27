import cv2 as cv

def camera_starting(video_path):
    cap = cv.VideoCapture(video_path)
    