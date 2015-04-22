
import numpy as np
import cv2
import video
import sys

if __name__ == '__main__':
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0

    cam=video.create_capture(video_src)
    mser=cv2.MSER()
    counter=0
    while True:
        ret,img=cam.read()
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        vis=img.copy()
        counter+=1
        areas=mser.detect(gray, None)
        hulls=[cv2.convexHull(p.reshape(-1,1,2)) for p in areas]
        if counter==1: print hulls
        cv2.polylines(vis,hulls,1,(0,255,0))
        cv2.circle(vis,(500,500),50,(0,0,255),10)
        cv2.imshow('img', vis)
        if 0xFF & cv2.waitKey(5) == 27:
            break
    cv2.destroyAllWindows()
