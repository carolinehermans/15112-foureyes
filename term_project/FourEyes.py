from Tkinter import *
import Tkinter as tk
import cv2
from PIL import Image, ImageTk
import os

"""last updated april 22"""

###########################################################
################# FACE SHAPE ALGORITHM ####################
###########################################################

def areSimilarDimensions(lenA,lenB):
    ratio = 1.0*lenA/lenB
    #saying that the ratio almost equals 1, with some room for variation
    allowedRatioDifference=0.3
    return abs(ratio-1.0)<=allowedRatioDifference

def areSimilarRatios(ratioA,ratioB):
    allowedRatioDifference=0.2
    return abs(ratioA-ratioB)<=allowedRatioDifference

def isHeartFace(faceDimensions):
    forehead,jaw,faceLength,faceWidth=faceDimensions
    #A face is heart shaped if the forehead is significantly wider than the jaw.
    foreheadJawRatio=1.0*forehead/jaw
    differentSizeRatio=1.24 #chosen based on tests
    #checking if the forehead is significantly the widest part of the face
    return foreheadJawRatio>differentSizeRatio

def isOvalFace(faceDimensions):
    forehead,jaw,faceLength,faceWidth=faceDimensions
    #A face is oval shaped if the face is approx 1.5 times as long as 
    #it is wide or more, but it was too sensitive so 1.55 gives more accurate
    #results
    lengthWidthRatio=1.0*faceLength/faceWidth
    idealOvalRatio=1.55
    return lengthWidthRatio>=idealOvalRatio

def isSquareFace(faceDimensions):
    #a face is square if the forehead and jaw are approximately the same width
    forehead,jaw,faceLength,faceWidth=faceDimensions
    foreheadJawRatio=1.0*forehead/jaw
    idealSquareForeheadJawRatio=1.0
    return areSimilarRatios(foreheadJawRatio,idealSquareForeheadJawRatio)

def getFaceShape(faceDimensions):
    #heart is the next distinctive, if the forehead is the widest, that
    #person's face is definitely a heart. therefore, it gets checked first.
    if isHeartFace(faceDimensions)==True:
        return "heart"
    #oval is the next most distinctive, so it gets checked second. If the length 
    #is about 1.5 times the width, it's an oval.
    if isOvalFace(faceDimensions)==True:
        return "oval"
    #then comes square, with angular features and similar widths everywhere
    elif isSquareFace(faceDimensions)==True:
        return "square"
    #last remaining face shape
    else: return "round"

def getFaceDimensions(dots):
    #the information about distances is stored in the dots made earlier
    (ax,ay)=dots[0].cx,dots[0].cy
    (bx,by)=dots[1].cx,dots[1].cy
    (cx,cy)=dots[2].cx,dots[2].cy
    (dx,dy)=dots[3].cx,dots[3].cy
    (ex,ey)=dots[4].cx,dots[4].cy
    (fx,fy)=dots[5].cx,dots[5].cy
    #distance formula between particular dots
    foreheadWidth=((fx-bx)**2+(fy-by)**2)**0.5
    jawWidth=((ex-cx)**2+(ey-cy)**2)**0.5
    faceLength=((ax-dx)**2+(ay-dy)**2)**0.5
    faceWidth=(foreheadWidth+jawWidth)/2.0
    return (foreheadWidth,jawWidth,faceLength,faceWidth)

###########################################################
###################### CLASSES ############################
###########################################################

class Struct: pass

