
import cv2
import numpy as np
import math


class Struct():
    pass

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def toDegrees(radTheta):
    return round(int(radTheta*57.2))

def drawGlasses(frame):
    scale=data.glassesScale
    theta=toDegrees(data.glassesTheta)

    glasses=cv2.imread("glassespics/heart.png",-1)
    glasses=cv2.resize(glasses,(0,0),fx=scale,fy=scale)
    w=glasses.shape[1]
    h=glasses.shape[0]
    glasses=-glasses
    for c in xrange(0,3):
        frameROI=frame[data.y:data.y+glasses.shape[0],data.x:data.x+glasses.shape[1],c] 
        try:
            aBigNumber=500
            newFrameROI=-glasses[:,:,c]*(glasses[:,:,2]/aBigNumber)+frameROI*(1.0 - glasses[:,:,c]/255.0)
            frame[data.y:data.y+glasses.shape[0],data.x:data.x+glasses.shape[1],c]=newFrameROI

        except: frame=frame
    return frame


def getTwoEyes(eyerects):
    biggestArea=0
    biggestEye=None
    secondBiggestArea=0
    secondBiggestEye=None
    if len(eyerects)==2: return eyerects
    for eye in eyerects:
        x1,y1,x2,y2=eye
        currArea=abs(x1-x2)*abs(y1-y2)
        if currArea>biggestArea:
            secondBiggestArea=biggestArea
            secondBiggestEye=biggestEye
            biggestArea=currArea
            biggestEye=eye
    return [biggestEye,secondBiggestEye]

def getAllEyeXsAndYs(frame):
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eyerects=detect(gray,data.eyeCascade)
    twoEyes=getTwoEyes(eyerects)
    return twoEyes

def getBiggestFace(facerects):
    if len(facerects)==1: return facerects[0]
    biggestArea=0
    biggestFace=None
    for face in facerects:
        x0,y0,x1,y1=face
        area=abs(x0-x1)*abs(y0-y1)
        if area>biggestArea:
            biggestFace=face
            biggestArea=area
    return biggestFace

def getAngleOfRotation(frame):
    twoEyes=getAllEyeXsAndYs(frame)
    if twoEyes[0]==None or twoEyes[1]==None: return data.glassesTheta
    x01,y01,x02,y02=twoEyes[0]
    x11,y11,x12,y12=twoEyes[1]
    avgX1=float(x01+x02)/2
    avgX2=float(x11+x12)/2
    avgY1=float(y01+y02)/2
    avgY2=float(y11+y12)/2
    dX=min(avgX1,avgX2)-max(avgX2,avgX1)
    dY=min(avgY2,avgY1)-max(avgY2,avgY1)
    theta=math.atan(dY/dX)
    return theta


def getEyeXAndY(frame):
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eyerects=detect(gray,data.eyeCascade)
    twoEyes=getTwoEyes(eyerects)
    if twoEyes[0]==None or twoEyes[1]==None: return data.x,data.y
    x01,y01,x02,y02=twoEyes[0]
    x11,y11,x12,y12=twoEyes[1]
    movement=30
    finalX=((x01+x02)/2+(x11+x12)/2)/2-abs(x01-x11)-movement*data.glassesScale/2
    finalY=((y01+y02)/2+(y11+y12)/2)/2-abs((y01-y02))+movement*2
    smoothFactor=10
    aLargeDistance=20
    if abs(finalX-data.x)<smoothFactor: finalX=data.x
    if abs(finalY-data.y)<smoothFactor:finalY=data.y
    elif abs(finalX-data.x)>aLargeDistance and data.firstFrame==False:finalX=data.x
    elif abs(finalY-data.y)>aLargeDistance and data.firstFrame==False:finalY=data.y
    return finalX,finalY

def getGlassesScale(frame):
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    facerects=detect(gray,data.faceCascade)
    if len(facerects)==0: return 1
    rect=getBiggestFace(facerects)
    x0,y0,x1,y1=rect
    faceWidth=abs(x1-x0)
    #calculated using my desired values and using a best fit 
    #linear regression
    scale=round(0.0035*faceWidth-0.507,1)
    return scale


data=Struct()
data.glassesImgW=None
data.glassesImgH=None
cap=cv2.VideoCapture(0)
data.prevGray=None
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
data.frameCounter=0
data.prevHorizontalDistances,data.prevVerticalDistances=None,None
counter=0
#data.x,data.y=400,400
data.glasses=None
data.glassesScale=1
data.glassesTheta=0
eyes="haarcascades/haarcascade_eye.xml"
face="haarcascades/haarcascade_frontalface_alt.xml"
data.eyeCascade=cv2.CascadeClassifier(eyes)
data.faceCascade=cv2.CascadeClassifier(face)
data.x,data.y=width/2,height/2
data.firstFrame=True
while (True):
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    data.frameCounter+=1
    #cv2.imshow("hi",frame)
    data.x,data.y=getEyeXAndY(frame)
    data.glassesScale=getGlassesScale(frame)
   # data.glassesTheta=getAngleOfRotation(frame)
    if data.x==None:
        cv2.imshow("hi",frame)
    else: 
        frame=drawGlasses(frame)
        cv2.imshow("hi",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
    counter+=1
    data.firstFrame=False
cap.release()
cv2.destroyAllWindows()