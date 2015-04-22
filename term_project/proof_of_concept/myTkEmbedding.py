from Tkinter import *
import Tkinter as tk
import cv2
from PIL import Image, ImageTk

"""As of April 8:
Space: pause feed and draw face rectangle

All displayed in Tkinter
"""

def drawBackground(canvas):
    #draws the purple area around the image
    color="SlateBlue3"
    rectW,rectH=1200,800
    canvas.data.offset=50
    offset=canvas.data.offset
    canvas.create_rectangle(0,0,rectW*2,rectH*2,fill=color,width=0)
def drawFaceRectangle(canvas,img):
    #Tkinter, draws a rectangle around the face
    offset=canvas.data.offset
    x,y,w,h=canvas.data.facerect
    canvas.create_rectangle(x+offset,y+offset,x+w+offset,y+h+offset,
        outline="red",width=3)
def detectFace(cvFrame):
    #classifies faces, so it knows what to look for
    face_cascade =(
        cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_alt.xml'))
    gray=cv2.cvtColor(cvFrame,cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(gray, 1.3, 5)
    biggestFaceArea=0
    for face in faces:
        x,y,w,h=face
        #returns the biggest, most significant face it sees
        if (x+w)*(y+h)>biggestFaceArea:
            biggestFaceArea=(x+w)*(y+h)
            biggestFace=x,y,w,h
    #returns four coordinates so that it can draw the face box
    if biggestFace!=0: return biggestFace
    else: return "Error, no face detected!"
def drawFrame(canvas,img):
    #draws the webcam feed
    offset=canvas.data.offset
    canvas.create_image(offset,offset,anchor=NW,image=img)
def updateImage():
    #gets new frame from webcam feed every time it's called
    ret,frame=cap.read()
    frame=cv2.flip(frame,1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img=Image.fromarray(cv2image)
    h=450
    desiredW=600
    img=img.crop((0,0,desiredW,h))
    #converts to tkinter image
    tkImg=ImageTk.PhotoImage(image=img)
    imageLabel._image_cache=tkImg
    return tkImg
def keyPressed(event):
    if event.keysym=="space":
        #if they hit the space bar, pause the feed
        canvas.data.pause=True
        ret,frame=cap.read()
        frame=cv2.flip(frame,1)
        #find the face bounding box on the paused frame
        canvas.data.facerect=detectFace(frame)
def updateAll(canvas):
    #continually updates the function
    img = updateImage()
    if canvas.data.pause==True:
        drawFrame(canvas,img)
        drawFaceRectangle(canvas,img)
    else:
        root.after(15,func=lambda:updateAll(canvas))
        drawFrame(canvas,img)
def run():
    width, height = 800, 450
    global cap, root, imageLabel,canvas
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    root = tk.Tk()
    root.bind('<Escape>', lambda e: root.quit())
    root.bind("<Key>",keyPressed)
    imageLabel=tk.Label(root)
    imageLabel.pack()
    canvas=Canvas(root,width=1200,height=800)
    canvas.pack()
    class Struct: pass
    canvas.data=Struct()
    canvas.data.pause=False
    root.after(0,func=lambda:updateAll(canvas))
    drawBackground(canvas)
    drawFrame(canvas,updateImage())
    root.mainloop()
   
run()