class Button(object): #buttons that respond to beind clicked and reset after
    def __init__(self,text,font,x0,y0,x1,y1):
        #allows for formatting of how button text looks
        self.text=text 
        self.font=font
        self.x0=x0
        self.x1=x1
        self.y0=y0
        self.y1=y1
        self.buttonInset=4 #how much it sets into the screen when clicked
        #default colors: when it's clicked, it's clickColor, when it's 
        #unclicked, it's data.highlightColor
        self.color=data.highlightColor
        self.isClicked=False
        self.clickColor=rgbString(115,107,153)
    def draw(self,canvas):
        #draws the button and puts the text in the middle
        offset=self.buttonInset
        if self.isClicked==False:
            canvas.create_rectangle(self.x0+offset,self.y0+offset,
                self.x1+offset,self.y1+offset,fill=self.clickColor,width=0)
        canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1,
            fill=self.color,width=0)
        canvas.create_text((self.x0+self.x1)/2,(self.y0+self.y1)/2,
            fill=data.backgroundColor,text=self.text,font=self.font)
    def clicked(self):
        #when it's clicked, it sets into the screen and changes color
        self.isClicked=True
        self.color=self.clickColor
        self.x0+=self.buttonInset
        self.x1+=self.buttonInset
        self.y0+=self.buttonInset
        self.y1+=self.buttonInset
    def unclicked(self):
        #once it's unclicked, it undoes what clicking does and sets it back 
        #and resets the color
        self.color=data.highlightColor
        self.x0-=self.buttonInset
        self.x1-=self.buttonInset
        self.y0-=self.buttonInset
        self.y1-=self.buttonInset
        self.isClicked=False
    def setColor(self,color):
        self.color=color

class Dot(object):
    def __init__(self,x,y,n,color):
        #each dot has a location, a radius, and a "number"
        self.cx=x
        self.cy=y
        self.r=6
        self.n=n
        self.color=color
    def draw(self,canvas):
        x,y=self.cx,self.cy
        r=self.r
        canvas.create_oval(x-r,y-r,x+r,y+r,fill=self.color,width=2)
        #canvas.create_text(x,y,text=str(self.n))
    def clickInside(self,x,y):
        r=self.r*2 #gives user extra distance to mess up their click a bit
        if (x>self.cx-r and x<self.cx+r
         and y>self.cy-r and y<self.cy+r):
            return True
        return False

###########################################################
################## MAKE DOTS/BUTTONS ######################
###########################################################

def sortDots():
    #sorts the dots in order based on their dot number (dot.n) so that I can 
    #know which dot is where
    numDots=6
    newDots=[]
    for i in xrange(numDots):
        for dot in data.dots:
            if dot.n==i:
                newDots.append(dot)
    return newDots

def makeDots():
    #makes dots at expected coordinates based on the face detection
    dotList=[]
    x,y,w,h=data.facerect #the rectangle is where the face is detected
    babyspc=w/11
    smallspc=w/8
    medspc=w/5
    bigspc=w/4
    offset=data.offset
    yoffset=200
    color="white"
    dot1=Dot(x=x+w/2+offset,y=y-smallspc+yoffset,n=0,color=color) 
    dot2=Dot(x=x+w-smallspc+offset,y=y+bigspc+yoffset,n=1,color=color)
    dot3=Dot(x=x+w-smallspc+offset,y=y+h/2+bigspc+yoffset,n=2,color=color)
    dot4=Dot(x=x+w/2+offset,y=y+h+yoffset,n=3,color=color)
    dot5=Dot(x=x+medspc+offset,y=y+h/2+bigspc+yoffset,n=4,color=color)
    dot6=Dot(x=x+smallspc+offset,y=y+bigspc+yoffset,n=5,color=color)
    return [dot1,dot2,dot3,dot4,dot5,dot6] #returns array of all the dots

def makeStartButton():
    #creates the take a photo button
    text="Take a Photo"
    font="Verdana 45 bold"
    x0=data.width/3
    y0=2.5*data.height/4
    x1=2*data.width/3
    y1=3*data.height/4
    data.startButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1) 

def makeSeeBestGlassesButton():
    #creates the "see best style for you" button
    x0=180
    y0=560
    x1=data.width-x0
    y1=640
    text="See Best Style For You"
    font="Verdana 50 bold"
    data.seeBestGlassesButton=Button(text=text,font=font,x0=x0,y0=y0,
        x1=x1,y1=y1)

