from Tkinter import *
import Tkinter as tk
from PIL import Image, ImageTk

class Struct: pass
class Dot(object):
    def __init__(self,x,y,n):
        self.cx=x
        self.cy=y
        self.r=7
        self.n=n
    def draw(self,canvas):
        x,y=self.cx,self.cy
        r=self.r
        canvas.create_oval(x-r,y-r,x+r,y+r,fill="white")
        canvas.create_text(x,y,text=str(self.n))
    def clickInside(self,x,y):
        r=self.r
        if (x>self.cx-r and x<self.cx+r
         and y>self.cy-r and y<self.cy+r):
            return True
        return False
def drawBackground(canvas):
    canvas.create_rectangle(0,0,data.width,data.height,
        fill="black")
    canvas.create_image(data.width/2,data.height/2,anchor="c",image=data.img)
def drawAll(canvas):
    drawBackground(canvas)
    for dot in data.dots:
        dot.draw(canvas)
        print dot.n+"=("+str(dot.cx)+", "+str(dot.cy)+")"
    print "*******************"
def onMouseDown(event):
    for dot in data.dots:
        if dot.clickInside(event.x,event.y):
            data.clicked=True
            data.clickedDot=dot
            return
    data.clicked=False
def onMouseUp(event):
    if data.clicked==True:
        n=data.clickedDot.n
        data.dots.remove(data.clickedDot)
        data.dots.append(Dot(event.x,event.y,n))
        drawAll(canvas)
def makeDots():
    dot1=Dot(250,110,"A")
    dot2=Dot(340,200,"B")
    dot3=Dot(320,300,"C")
    dot4=Dot(250,350,"D")
    dot5=Dot(170,300,"E")
    dot6=Dot(160,200,"F")
    return [dot1,dot2,dot3,dot4,dot5,dot6]
def init():
    root=tk.Tk()
    global canvas, data
    canvas=Canvas(root,width=500,height=500)
    data=Struct()
    canvas.pack()
    data.width=500
    data.height=500
    data.dots=makeDots()
    canvas.bind("<Button-1>",onMouseDown)
    canvas.bind("<ButtonRelease-1>",onMouseUp)
    imageLabel=tk.Label(root)
    imageLabel.pack()
    #####image stuff#####
    start="facepictures/"
    picture="round.jpg"
    img=Image.open(start+picture)
    tkImg=ImageTk.PhotoImage(image=img)
    imageLabel._image_cache=tkImg
    data.img=tkImg
    drawAll(canvas)
    root.mainloop()

init()