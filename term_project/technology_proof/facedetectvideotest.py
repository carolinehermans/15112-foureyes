import numpy as np
import cv2

cascadePath='haarcascades/haarcascade_frontalface_alt.xml'
face_cascade=cv2.CascadeClassifier(cascadePath)
cap=cv2.VideoCapture(0)

def draw_rects(img, rects, color):
    for x, y, w, h in rects:
        cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)


dy,dx=0,0
r=100
i=0
while (True):
    ret,img=cap.read()
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if i%5==0:
        faces=face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
           
            roi_gray=gray[y:y+h, x:x+w]
            roi_color=img[y:y+h, x:x+w]
    #draw_rects(img,faces,(0,0,255))
    #draw_rects(img,faces,(0,0,255))
    i+=1
    #cv2.circle(img,(200,200),50,(0,0,255),10)
    cv2.imshow('img',img)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