def makeDoneWithDotsButton():
    #creates the "done" button for users to press after they're done with dots
    x0,y0,x1,y1=230,690,470,760
    text="DONE"
    font="Verdana 50 bold"
    data.doneWithDotsButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeBrowseFramesButton():
    #makes the buttons for users to browse frames
    x0=320
    x1=data.width-x0
    y0=640
    y1=700
    text="Browse These Frames"
    font="Verdana 40 bold"
    #button
    data.browseFramesButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeTryThemOnButton():
    #makes the button for people to try on glasses
    x0=320
    x1=data.width-x0
    y0=715
    y1=775
    text="Try Them On"
    font="Verdana 40 bold"
    data.tryThemOnButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeBrowseFramesBackButton():
    #makes the back button for the browse frames screen
    x0=30
    x1=280
    y0=data.height-50
    y1=data.height-120
    text="< BACK"
    font="Verdana 50 bold"
    data.browseFramesBackButton=Button(text=text,font=font,
        x0=x0,y0=y0,x1=x1,y1=y1)

def makeTryThemOnBackButton():
    #makes the try them on back button
    x0=30
    x1=280
    y0=data.height-20
    y1=data.height-80
    text="< BACK"
    font="Verdana 43 bold"
    data.tryThemOnBackButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

###########################################################
#################### MISCELLANEOUS ########################
###########################################################

###from course notes
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

#returns the suggested frames for each face shape
#sets the glasses types it's looking for into data
def getSuggestedFrames():
    if data.faceShape=="oval":
        data.glasses=["Square","Rectangular"]
        return "Square Frames"
    elif data.faceShape=="heart":
        data.glasses=["Rimless","Wire"]
        return "Thin Frames"
    elif data.faceShape=="square":
        data.glasses=["Oval","Round"]
        return "Rounded Frames"
    elif data.faceShape=="round":
        data.glasses=["Rectangular"]
        return "Rectangular Frames"

#modified version of the function in the course notes, returns .txt file as a
#list of lines for my purposes of putting writeups on multiple lines
def readFile(filename, mode="rt"):
    # rt = "read text"
    alltext=[]
    with open(filename, mode) as fin:
        for line in fin:
            alltext.append(line)
    return alltext


###########################################################
############# MOUSE FUNCTIONS/CLICK CHECKS ################
###########################################################

#checks if the start button has clicked
def clickInStartButton(x,y):
    x0,y0,x1,y1=(data.startButton.x0,data.startButton.y0,data.startButton.x1,
    data.startButton.y1)
    data.takeAPhoto=True
    return x>x0 and x<x1 and y>y0 and y<y1

#checks if they've taken a photo
def clickInPhotoButton(x,y):
    x0=900-100
    x1=900+100
    y0=data.height-data.height/8-100
    y1=data.height-data.height/8+100
    if x>x0 and x<x1 and y>y0 and y<y1: return True
    return False

#checks if they've clicked the "see best glasses" button
def clickSeeBestGlasses(x,y):
    x0,y0,x1,y1=(data.seeBestGlassesButton.x0,data.seeBestGlassesButton.y0,
        data.seeBestGlassesButton.x1,data.seeBestGlassesButton.y1)
    if x>x0 and x<x1 and y>y0 and y<y1: 
        return True
    return False

#checks if they've clicked the "browse frames" button
def clickBrowseFrames(x,y):
    x0=320
    x1=data.width-x0
    y0=640
    y1=700
    return x>x0 and x<x1 and y>y0 and y<y1

#checks if they've clicked the "done with dots" button
def clickDoneWithDots(x,y):
    x0,y0,x1,y1=(data.doneWithDotsButton.x0,data.doneWithDotsButton.y0,
            data.doneWithDotsButton.x1,data.doneWithDotsButton.y1)
    if x>x0 and x<x1 and y>y0 and y<y1: return True

#checks if they've clicked the "try them on" button
def clickTryThemOn(x,y):
    x0=320
    x1=data.width-x0
    y0=715
    y1=775
    return x>x0 and x<x1 and y>y0 and y<y1

#checks if they've clicked the "browse frames" back button
def clickBrowseFramesBackButton(x,y):
    x0=30
    x1=280
    y0=data.height-120
    y1=data.height-50
    return x>x0 and x<x1 and y>y0 and y<y1

#checks if they've gone between prev pages
def clickPreviousPage(x,y):
    if data.pageNumber==1: return False
    y0=data.height-110
    r=50
    xspacing=140
    x0=data.width/2-xspacing
    return x>x0-r and x<x0+r and y>y0-r and y<y0+r

