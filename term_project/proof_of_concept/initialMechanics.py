import numpy as np
import cv2
from math import *

"""As of April 4:
Space: take picture
R: retake picture
Q: quit
"""
#used to store stuff
class Face(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
class Dot(object): #class for dots for initial screen
    def __init__(self,cx,cy):
        self.cx=cx
        self.cy=cy
        self.r=6
    def draw(self,img):
        color=(255,0,0)
        cv2.rectangle(img,(self.cx-self.r,self.cy-self.r),
            (self.cx+self.r,self.cy+self.r),color,2)
    def clickInDot(self,x,y):
        if x>self.cx-r and x<self.cx+r and y>self.cy-r and y<self.cy+r:
            return True
        return False
    def connect(self,other,img,face):
        color=(255,0,0)
        cv2.line(img,(self.cx,self.cy),(other.cx,other.cy),color,1)
def faceDetect(face):#gets the bounding of the face and returns it
    face_cascade =(
        cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml'))
    gray = cv2.cvtColor(face.img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    try:
        (x,y,w,h)=faces[0]
    except:
        return "Error, no face detected!"
    return (x,y,w,h)
def makeDots(face): #creates the six dots that the user sees initially
    dotList=[]
    x,y,w,h=face.rectangle
    smallspc=w/10
    medspc=w/5
    bigspc=w/3
    dot1=Dot(cx=x+smallspc,cy=y+medspc)
    dot2=Dot(cx=x+medspc,cy=y+h/2+bigspc)
    dot3=Dot(cx=x+w/2,cy=y+h)
    dot4=Dot(cx=x+w-smallspc,cy=y+medspc)
    dot5=Dot(cx=x+w-medspc,cy=y+h/2+bigspc)
    dot6=Dot(cx=x+w/2,cy=y-medspc)
    return [dot1,dot2,dot3,dot4,dot5,dot6]
def drawDots(face): #draws all of the dots
    for dot in face.dots:
        dot.draw(face.img)
    cv2.imshow("hi",face.img)
def connectDots(face): #lines connecting all of the dots
    dots=face.dots
    dots[0].connect(dots[1],face.img,face)
    dots[1].connect(dots[2],face.img,face)
    dots[2].connect(dots[4],face.img,face)
    dots[4].connect(dots[3],face.img,face)
    dots[3].connect(dots[5],face.img,face)
    dots[5].connect(dots[0],face.img,face)
    cv2.imshow("hi",face.img)
#gets the video feed and waits for space bar to take photo
def getImg(face):
    pictureTaken=False
    cap=cv2.VideoCapture(0)
    while (pictureTaken==False):
        ret,img=cap.read()
        cv2.imshow("hi",img)
        if cv2.waitKey(1) & 0XFF == ord(" "): #pauses video feed
            return img
def restart():
    run()
def run():
    face=Face()
    face.img=getImg(face)
    #face.img=("aj.jpg")
    if type(faceDetect(face))!=str: #if it has detected a face
            face.rectangle=faceDetect(face)
    else: #if it hasn't detected a face, try again
        getImg(face)
        print faceDetect(face)
        return
    face.dots=makeDots(face)
    drawDots(face)
    connectDots(face)
    while True: #r to restart, q to quit
        if cv2.waitKey(1)&0XFF==ord("r"):
            restart()
        if cv2.waitKey(1)&0xFF==ord("q"):
            cv2.destroyAllWindows()          
run()








