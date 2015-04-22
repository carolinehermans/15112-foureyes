import numpy as np
import cv2

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml')
eye_cascade=cv2.CascadeClassifier("haarcascades/haarcascade_eye.xml")

img = cv2.imread('aj.jpg')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faces = face_cascade.detectMultiScale(gray, 1.3, 5)


def draw_rects(img, rects, color):
    for x, y, w, h in rects:
        cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)


for (x,y,w,h) in faces:
    draw_rects(img,faces,(0,0,255))
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = img[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray)
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(roi_gray,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)



cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()