#checks if they've gone to next page
def clickNextPage(x,y):
    if data.pageNumber==data.totalPages: return False
    y0=data.height-110
    r=50
    xspacing=140
    x0=data.width/2+xspacing
    return x>x0-r and x<x0+r and y>y0-r and y<y0+r

def clickTryThemOnBackButton(x,y):
    x0=30
    x1=280
    y0=data.height-20
    y1=data.height-80
    return x>x0 and x<x1 and y<y0 and y>y1

def haventStartedMouseUp(x,y):
    if clickInStartButton(x,y):
        data.start=True

def haventPausedMouseUp(x,y):
    if clickInPhotoButton(x,y):
        data.pause=True
        ret,frame=data.cap.read()
        frame=cv2.flip(frame,1)
        #find the face bounding box on the paused frame
        data.facerect=detectFace(frame)
        data.dots=makeDots()

def havePausedDotsMouseUp(x,y):
        if clickDoneWithDots(x,y):
            data.doneWithDotsButton.clicked()
            faceDimensions=getFaceDimensions(data.dots)
            data.faceShape=getFaceShape(faceDimensions)
            data.takeAPhoto=False
            data.faceShapeInfo=True

def tryThemOnMouseUp(x,y):
    if clickTryThemOnBackButton(x,y):
        data.showBestGlasses=True
        data.tryThemOn=False
        data.tryThemOnBackButton.unclicked()
        data.tryThemOnButton.unclicked()

def browseFramesMouseUp(x,y):
    if clickBrowseFramesBackButton(x,y):
        data.showBestGlasses=True
        data.browseFrames=False
        data.browseFramesBackButton.unclicked()
        data.browseFramesButton.unclicked()
    elif clickPreviousPage(x,y):
        data.pageNumber-=1
    elif clickNextPage(x,y):
        data.pageNumber+=1

def doneWithDotsMouseUp(x,y):
    if clickSeeBestGlasses(x,y):
        data.showBestGlasses=True
        data.doneWithDotsButton.unclicked()
    if data.showBestGlasses==True and clickBrowseFrames(x,y):
        data.showBestGlasses=False
        data.browseFrames=True
        data.pageNumber=1 #resets browse frames page number to 1 every time
    if data.showBestGlasses==True and clickTryThemOn(x,y):
        data.showBestGlasses=False
        data.tryThemOn=True
    if data.browseFrames==True:
        browseFramesMouseUp(x,y)
    if data.tryThemOn==True:
        tryThemOnMouseUp(x,y)

#moves the dots around when the mouse is released
def clickedMouseUp(event):
    n=data.clickedDot.n
    data.dots.remove(data.clickedDot)
    data.dots.append(Dot(event.x,event.y,n,data.highlightColor))
    data.dots=sortDots()
    data.startButton.unclicked()

def onMouseUp(event):
    if data.clicked==True:
        data.draggingDots=False
        clickedMouseUp(event)
    elif data.start==False:
        haventStartedMouseUp(event.x,event.y)
    elif data.pause==False:
        haventPausedMouseUp(event.x,event.y)     
    elif data.pause==True:
        havePausedDotsMouseUp(event.x,event.y)
    if data.doneWithDots==True:
        doneWithDotsMouseUp(event.x,event.y)

def haventStartedMouse(x,y):
    if clickInStartButton(x,y):
        data.startButton.clicked()

def haventPausedMouse(x,y):
    if clickInPhotoButton(x,y):
        data.photoIconClicked=True
        ret,frame=data.cap.read()
        frame=cv2.flip(frame,1)
        #find the face bounding box on the paused frame
        data.facerect=detectFace(frame)

def havePausedDotsMouse(x,y):
    if data.dots:
        for dot in data.dots:
            if dot.clickInside(x,y):
                clickColor=rgbString(115,107,153)
                data.clicked=True
                data.draggingDots=True
                data.clickedDot=dot
                n=dot.n
                data.dots.remove(dot)
                newDot=Dot(x,y,n,clickColor)
                data.dots.append(newDot)
                data.clickedDot=newDot
                data.dots=sortDots()
                return
        data.clicked=False
    if clickDoneWithDots(x,y):
        data.doneWithDotsButton.clicked()

