import numpy as np
import cv2

# built-in modules
import os
import sys
import glob
import argparse
from math import *

drag_start = None
rect = (0,0,0,0)

drag_start = None
sel = (0,0,0,0)

def onmouse(event, x, y, flags, param):
    global drag_start, sel
    if event == cv2.EVENT_LBUTTONDOWN:
        drag_start = x, y
        sel = 0,0,0,0
    elif event == cv2.EVENT_LBUTTONUP:
        drag_start = None
    elif drag_start:
        #print flags
        if flags & cv2.EVENT_FLAG_LBUTTON:
            minpos = min(drag_start[0], x), min(drag_start[1], y)
            maxpos = max(drag_start[0], x), max(drag_start[1], y)
            sel = minpos[0], minpos[1], maxpos[0], maxpos[1]
            img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            cv2.rectangle(img, (sel[0], sel[1]), (sel[2], sel[3]), (255,0,0), 2)
            cv2.imshow("gray", img)
        else:
            print "selection is complete"
            drag_start = None

if __name__=='__main__':
    cv2.namedWindow("gray",1)
    cv2.setMouseCallback("gray", onmouse)
    '''Loop through all the images in the directory'''
    
    img=cv2.imread("test.png")     
    sel = (0,0,0,0)
    drag_start = None
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img2=img.copy()
    cv2.imshow("gray",gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
