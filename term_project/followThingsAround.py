import cv2
import numpy as np
import cv
import time
import math

class Struct(): pass
def getOpticalFlowInDirections(frame,distance=None,timestep=1,moveStep=10):
    gray=frame
    xsum,ysum=0,0
    horizontalDistances=[]
    verticalDistances=[]
    if data.prevGray!=None:
        flow=cv2.calcOpticalFlowFarneback(data.prevGray, gray, pyr_scale=0.5, 
            levels=5, winsize=13, iterations=10, poly_n=5, poly_sigma=1.1, 
            flags=0) 
        for y in xrange(0,flow.shape[0],moveStep):
            horizontalDistanceRow=[]
            verticalDistanceRow=[]
            for x in xrange(0,flow.shape[1],moveStep):
                fx,fy=flow[y,x]
                xsum+=fx
                ysum+=fy
                #print xsum,ysum
                horizontalDistanceRow.append(xsum)
                verticalDistanceRow.append(ysum)
            horizontalDistances.append(horizontalDistanceRow)
            verticalDistances.append(verticalDistanceRow)
        currTime=time.time()
        data.prevTime=currTime
    data.prevGray=gray
    #print horizontalDistances,verticalDistances
    return horizontalDistances,verticalDistances

def findDistance(currentDist,prevDist):
    if prevDist==None:
        return None
    else:
        distanceSum=0
        distanceCounter=0
        for i in xrange(len(prevDist)):
            for j in xrange(len(prevDist[0])):
                currDistance=(currentDist[i][j]-prevDist[i][j])
                distanceSum+=currDistance
                distanceCounter+=1

    if distanceCounter!=0:
        return distanceSum/(distanceCounter*300)
    else: return 0
  

def getInitialEyePosition(frame):
    eyes="haarcascade_eye.xml"
    eyeCascade=cv2.CascadeClassifier(eyes)

def drawGlasses(frame,glasses=None):
    glasses=cv2.imread("square.jpg",-1)
    glasses=-glasses
    x_offset,y_offset=data.x,data.y
    for c in xrange(0,3):
        frameROI=frame[data.y:data.y+glasses.shape[0],data.x:data.x+glasses.shape[1],c] 
        newFrameROI=-glasses[:,:,c]*(glasses[:,:,1]/255.0)+frameROI*(1.0 - glasses[:,:,1]/255.0)
        frame[data.y:data.y+glasses.shape[0],data.x:data.x+glasses.shape[1],c]=newFrameROI
    cv2.imshow("hi",frame)

data=Struct()
cap=cv2.VideoCapture(0)
data.prevGray=None
width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
data.frameCounter=0
data.prevHorizontalDistances,data.prevVerticalDistances=None,None
counter=0
data.x,data.y=None,None
data.glasses=None
bgs = cv2.BackgroundSubtractorMOG(24*60, 1, 0.9, 0.01)
while (True):
    if counter%2==0:
        ret,frame=cap.read()
        frame=cv2.flip(frame,1)
        if data.x==None:
            data.x,data.y=getInitialEyePosition(frame)
        data.frameCounter+=1
        fgmask = bgs.apply(frame)
        data.horizontalDistances,data.verticalDistances=getOpticalFlowInDirections(fgmask)
        xMovement=findDistance(data.horizontalDistances,data.prevHorizontalDistances)
        yMovement=findDistance(data.verticalDistances,data.prevVerticalDistances)
        if xMovement!=None: data.x+=xMovement
        if yMovement!=None: data.y+=yMovement
        data.prevHorizontalDistances,data.prevVerticalDistances=data.horizontalDistances,data.verticalDistances
        drawGlasses(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    counter+=1
cap.release()
cv2.destroyAllWindows()

