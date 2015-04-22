from Tkinter import *
import Tkinter as tk
import cv2
from PIL import Image, ImageTk

width, height = 680, 400
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)
root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit())
lmain = tk.Label(root)
lmain.pack()

def drawBackground(canvas,image):
    color="SlateBlue3"
    canvas.create_rectangle(0,0,1000,500,fill=color,
        width=0)
    canvas.create_image(50,50,anchor=NW,image=image)
def show_frame(canvas):
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    drawBackground(canvas,imgtk)
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame(canvas))
    show_frame(canvas)
#def update
global canvas
canvas=Canvas(root,width=1000,height=500)
canvas.pack()
show_frame(canvas)

root.mainloop()