def tryThemOnMouse(x,y):
    if clickTryThemOnBackButton(x,y):
        data.tryThemOnBackButton.clicked()

def browseFramesMouse(x,y):
    if clickBrowseFramesBackButton(x,y):
        data.browseFramesBackButton.clicked()

def doneWithDotsMouse(x,y):
    if clickSeeBestGlasses(x,y):
        data.seeBestGlassesButton.clicked()
    if data.showBestGlasses==True and clickBrowseFrames(x,y):
        data.browseFramesButton.clicked()
    if data.showBestGlasses==True and clickTryThemOn(x,y):
        data.tryThemOnButton.clicked()
    if data.browseFrames==True:
        browseFramesMouse(x,y)
    if data.tryThemOn==True:
        tryThemOnMouse(x,y)

def onMouseDown(event):
    if data.start==False:
        haventStartedMouse(event.x,event.y)
    elif data.pause==False:
        haventPausedMouse(event.x,event.y)     
    elif data.pause==True:
        havePausedDotsMouse(event.x,event.y)
    if data.doneWithDots==True:
        doneWithDotsMouse(event.x,event.y)

#this function is used for the click and drag dots feature
def clickAndDrag(event):
    clickColor=rgbString(115,107,153)
    if data.draggingDots==True:
        n=data.clickedDot.n
        data.dots.remove(data.clickedDot)
        newDot=Dot(event.x,event.y,n,clickColor)
        data.dots.append(newDot)
        data.clickedDot=newDot
        data.dots=sortDots()

###########################################################
#################### DRAW FUNCTIONS #######################
###########################################################

#these are my draw functions, listed in order they appear in my program,
#with drawAll at the bottom

def drawBackground(canvas):
    #draws the purple area in the back of each screen
    data.backgroundColor=rgbString(66,51,98)
    rectW,rectH=1200,800
    data.offset=50
    offset=data.offset
    canvas.create_rectangle(0,0,rectW*2,rectH*2,
        fill=data.backgroundColor,width=0)

def drawFrame(canvas,img):
    #draws the webcam feed
    xoffset=50
    yoffset=200
    canvas.create_image(xoffset,yoffset,anchor=NW,image=img)

def drawStartScreen(canvas):
    #sets up size of the button
    #draws the background
    #canvas.create_rectangle(0,0,data.width*2,data.height*2,
       # fill=data.backgroundColor,width=0)
    mainText="FourEyes"
    font="Eurostile 160 bold"
    #draws the title
    canvas.create_text(data.width/2,data.height/4,anchor="c",
        fill=data.highlightColor,text=mainText,font=font)
    filler1="Learn which glasses frames will look"
    filler2="the best with your face shape."
    font="Verdana 35"
    #draws the descriptions
    canvas.create_text(data.width/2,1.7*data.height/4,anchor="c",
        fill=data.accentColor,text=filler1,font=font)
    canvas.create_text(data.width/2,1.9*data.height/4,anchor="c",
        fill=data.accentColor,text=filler2,font=font)
    data.startButton.draw(canvas)

#take a photo screen
def drawTakeAPhotoScreen(canvas):
    text="Take a Photo"
    font="Verdana 80 bold"
    canvas.create_text(data.width/2,data.height/8,text=text,font=font,
        fill="white")
    xoffset=30
    yoffset=180
    x2=670
    y2=670
    canvas.create_rectangle(xoffset,yoffset,x2,y2,fill=data.accentColor,width=7,
        outline=data.highlightColor)
    drawInstructionText(canvas)
    if data.photoIconClicked==False:
        drawPhotoIcon(canvas)
    else:
        drawClickedPhotoIcon(canvas)

def drawInstructionText(canvas):
    #draws take a photo instructions
    rule1="1. Put your hair back"
    rule2="2. Put your entire"
    rule2b="    face in the frame"
    rule3="3. Make sure there is"
    rule3b="    light on your face"
    color=data.accentColor
    smallspc=50
    spc=100
    font="Verdana 40"
    x0,y0=715, 225
    canvas.create_text(x0,y0,anchor="nw",text=rule1,fill=color,font=font)
    canvas.create_text(x0,y0+spc,anchor="nw",text=rule2,fill=color,font=font)
    canvas.create_text(x0,y0+spc+smallspc,anchor="nw",text=rule2b,fill=color,
        font=font)
    canvas.create_text(x0,y0+spc+smallspc+spc,anchor="nw",text=rule3,fill=color,
        font=font)
    canvas.create_text(x0,y0+spc+smallspc+spc+smallspc,anchor="nw",text=rule3b,
        fill=color,font=font)

