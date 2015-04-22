from Tkinter import *
import Tkinter as tk

class Struct: pass
class Dot(object):
    def __init__(self,x,y,n):
        self.cx=x
        self.cy=y
        self.r=10
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
def updateAll(canvas):
    drawAll(canvas)
def drawAll(canvas):
    drawBackground(canvas)
    for dot in data.dots:
        dot.draw(canvas)
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
    dot1=Dot(100,100,1)
    dot2=Dot(200,200,2)
    dot3=Dot(300,150,3)
    dot4=Dot(100,450,4)
    dot5=Dot(400,400,5)
    dot6=Dot(130,300,6)
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
    drawAll(canvas)
    root.mainloop()

init()