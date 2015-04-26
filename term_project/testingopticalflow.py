import cv2
import numpy as np

import time
import math


class Struct(): pass
data=Struct()
data.xvel,data.yvel=0,0
data.xsum,data.ysum=0,0
class OpticalFlowCalculator:

    def __init__(self,frame_width,frame_height,flow_color_rgb=(0,255,0)):
        self.move_step=10
        self.size=(int(frame_width),int(frame_height))
        self.prev_gray=None
        self.prev_time=None

    def processBytes(self,rgbBytes,distance=None,timestep=1):
        frame=np.frombuffer(rgb_bytes,np.uint8)
        frame=np.reshape(frame,(self.size[1],self.size[0],3))
        return self.processFrame(frame,distance,timestep)
    def processFrame(self, frame, distance=None, timestep=1):
        '''
        Processes one image frame, returning summed X,Y flow
        Optional inputs are:
          distance - distance in meters to image (focal length) for returning flow in meters per second
          timestep - time step in seconds for returning flow in meters per second
        '''

        frame2 = cv2.resize(frame, self.size)
 
        gray = cv2.cvtColor(frame, cv2.cv.CV_BGR2GRAY)

        xsum, ysum = 0,0

        xvel, yvel = 0,0
        
        if self.prev_gray != None:

            flow = cv2.calcOpticalFlowFarneback(self.prev_gray, gray, pyr_scale=0.5, levels=5, winsize=13, iterations=10, poly_n=5, poly_sigma=1.1, flags=0) 
            for y in range(0, flow.shape[0], self.move_step):
                for x in range(0, flow.shape[1], self.move_step):
                    fx, fy = flow[y, x]
                    xsum += fx
                    ysum += fy
                    #####IMPORTANT####
                    cv2.line(frame2, (x,y), (int(x+fx),int(y+fy)), (0,244,0))
                    cv2.circle(frame2, (x,y), 1, (0,244,0), -1)

            # Default to system time if no timestep
            curr_time = time.time()
            if not timestep:
                timestep = (curr_time - self.prev_time) if self.prev_time else 1
            self.prev_time = curr_time

            xvel = self._get_velocity(flow, xsum, flow.shape[1], distance, timestep)
            yvel = self._get_velocity(flow, ysum, flow.shape[0], distance, timestep)

        self.prev_gray = gray


        cv2.imshow("hi", frame2)
        if cv2.waitKey(1) & 0x000000FF== 27: # ESC
            return None
        
       # Normalize and divide by timestep
        return  xvel, yvel
    def _get_velocity(self, flow, sum_velocity_pixels, dimsize_pixels, distance_meters, timestep_seconds):
        count =  (flow.shape[0] * flow.shape[1]) / self.move_step**2
        average_velocity_pixels_per_second = sum_velocity_pixels / count / timestep_seconds
        return average_velocity_pixels_per_second

cap=cv2.VideoCapture(0)
width    = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
height   = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
scaledown = 1
movestep = 10
flow = OpticalFlowCalculator(width, height) 
start_sec = time.time()
while True:
    success, frame = cap.read()           
    if not success:
        break
    result = flow.processFrame(frame)
    #print result
    if not result:
        break

    elapsed_sec = time.time() - start_sec