def drawClickedPhotoIcon(canvas):
    img=ImageTk.PhotoImage(file="clickedcamera.gif")
    data.imageLabel._image_cache=img
    x=900+5
    canvas.create_image(x,data.height-data.height/8+5,
        anchor="c",image=img)

def drawPhotoIcon(canvas):
    #the button to take a photo
    img=ImageTk.PhotoImage(file="camera.gif")
    data.imageLabel._image_cache=img
    x=900
    canvas.create_image(x,data.height-data.height/8,
        anchor="c",image=img)

#the screen for dragging the dots
def drawDotScreen(canvas):
    drawBackground(canvas)
    text="Drag the Dots"
    font="Verdana 80 bold"
    color=data.highlightColor
    canvas.create_text(data.width/2,data.height/8,text=text,font=font,
        fill=color)
    xoffset=30
    yoffset=180
    x2=670
    y2=670
    canvas.create_rectangle(xoffset,yoffset,x2,y2,fill=data.accentColor,width=7,
        outline=data.highlightColor)
    drawDotInstructions(canvas)
    data.doneWithDotsButton.draw(canvas)

def drawDots(canvas):
    #draws the dots themselves
    drawBackground(canvas)
    drawFrame(canvas,data.pauseImg)#########
    for dot in data.dots:
        print data.clickedDot.n
        dot.draw(canvas)


#draws the instrctions for the dot screen
def drawDotInstructions(canvas):
    text2="For the best results,"
    text3="match the example as"
    text4="precisely as you can."
    color=data.accentColor
    font="Verdana 40"
    x=data.offset+880
    y0=590
    spacing=55
    canvas.create_text(x,y0,anchor="c",text=text2,font=font,fill=color)
    canvas.create_text(x,y0+spacing,anchor="c",text=text3,font=font,fill=color)
    canvas.create_text(x,y0+2*spacing,anchor="c",text=text4,font=font,
        fill=color)
    drawInstructionImage(canvas)

#draws the little picture of the dude I drew to show people how to 
#drag dots
def drawInstructionImage(canvas):
    img=ImageTk.PhotoImage(file="tpFace.gif")
    data.imageLabel._image_cache=img
    x=data.offset+715
    y=190
    canvas.create_image(x,y,anchor="nw",image=img)

#next screen: tell them their face shape
def drawFaceShapeScreen(canvas):
    drawBackground(canvas)
    data.pause=False
    text1="Your face shape is"
    text2=data.faceShape[0].upper()+data.faceShape[1:]
    filename=str(data.faceShape)+".txt"
    writeup=readFile("shapes/"+filename)
    font1="Verdana 60"
    font2="Verdana 170 bold"
    y0=90
    spacing=100
    canvas.create_text(data.width/2,y0,anchor="c",text=text1,font=font1,
        fill=data.highlightColor)
    canvas.create_text(data.width/2,y0+spacing,anchor="c",text=text2,font=font2,
        fill=data.highlightColor)
    drawFaceShapeWriteup(canvas,writeup)
    data.seeBestGlassesButton.draw(canvas)

def drawFaceShapeWriteup(canvas,writeup):
    #puts each line of the writup on a different line
    spacing=50
    y0=342
    font="Verdana 45"
    for i in xrange(len(writeup)):
        #this is a fix for a weird bug I get when center aligning text
        if i!=len(writeup)-1: 
            canvas.create_text(data.width/2,y0+spacing*i,text=writeup[i],
                fill=data.accentColor,font=font)
        else:
            newspc=41
            canvas.create_text(data.width/2,y0+newspc*i,text=writeup[i],
                fill=data.accentColor,font=font)
    data.doneWithDots=True ##########weird


def drawBestGlassesScreen(canvas):
    #finds the writeup for the person's face shape
    filepath="glassesrecs/"+data.faceShape+".txt"
    writeup=readFile(filepath)
    font="Verdana 80 bold"
    #finds the suggested frames for the person
    suggestedFrames=getSuggestedFrames()
    y0=80
    #tells the person their suggested frames
    canvas.create_text(data.width/2,y0,text=suggestedFrames,font=font,
        fill=data.highlightColor)
    drawGlassesImage(canvas)
    drawGlassesWriteup(canvas,writeup)
    data.browseFramesButton.draw(canvas)
    data.tryThemOnButton.draw(canvas)

def drawGlassesImage(canvas):
    #draws the photo I found for the person's glasses recommendation
    filename="recphotos/"+data.faceShape+".gif"
    img=ImageTk.PhotoImage(file=filename)
    data.imageLabel._image_cache=img
    x=50
    y=200
    canvas.create_image(x,y,anchor="nw",image=img)

def drawGlassesWriteup(canvas,writeup):
    #puts each line of my writeup on a different line
    font="Verdana 40"
    color=data.accentColor
    spacing=44
    y0=180
    x0=630
    linecounter=0
    for i in xrange(len(writeup)):
        line=writeup[i]
        canvas.create_text(x0,y0+linecounter*spacing,anchor="nw",fill=color,
        font=font,text=line)
        linecounter+=1


def drawBrowseFramesPageText(canvas):
    font="Verdana 33 bold"
    text="Page "+str(data.pageNumber)+" of "+str(data.totalPages)
    y0=data.height-110
    canvas.create_text(data.width/2,y0,anchor="c",text=text,font=font,
        fill=data.accentColor)
    xspacing=140
    if data.pageNumber!=1:
        #if it's not the first page, let the user have a back button
        canvas.create_text(data.width/2-xspacing,y0,anchor="c",text="<",
            font=font,fill=data.accentColor)
    if data.pageNumber!=data.totalPages:
        #if it's not the last page, let the user have a next button
        canvas.create_text(data.width/2+xspacing,y0,anchor="c",text=">",
            font=font,fill=data.accentColor)

def drawBrowseFramesScreen(canvas):
    text="Frames For You"
    font="Verdana 80 bold"
    y0=80
    canvas.create_text(data.width/2,y0,anchor="c",text=text,
        font=font,fill=data.highlightColor)
    x0=50
    x1=data.width-x0
    y0=150
    y1=data.height-150
    canvas.create_rectangle(x0,y0,x1,y1,fill=data.accentColor,width=0)
    data.browseFramesBackButton.draw(canvas)
    drawBrowseFramesPageText(canvas)
    #TEMPORARY
    temptext="Fancy glasses gallery coming soon!"
    canvas.create_text(data.width/2,data.height/2,text=temptext,
        font="Verdana 40", fill=data.backgroundColor)

def drawTryThemOnScreen(canvas):
    text="Trying "+getSuggestedFrames()
    font="Verdana 80 bold"
    y0=80
    canvas.create_text(data.width/2,y0,anchor="c",text=text,
        font=font,fill=data.highlightColor)
    x0=205
    x1=data.width-x0
    y0=150
    y1=data.height-150
    canvas.create_rectangle(x0,y0,x1,y1,fill=data.accentColor,width=7,
        outline=data.highlightColor)
    data.tryThemOnBackButton.draw(canvas)
    temptext="Wow look it's your face! And you're wearing glasses!"
    canvas.create_text(data.width/2,data.height/2,text=temptext,
        font="Verdana 25", fill=data.backgroundColor)

def drawTryOnFrame(canvas,img):
    xoffset=233
    yoffset=175
    canvas.create_image(xoffset,yoffset,anchor=NW,image=img)

def drawAll(canvas):
    drawBackground(canvas)
    if data.showBestGlasses==True:
        drawBestGlassesScreen(canvas) 
    elif data.browseFrames==True:
        drawBrowseFramesScreen(canvas)####
    elif data.tryThemOn==True:
        drawTryThemOnScreen(canvas) 
        img=updateTryOnImage()
        drawTryOnFrame(canvas,img)         
    elif data.start==False:
        drawStartScreen(canvas)
    else:
        if data.pause==False and data.takeAPhoto==True:
            drawTakeAPhotoScreen(canvas)
            drawFrame(canvas,data.currImg)
        elif data.faceShapeInfo==True:
            drawFaceShapeScreen(canvas)
        else:
            drawDotScreen(canvas)
            drawFrame(canvas,data.pauseImg)
            for dot in data.dots:
                dot.draw(canvas)

###########################################################
################### UPDATE FUNCTIONS ######################
###########################################################

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
    if biggestFaceArea!=0: return biggestFace
    else: return (220, 100, 260, 280)

def updateTryOnImage():
    #gets new frame from webcam feed every time it's called
    ret,frame=data.cap.read()
    frame=cv2.flip(frame,1)
    if data.pause==True: data.cv2img=frame
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img=Image.fromarray(cv2image)
    h=760
    desiredW=data.height-70
    img=img.crop((0,0,desiredW,h))
    #converts to tkinter image
    tkImg=ImageTk.PhotoImage(image=img)
    data.imageLabel._image_cache=tkImg
    return tkImg

def updateImage():
    #gets new frame from webcam feed every time it's called
    ret,frame=data.cap.read()
    frame=cv2.flip(frame,1)
    if data.pause==True: data.cv2img=frame
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img=Image.fromarray(cv2image)
    h=450
    desiredW=600
    img=img.crop((0,0,desiredW,h))
    #converts to tkinter image
    tkImg=ImageTk.PhotoImage(image=img)
    data.imageLabel._image_cache=tkImg
    return tkImg

def updateAll(canvas):
    #continually updates the function
    img = updateImage()
    if data.pause==True:
        if data.pauseImg==None:
            data.pauseImg=img
        drawFrame(canvas,data.pauseImg)
        if data.dots==None: 
            data.facerect=detectFace(data.cv2img)
            data.dots=makeDots()
        drawAll(canvas)
    else:
        data.currImg=img
        drawAll(canvas)
    framerate=150
    canvas.after(framerate,func=lambda:updateAll(canvas))

###########################################################
#################### INIT FUNCTIONS #######################
###########################################################

def resetData():
    #starts all the booleans that tells us where in the program we are
    data.dots=None
    cap = cv2.VideoCapture(0) #gives a video feed
    data.cap=cap
    imgwidth,imgheight=800,450
    data.cap.set(3, imgwidth) #sets the size of the video feed
    data.cap.set(4, imgheight)
    data.pause=False #the image isn't paused
    w,h=1200,800
    data.width,data.height=w,h #width and height of the screen
    data.totalPages=4 #number of pages for browse frames
    #sets up colors for the program 
    data.backgroundColor=rgbString(66,51,98)
    data.accentColor=rgbString(195,186,235)
    data.highlightColor=rgbString(255,255,255)

def storePhaseBooleans():
    data.start=False
    data.clicked=False #button isn't clicked
    data.showBestGlasses=False #it isn't showing best glasses screen
    data.doneWithDots=False #it isn't done with the dots screen
    data.pauseImg=None #there is no paused picture available
    data.faceShapeInfo=False #not displaying info about faceshape
    data.takeAPhoto=False #not displaying take a photo screen
    data.tryThemOn=False #person isn't trying glasses on
    data.browseFrames=False #person isn't browsing frames
    data.photoIconClicked=False
    data.draggingDots=False

def makeButtons():
    makeStartButton()
    makeDoneWithDotsButton()
    makeTryThemOnBackButton()
    makeBrowseFramesBackButton()
    makeSeeBestGlassesButton()
    makeBrowseFramesButton()
    makeTryThemOnButton()

def run():
    root=tk.Tk()
    global data 
    data=Struct()
    resetData() 
    storePhaseBooleans() #tells us the phase in the program we're at
    makeButtons()
    canvas=Canvas(root,width=data.width,height=data.height)
    canvas.bind("<Button-1>",onMouseDown)
    canvas.bind("<B1-Motion>",clickAndDrag)
    canvas.bind("<ButtonRelease-1>",onMouseUp)
    canvas.pack()
    canvas.after(0,func=lambda:updateAll(canvas)) #continually updates 
    data.imageLabel=tk.Label(root)
    data.imageLabel.pack()
    drawBackground(canvas)
    root.mainloop()

run()