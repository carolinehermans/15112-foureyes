from Tkinter import *
import Tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import csv
import webbrowser

"""last updated april 27 at 9:36PM"""

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
        self.fontColor=data.backgroundColor
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
            fill=self.color,width=0,outline=data.highlightColor)
        canvas.create_text((self.x0+self.x1)/2,(self.y0+self.y1)/2,
            fill=self.fontColor,text=self.text,font=self.font)
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

class DarkerButton(Button):
    def __init__(self,text,font,x0,y0,x1,y1):
        #allows for formatting of how button text looks
        self.text=text 
        self.font=font
        self.fontColor=data.accentColor
        self.x0=x0
        self.x1=x1
        self.y0=y0
        self.y1=y1
        self.buttonInset=4 #how much it sets into the screen when clicked
        #default colors: when it's clicked, it's clickColor, when it's 
        #unclicked, it's data.highlightColor
        self.color=rgbString(115,107,153)
        self.isClicked=False
        self.clickColor=data.highlightColor
        self.clickColor=data.accentColor
    def draw(self,canvas):
        #draws the button and puts the text in the middle
        offset=self.buttonInset
        canvas.create_rectangle(self.x0,self.y0,self.x1,self.y1,
            fill=self.color,width=2,outline=data.accentColor)
        canvas.create_text((self.x0+self.x1)/2,(self.y0+self.y1)/2,
            fill=self.fontColor,text=self.text,font=self.font)

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
    def connect(self,other,canvas,clicked=None):
        if clicked==None: color="white"
        elif self is clicked or other is clicked:
            color=rgbString(115,107,153)
        else: color="white"
        canvas.create_line((self.cx,self.cy),(other.cx,other.cy),fill=color,
            width=2,dash=(2,12))

class GlassesDisplay(object):
    # A class for the visual representation of a pair of glasses, implemented
    # in the browse frames feature
    def __init__(self,name,shape,price,image,brand,link):
        # Each pair has all of these features
        self.name=name
        self.shape=shape
        self.price=self.getRealPrice(price)
        self.image="browseglasses/"+image+".gif"
        self.brand=brand
        self.link=link
        self.clicked=False
        self.x0=None
        self.x1=None
        self.y0=None
        self.y1=None
        self.shadow=8
    def __repr__(self):
        # Using repr to see information about the current pair
        result=("GlassesDisplay(name="+self.name+", shape="+self.shape+
            ", price="+self.price+", image="+self.image+", brand="+self.brand+
            ", link="+self.link+")")
        return result
    def getRealPrice(self,oldPrice):
        # In the csv, 150.00 is represented as 150, so this is a fix for that
        period=oldPrice.index(".")
        while len(oldPrice[period:])<=2:
            oldPrice+="0"
        return oldPrice
    def draw(self,canvas): #draws a white rectangle in the appropriate place
        if self.pageNumber!=data.pageNumber: return #if it's not on the page
        (left, top, xspacing, yspacing)=(80, 165, 80, 40)
        (width, height)=(400, 365/2)
        if self.position==3 or self.position==4: rowNum=2 #top half of screen
        else: rowNum=1 #bottom half of screen
        if self.position==1 or self.position==3: colNum=1 #left half of screen
        else: colNum=2 #right half of screen
        (x0, y0)=(left+colNum*xspacing+width*(colNum-1),
            top+yspacing*rowNum+height*(rowNum-1))
        (x1,y1)= (x0+width,y0+height) #spacing
        (self.x0, self.x1, self.y0, self.y1)=(x0, x1, y0, y1)
        if self.clicked==True: self.drawClicked(canvas) #draw the clicked button
        else:
            canvas.create_rectangle(x0+self.shadow,y0+self.shadow, #drop shadow
            x1+self.shadow,y1+self.shadow, fill=data.backgroundColor,width=0) 
            canvas.create_rectangle(x0,y0,x1,y1,fill=data.highlightColor,
                width=1,outline=data.backgroundColor) #the white box
            self.drawImage(canvas,x0,x1,y0,y1) #draw the glasses image
            self.drawText(canvas,x0,x1,y0,y1) #draw price and title
    def drawClicked(self,canvas):
        x0=self.x0
        x1=self.x1
        y0=self.y0
        y1=self.y1
        #draws the button in the darker color set into the screen when clicked
        canvas.create_rectangle(x0+self.shadow,y0+self.shadow,x1+self.shadow,
            y1+self.shadow,fill=data.backgroundColor,width=0)
        self.drawClickedText(canvas,x0,x1,y0,y1)
    def drawClickedText(self,canvas,x0,x1,y0,y1):
        #draws the same text as usual but offset by the shadow and white
        textY=y0+30+2*self.shadow
        textX=(x0+x1)/2+2*self.shadow
        font="Avenir 20 bold"
        color=data.highlightColor
        text='"'+self.name+'"'+" by "+self.brand
        canvas.create_text(textX,textY,font=font,fill=color,text=text)
        priceX=x1-10+self.shadow
        priceY=y1-5+self.shadow
        text="$"+self.price
        font="Avenir 25"
        canvas.create_text(priceX,priceY,text=text,
            anchor="se",font=font,fill=color)
    def drawText(self,canvas,x0,x1,y0,y1):
        #draws information about price and such
        textY=y0+30
        textX=(x0+x1)/2
        font="Avenir 20 bold"
        color=data.backgroundColor
        text='"'+self.name+'"'+" by "+self.brand
        canvas.create_text(textX,textY,font=font,fill=color,text=text)
        priceX=x1-10
        priceY=y1-5
        text="$"+self.price
        font="Avenir 25"
        canvas.create_text(priceX,priceY,text=text,anchor="se",font=font,
            fill=color)
    def drawImage(self,canvas,x0,x1,y0,y1):
        #draws the image for the glasses in the right spot
        imagepath=self.image
        img=ImageTk.PhotoImage(file=imagepath)
        #need 4 imagelabels to display 4 images at a time
        if self.position==1:
            data.imageLabel._image_cache=img
        elif self.position==2:
            data.imageLabel2._image_cache=img
        elif self.position==3:
            data.imageLabel3._image_cache=img
        else:
            data.imageLabel4._image_cache=img
        x=(x0+x1)/2
        y=y0+110
        canvas.create_image(x,y,anchor="c",image=img)
    def isClicked(self,x,y):
        #checks if the glasses pair has been clicked
        return (x>self.x0 and x<self.x1 and y>self.y0 and y<self.y1 and
            data.pageNumber==self.pageNumber)
    def linkToSite(self):
        #opens a link to the glasses pair's link
        webbrowser.open_new(self.link)
        
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
    offset=100
    yoffset=200
    color="white"
    dot1=Dot(x=x+w/2+offset,y=y-smallspc+yoffset,n=0,color=color) 
    dot2=Dot(x=x+w-smallspc+offset,y=y+bigspc+yoffset,n=1,color=color)
    dot3=Dot(x=x+w-smallspc+offset,y=y+h/2+medspc*1.5+yoffset,n=2,color=color)
    dot4=Dot(x=x+w/2+offset,y=y+h+yoffset,n=3,color=color)
    dot5=Dot(x=x+medspc+offset,y=y+h/2+medspc*1.5+yoffset,n=4,color=color)
    dot6=Dot(x=x+smallspc+offset,y=y+bigspc+yoffset,n=5,color=color)
    return [dot1,dot2,dot3,dot4,dot5,dot6] #returns array of all the dots

def makeStartButton():
    #creates the take a photo button
    text="Take a Photo"
    font="Helvetica 50 bold"
    x0=data.width/3
    y0=2.5*data.height/4
    x1=2*data.width/3
    y1=3*data.height/4
    data.startButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1) 

def makeSeeBestGlassesButton():
    #creates the "see best style for you" button
    x0=290
    y0=590
    x1=data.width-x0
    y1=690
    text="See Best Style For You"
    font="Helvetica 43 bold"
    data.seeBestGlassesButton=Button(text=text,font=font,x0=x0,y0=y0,
        x1=x1,y1=y1)

def makeDoneWithDotsButton():
    #creates the "done" button for users to press after they're done with dots
    midx=(80+720)/2
    x0,y0,x1,y1=midx-90,703,midx+90,773
    text="DONE"
    font="Helvetica 43 bold"
    data.doneWithDotsButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeBrowseFramesButton():
    #makes the buttons for users to browse frames
    x0=360
    x1=data.width-x0
    y0=615
    y1=680
    text="Browse These Frames"
    font="Helvetica 35 bold"
    #button
    data.browseFramesButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeTryThemOnButton():
    #makes the button for people to try on glasses
    x0=360
    x1=data.width-x0
    y0=695
    y1=760
    text="Try Them On"
    font="Helvetica 35 bold"
    data.tryThemOnButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeBrowseFramesBackButton():
    #makes the back button for the browse frames screen
    x0=80
    x1=180
    y0=data.height-50
    y1=data.height-120
    text="<"
    font="Helvetica 43 bold"
    data.browseFramesBackButton=Button(text=text,font=font,
        x0=x0,y0=y0,x1=x1,y1=y1)

def makeTryThemOnBackButton():
    #makes the try them on back button
    x0=48
    x1=138
    y0=data.height-33
    y1=data.height-103
    text="<"
    font="Helvetica 43 bold"
    data.tryThemOnBackButton=Button(text=text,font=font,x0=x0,y0=y0,x1=x1,y1=y1)

def makeResetButton():
    y0=700
    y1=765
    x0=data.width-222
    x1=data.width-82
    text="Restart"
    font="Helvetica 30 bold"
    #data.resetButton=DarkerButton(text=text,font=font,x0=x0,
        #y0=y0,x1=x1,y1=y1)


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
        data.glassesType= "Square Frames"
        return "Square Frames"
    elif data.faceShape=="heart":
        data.glasses=["Rimless","Wire"]
        data.glassesType= "Thin Frames"
        return "Thin Frames"
    elif data.faceShape=="square":
        data.glasses=["Oval","Round"]
        data.glassesType= "Rounded Frames"
        return "Rounded Frames"
    elif data.faceShape=="round":
        data.glasses=["Rectangular"]
        data.glassesType= "Rectangular Frames"
        return "Rectangular Frames"

def getGlassesList():
    #returns a list of all of the glasses that the specific user needs
    glassesList=None
    if data.faceShape=="heart":
        glassesList=data.glassesForHeart
    elif data.faceShape=="oval":
        glassesList=data.glassesForOval
    elif data.faceShape=="square":
        glassesList=data.glassesForSquare
    else:
        glassesList=data.glassesForRound
    return glassesList

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
    x0=940-100
    x1=940+100
    y0=600-100
    y1=600+100
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
    x0=360
    x1=data.width-x0
    y0=615
    y1=680
    return x>x0 and x<x1 and y>y0 and y<y1

#checks if they've clicked the "done with dots" button
def clickDoneWithDots(x,y):
    midx=(80+720)/2
    x0,y0,x1,y1=midx-90,703,midx+90,773
    if x>x0 and x<x1 and y>y0 and y<y1: return True

#checks if they've clicked the "try them on" button
def clickTryThemOn(x,y):
    x0=360
    x1=data.width-x0
    y0=695
    y1=760
    return x>x0 and x<x1 and y>y0 and y<y1

#checks if they've clicked the "browse frames" back button
def clickBrowseFramesBackButton(x,y):
    x0=80
    x1=180
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

#checks if they've clicked the try them on back button
def clickTryThemOnBackButton(x,y):
    x0=48
    x1=138
    y0=data.height-33
    y1=data.height-103
    return x>x0 and x<x1 and y<y0 and y>y1

#if they haven't hit start, waits for start button
def haventStartedMouseUp(x,y):
    if clickInStartButton(x,y):
        data.start=True

#if they haven't paused the image, waits for them to take a photo
def haventPausedMouseUp(x,y):
    if clickInPhotoButton(x,y):
        data.pause=True
        ret,frame=data.cap.read()
        frame=cv2.flip(frame,1)
        #find the face bounding box on the paused frame
        data.facerect=detectFace(frame)
        data.dots=makeDots()

def havePausedDotsMouseUp(x,y):
    #waits for them to click "done"
    if clickDoneWithDots(x,y): 
        data.doneWithDotsButton.clicked()
        faceDimensions=getFaceDimensions(data.dots)
        if data.faceShape==None:
            data.faceShape=getFaceShape(faceDimensions)
            data.glassesList=getGlassesList()
        if data.glassesType==None:
            getSuggestedFrames()
        #moves onto the next phase of the program
        data.takeAPhoto=False
        data.faceShapeInfo=True

def saveCurrentTryOnImage():
    #saves the image they're taking to the current directory
    data.numPhotosTaken+=1
    #because it's keeping track of numPhotosTaken, they won't save over each
    #other
    title="TryingGlasses"+str(data.numPhotosTaken)+".png"
    currImg=data.savedImage
    #an opencv image gets saved
    cv2.imwrite(title,currImg)

def clickCameraIcon(x,y):
    #checks if they've clicked the camera icon to take a photo
    x0=370
    y0=645
    x1=x0+157
    y1=y0+142
    return x>x0 and x<x1 and y>y0 and y<y1

def tryThemOnBackButtonClicked():
    #changes the phases of the program according to what happens
    #when the user clicks the try them on back button
    data.showBestGlasses=True
    data.tryThemOn=False
    data.tryThemOnBackButton.unclicked()
    data.tryThemOnButton.unclicked()
    data.pausedTryOn=False
    data.cameraClickedTryOn=False
    data.ableToClick=True
    data.canSeeBestGlasses=True
    data.browseFramesCantBeClicked=False

def tryThemOnMouseUp(x,y):
    #limits the program based on what can and can't be accessed
    data.browseFramesCantBeClicked=True
    data.canSeeBestGlasses=False
    data.browseFrames=False
    if clickTryThemOnBackButton(x,y):
        tryThemOnBackButtonClicked()
    else:
        data.ableToClick=False #limits what the program can click
    if data.cameraClickedTryOn==True: #if they click the play/camera button
        if data.pausedTryOn==False: #does the camera thing
            saveCurrentTryOnImage()
            data.pausedTryOn=True
            data.cameraClickedTryOn=False
        elif data.pausedTryOn==True:  #does the play button thing
            data.pausedTryOn=False
            data.cameraClickedTryOn=False
            data.shadedPlayButton=False

def browseFramesMouseUp(x,y):
    #restricts program from accessing old information
    data.canSeeBestGlasses=False
    if clickBrowseFramesBackButton(x,y): #resets phases of program
        data.showBestGlasses=True
        data.browseFrames=False
        data.browseFramesBackButton.unclicked()
        data.browseFramesButton.unclicked()
        data.ableToClick=True
        data.canSeeBestGlasses=True
    if clickPreviousPage(x,y): #if they click the forward or back arrows
        data.pageNumber-=1
    if clickNextPage(x,y):
        data.pageNumber+=1
    #link to website if they click a pair of glasses
    for glasses in data.glassesList: 
        if glasses.isClicked(x,y):
            glasses.linkToSite()
            glasses.clicked=False

def goToBrowseFramesPhase():
    #resets browse frames phase booleans
    data.canSeeBestGlasses=False
    data.showBestGlasses=False
    data.browseFrames=True
    data.pageNumber=1 
    data.ableToClick=False

def goToTryThemOnPhase():
    #resets try them on phase booleans
    data.showBestGlasses=False
    data.tryThemOn=True
    data.ableToClick=False
    data.browseFramesCantBeClicked=True

def doneWithDotsMouseUp(x,y):
    if (clickBrowseFrames(x,y) and data.ableToClick==True and 
        data.browseFramesCantBeClicked==False):
        goToBrowseFramesPhase() #should be in browse frames
    elif data.ableToClick==True and clickTryThemOn(x,y):
        goToTryThemOnPhase() #should be in try them on
    elif clickSeeBestGlasses(x,y) and data.canSeeBestGlasses==True:
        data.canSeeBestGlasses=True #goes to see best glasses phase
        data.showBestGlasses=True
        data.doneWithDotsButton.unclicked()
        data.ableToClick=True
        data.canSeeBestGlasses=True
        data.browseFramesCantBeClicked=False
    if data.browseFrames==True:
        data.canSeeBestGlasses=False
        browseFramesMouseUp(x,y)
    elif data.tryThemOn==True: #goes to next mouse phase
        tryThemOnMouseUp(x,y)

#moves the dots around when the mouse is released
def clickedMouseUp(event):
    n=data.clickedDot.n
    data.dots.remove(data.clickedDot) #removes and redraws clicked dot
    data.dots.append(Dot(event.x,event.y,n,data.highlightColor))
    data.dots=sortDots() #re-sorts them every time it draws a new one
    data.startButton.unclicked()

def onMouseUp(event):
    #mouse up functions based on various phases in programs
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
    #waits for the start button
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
    #if dots aren't None 
    if data.dots:
        for dot in data.dots:
            if dot.clickInside(x,y): #checks every dot
                clickColor=rgbString(115,107,153)
                data.clicked=True
                data.draggingDots=True #it's moving the dots and they're clicked
                data.clickedDot=dot
                n=dot.n
                data.dots.remove(dot) #takes out dot, puts a new one
                newDot=Dot(x,y,n,clickColor)
                data.dots.append(newDot)
                data.clickedDot=newDot
                data.dots=sortDots() #sorts dots every time
                return
        data.clicked=False #unclicked
    if clickDoneWithDots(x,y):
        data.doneWithDotsButton.clicked() #if they're done, clicks the button

def checkClickGlassesPair(x,y):
    #This is where it draws the purple rectangles around the current 
    #pair of glasses on the try-on screen
    x0=900
    x1=1130
    ya1,ya2=165,273 #boundaries for where the rectangles go
    yb1,yb2=296,402
    yc1,yc2=431,539
    yd1,yd2=573,680
    if x>x0 and x<x1: #changes current glasses pair depending on click
        if y>ya1 and y<ya2:
            data.glassesPair=0
        elif y>yb1 and y<yb2:
            data.glassesPair=1
        elif y>yc1 and y<yc2:
            data.glassesPair=2
        elif y>yd1 and y<yd2:
            data.glassesPair=3

def tryThemOnMouse(x,y):
    data.ableToClick=True
    if clickTryThemOnBackButton(x,y): #checks for the back button
        data.tryThemOnBackButton.clicked()
    checkClickGlassesPair(x,y) #checks if they've clicked different glasses 
    if clickCameraIcon(x,y): #checks if they've taken a photo
        if data.pausedTryOn==False: #if it's the camera, do the camera thing
            data.cameraClickedTryOn=True
            data.shadedPlayButton=False
        elif data.pausedTryOn==True: #if it's the play button, do that thing
            data.shadedPlayButton=True 
            data.cameraClickedTryOn=True

def browseFramesMouse(x,y):
    #sets up limits for what can and can't be clicked
    data.canHitBrowseFrames=False
    if clickBrowseFramesBackButton(x,y):
        #clicks button and does button things
        data.browseFramesBackButton.clicked()
        data.canHitBrowseFrames=True
    for glasses in data.glassesList:
        #checks for glasses clicks and animates them accordingly
        if glasses.isClicked(x,y):
            glasses.clicked=True

def doneWithDotsMouse(x,y):
    #checks for various clicked buttons and acts accordingly
    if data.showBestGlasses==True and clickBrowseFrames(x,y):
        data.browseFramesButton.clicked()
    if data.showBestGlasses==True and clickTryThemOn(x,y):
        data.tryThemOnButton.clicked()
    if clickSeeBestGlasses(x,y):
        data.seeBestGlassesButton.clicked()
    if data.browseFrames==True:
        browseFramesMouse(x,y)
    if data.tryThemOn==True:
        tryThemOnMouse(x,y)

def onMouseDown(event):
    #checks the phase and does the appropriate mouse function
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
    xoffset=100
    yoffset=209
    canvas.create_image(xoffset,yoffset,anchor=NW,image=img)

def drawStartScreen(canvas):
    #sets up size of the button
    #draws the background
    #canvas.create_rectangle(0,0,data.width*2,data.height*2,
       # fill=data.backgroundColor,width=0)
    mainText="FourEyes"
    font="Avenir 125 bold"
    #draws the title
    canvas.create_text(data.width/2,data.height/4,anchor="c",
        fill=data.highlightColor,text=mainText,font=font)
    filler1="Learn which glasses frames will look"
    filler2="the best with your face shape."
    font="Avenir 34"
    #draws the descriptions
    canvas.create_text(data.width/2,1.65*data.height/4-5,anchor="c",
        fill=data.accentColor,text=filler1,font=font)
    canvas.create_text(data.width/2,1.9*data.height/4-5,anchor="c",
        fill=data.accentColor,text=filler2,font=font)
    data.startButton.draw(canvas)

#take a photo screen
def drawTakeAPhotoScreen(canvas):
    text="Take a Photo"
    font="Helvetica 90 bold"
    canvas.create_text(data.width/2,data.height/8,text=text,font=font,
        fill="white")
    xoffset=80
    yoffset=188
    x2=720
    y2=680
    canvas.create_rectangle(xoffset,yoffset,x2,y2,fill=data.accentColor,width=7,
        outline=data.highlightColor)
    drawInstructionText(canvas)
    if data.photoIconClicked==False:
        drawPhotoIcon(canvas)
    else:
        drawClickedPhotoIcon(canvas)

def drawInstructionText(canvas):
    #draws take a photo instructions
    rule1="1. Hair pushed back"
    rule2="2. Face in the frame"
    rule3="3. Blank expression"
    rules=[rule1,rule2,rule3]
    color=data.accentColor
    spc=100
    font="Avenir 40"
    x0,y0=763, 229
    for i in xrange(len(rules)):
        canvas.create_text(x0,y0+spc*i,anchor="nw",font=font,text=rules[i],
            fill=data.highlightColor)

def drawClickedPhotoIcon(canvas):
    #inset clicked photo icon
    img=ImageTk.PhotoImage(file="clickedcamera.gif")
    data.imageLabel._image_cache=img
    x=940+5
    y=600+5
    canvas.create_image(x,y, anchor="c",image=img)

def drawPhotoIcon(canvas):
    #the button to take a photo
    img=ImageTk.PhotoImage(file="camera.gif")
    data.imageLabel._image_cache=img
    x=940
    y=600
    canvas.create_image(x,y, anchor="c",image=img)

#the screen for dragging the dots
def drawDotScreen(canvas):
    drawBackground(canvas)
    text="Drag the Dots"
    font="Helvetica 90 bold"
    color=data.highlightColor
    canvas.create_text(data.width/2,data.height/8,text=text,font=font,
        fill=color)
    xoffset=80
    yoffset=188
    x2=720
    y2=680
    canvas.create_rectangle(xoffset,yoffset,x2,y2,fill=data.accentColor,width=7,
        outline=data.highlightColor)
    drawDotInstructions(canvas)
    data.doneWithDotsButton.draw(canvas)

#draws the instrctions for the dot screen
def drawDotInstructions(canvas):
    text2="For the best results,"
    text3="match the example as"
    text4="precisely as you can."
    color=data.accentColor
    font="Avenir 35"
    x=70+880
    y0=575
    spacing=45
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
    x=90+715
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
    font1="Helvetica 50 "
    font2="Avenir 170 bold"
    y0=100
    spacing=125
    canvas.create_text(data.width/2,y0,anchor="c",text=text1,font=font1,
        fill=data.highlightColor)
    canvas.create_text(data.width/2,y0+spacing,anchor="c",text=text2,font=font2,
        fill=data.highlightColor)
    drawFaceShapeWriteup(canvas,writeup)
    data.seeBestGlassesButton.draw(canvas)

def drawFaceShapeWriteup(canvas,writeup):
    #puts each line of the writup on a different line
    spacing=48
    y0=380
    font="Avenir 35"
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
    font="Helvetica 90 bold"
    #finds the suggested frames for the person
    suggestedFrames=data.glassesType
    y0=96
    #tells the person their suggested frames
    canvas.create_text(data.width/2,y0,text=suggestedFrames,font=font,
        fill=data.highlightColor)
    drawGlassesImage(canvas)
    drawGlassesWriteup(canvas,writeup)
    data.browseFramesButton.draw(canvas)
    data.tryThemOnButton.draw(canvas)
    #data.resetButton.draw(canvas)

def drawGlassesImage(canvas):
    #draws the photo I found for the person's glasses recommendation
    filename="recphotos/"+data.faceShape+".gif"
    img=ImageTk.PhotoImage(file=filename)
    data.imageLabel._image_cache=img
    x=75
    y=195
    canvas.create_image(x,y,anchor="nw",image=img)

def drawGlassesWriteup(canvas,writeup):
    #puts each line of my writeup on a different line
    font="Avenir 35"
    color=data.accentColor
    spacing=48
    y0=185
    x0=665
    linecounter=0
    for i in xrange(len(writeup)):
        line=writeup[i]
        canvas.create_text(x0,y0+linecounter*spacing,anchor="nw",fill=color,
        font=font,text=line)
        linecounter+=1

def drawBrowseFramesPageText(canvas):
    font="Avenir 33 bold"
    text="Page "+str(data.pageNumber)+" of "+str(data.totalPages)
    y0=data.height-90
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

def drawOtherGlassesPairs(canvas):
    y0=170
    filename="glassespics/all"+data.faceShape+".gif"
    #glassespics/alloval.gif
    img=ImageTk.PhotoImage(file=filename)
    data.imageLabel3._image_cache=img
    x=915
    canvas.create_image(x,y0,anchor="nw",image=img)
    drawSelectedPair(canvas)

def drawSelectedPair(canvas):
    #highlights the pair that's selected 
    x0=915
    x1=1145
    #the boundaries for where the rectangle should go
    ya0,ya1=170,273
    yb0,yb1=300,410
    yc0,yc1=432,547
    yd0,yd1=575,687
    color=data.accentColor
    #draws rectangle based on which pair should be highlighted
    if data.glassesPair==0:
        canvas.create_rectangle(x0,ya0,x1,ya1,fill=None,width=10,outline=color)
    elif data.glassesPair==1:
        canvas.create_rectangle(x0,yb0,x1,yb1,fill=None,width=10,outline=color)
    elif data.glassesPair==2:
        canvas.create_rectangle(x0,yc0,x1,yc1,fill=None,width=10,outline=color)
    elif data.glassesPair==3:
        canvas.create_rectangle(x0,yd0,x1,yd1,fill=None,width=10,outline=color)

def drawPlayIcon(canvas):
    if data.shadedPlayButton==False: #the regular play button gets drawn
        img=ImageTk.PhotoImage(file="play.gif")
        data.imageLabel2._image_cache=img
        x=370
        y=645
        canvas.create_image(x,y,anchor="nw",image=img)
    else: #the clicked play button gets drawn
        img=ImageTk.PhotoImage(file="clickplay.gif")
        data.imageLabel2._image_cache=img
        x=370+5
        y=645+5
        canvas.create_image(x,y,anchor="nw",image=img)

def drawPauseIcon(canvas):
    if data.pausedTryOn==True:
        drawPlayIcon(canvas) #if it's paused, do the play icon
    elif data.cameraClickedTryOn==True:
        drawClickedCameraButton(canvas)  #clicked if it's clicked
    else:  #draws the camera icon
        img=ImageTk.PhotoImage(file="camera.gif")
        data.imageLabel2._image_cache=img
        x=370
        y=645
        canvas.create_image(x,y,anchor="nw",image=img)

def drawClickedCameraButton(canvas): #draws clicked version of camera icon
    img=ImageTk.PhotoImage(file="clickedcamera.gif")
    data.imageLabel2._image_cache=img
    x=370+5
    y=645+5
    canvas.create_image(x,y,anchor="nw",image=img)

def drawTryThemOnScreen(canvas): #draws the try them on screen
    text=data.glassesType    
    font="Helvetica 80 bold"
    y0=80
    canvas.create_text(data.width/2,y0,anchor="c",text=text,
        font=font,fill=data.highlightColor)
    x0=50
    x1=data.width-x0-300
    y0=150
    y1=data.height-185
    canvas.create_rectangle(x0,y0,x1,y1,fill=data.accentColor,width=7,
        outline=data.highlightColor)
    data.tryThemOnBackButton.draw(canvas)
    drawSelectedPair(canvas)
    drawPauseIcon(canvas)

def drawTryOnFrame(canvas,img):
    #draws the image of the try them on screen
    x=50+20
    y=150+20
    canvas.create_image(x,y,anchor="nw",image=img)
    if data.pausedTryOn==True: #if it's paused, do the "picture saved" thing
        text="Picture Saved"
        color=data.accentColor
        fontColor=data.backgroundColor
        font="Avenir 24 bold"
        x1=data.width-350
        x0=x1-180
        y1=data.height-185
        y0=y1-60
        canvas.create_rectangle(x0,y0,x1,y1,fill=color,width=7,outline=
            data.highlightColor)
        canvas.create_text((x0+x1)/2,(y0+y1)/2,fill=data.backgroundColor,
            anchor="c",font=font,text=text)

def drawGlassesPairs(canvas):
    #draws every glasses pair for the pages in the browse frames feature
    for glassesPair in data.glassesList:
        glassesPair.draw(canvas)

def drawBrowseFramesScreen(canvas):
    #the screen for searching through all of the glasses frames
    text="Recommended Frames"
    font="Helvetica 70 bold"
    y0=96
    canvas.create_text(data.width/2,y0,anchor="c",text=text,
        font=font,fill=data.highlightColor)
    x0=80
    x1=data.width-x0
    y0=165
    y1=data.height-150
    canvas.create_rectangle(x0,y0,x1,y1,fill=data.accentColor,width=0)
    data.browseFramesBackButton.draw(canvas)
    drawBrowseFramesPageText(canvas)
    drawGlassesPairs(canvas)

def doDotDrawings(canvas):
    #draws the dot screen and the dots on top of it
    drawDotScreen(canvas)
    drawFrame(canvas,data.pauseImg)
    for dot in data.dots:
        dot.draw(canvas)
    for i in xrange(1,len(data.dots)):
        data.dots[i].connect(data.dots[i-1],canvas,data.clickedDot)
    data.dots[0].connect(data.dots[-1],canvas,data.clickedDot)  
    data.dots[1].connect(data.dots[5],canvas,data.clickedDot)
    data.dots[2].connect(data.dots[4],canvas,data.clickedDot)

def drawAll(canvas):
    canvas.delete(ALL) #important lolz
    drawBackground(canvas) 
    if data.showBestGlasses==True: drawBestGlassesScreen(canvas) 
    elif data.browseFrames==True: drawBrowseFramesScreen(canvas)
    elif data.tryThemOn==True:
        drawTryThemOnScreen(canvas) #draws screens based on where they belong
        if data.pausedTryOn==False: img=updateTryOnImage()
        else: img=data.pausedTryOnImage #pauses if necessary
        drawTryOnFrame(canvas,img)  #does try on stuff
        drawOtherGlassesPairs(canvas)       
    elif data.start==False: drawStartScreen(canvas) #draws start stuff
    else:
        if data.pause==False and data.takeAPhoto==True: #take a photo screen
            drawTakeAPhotoScreen(canvas)
            drawFrame(canvas,data.currImg)
        elif data.faceShapeInfo==True: drawFaceShapeScreen(canvas)
        else: doDotDrawings(canvas)


###########################################################
################ CSV STUFF FOR BROWSE #####################
###########################################################

def csvToGlassesDisplayObjects():
    filename="Glasses.csv" #reads in the glasses
    data.glassesForRound, data.glassesForSquare=[], []
    data.glassesForOval, data.glassesForHeart=[], []
    with open(filename, "rt") as f:
        for pairOfGlasses in csv.DictReader(f):
            name=pairOfGlasses["Name"] #sets up a new object
            shape=pairOfGlasses["Shape"]
            price=pairOfGlasses["Price"]
            image=pairOfGlasses["Image"]
            brand=pairOfGlasses["Brand"]
            link=pairOfGlasses["Link"]
            newPair=GlassesDisplay(name,shape,price,image,brand,link)
            if newPair.shape=="Rectangular": #makes four different lists
                data.glassesForRound.append(newPair)
            elif newPair.shape=="Square":
                data.glassesForOval.append(newPair)
            elif newPair.shape=="Round":
                data.glassesForSquare.append(newPair)
            else: data.glassesForHeart.append(newPair) 
    giveGlassesDisplayObjectsPositionsAndPageNumbers(data.glassesForRound)
    giveGlassesDisplayObjectsPositionsAndPageNumbers(data.glassesForSquare)
    giveGlassesDisplayObjectsPositionsAndPageNumbers(data.glassesForOval)
    giveGlassesDisplayObjectsPositionsAndPageNumbers(data.glassesForHeart)

def giveGlassesDisplayObjectsPositionsAndPageNumbers(glassesList):
    #gives each pair a position on the page, 1 through 4, and a page number.
    data.numSpots=4
    counter=0
    for i in xrange(1,data.totalPages+1):
        for j in xrange(1,data.numSpots+1):
            glassesList[counter].pageNumber=i
            glassesList[counter].position=j
            counter+=1


###########################################################
################ OPENCV STUFF FOR TRY-ON ##################
###########################################################

#adapted from this: http://fideloper.com/facial-detection
def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, 
        minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def putOnGlasses(frame):
    scale=data.glassesScale #places the glasses on the user's face
    filename="glassespics/"+data.faceShape+str(data.glassesPair)+".png"
    #filename="glassespics/oval4.png"
    glasses=cv2.imread(filename,-1)
    glasses=cv2.resize(glasses,(0,0),fx=scale,fy=scale)
    w, h=glasses.shape[1], glasses.shape[0]
    y0=data.glassesy-float(h)/2
    y1=data.glassesy+float(h)/2
    x0=data.glassesx-float(w)/2
    x1=data.glassesx+float(w)/2
    glasses=-glasses
    for c in xrange(0,3):
        frameROI=(frame[y0:y1,x0:x1,c])
        try: #if it doesn't work, don't do anything or it crashes
            aBigNumber=500 #opencv image manipulation and transparency stuff
            newFrameROI=(-glasses[:,:,c]*(glasses[:,:,2]/aBigNumber)+frameROI*
                    (1.0 - glasses[:,:,c]/255.0))
            (frame[y0:y1,x0:x1,c])=newFrameROI
        except: frame=frame
    return frame

def getTwoEyes(eyerects):
    #finds the two biggest eyes in the frame
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

def getBiggestFace(facerects):
    #finds the biggest face in the frame
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

def getEyeXAndY(frame):
    #gets the x and y locations of the glasses
    finalX,finalY=0,0
    if data.frameCounter%10==0:
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyerects=detect(gray,data.eyeCascade)
        twoEyes=getTwoEyes(eyerects)
        if twoEyes[0]==None or twoEyes[1]==None: 
            return data.glassesx,data.glassesy
        x01,y01,x02,y02=twoEyes[0]
        x11,y11,x12,y12=twoEyes[1]
        movement=30
        finalX=((x01+x02)/2+(x11+x12)/2)/2 #middle of the eyes
        finalY=((y01+y02)/2+(y11+y12)/2)/2 #middle of the eyes
        smoothFactor=15 #smooths things out so it's not jumpy
        if abs(finalX-data.glassesx)<smoothFactor: finalX=data.glassesx
        if abs(finalY-data.glassesy)<smoothFactor:finalY=data.glassesy
    if finalX!=0 and finalY!=0: return finalX,finalY #returns middle of eyes
    else: return data.glassesX,data.glassesY #don't move if there's no eyes

def getGlassesScale(frame):
    scale=1 #don't resize by anything
    if data.frameCounter%10==0: #do every so many frames so it's faster
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        facerects=detect(gray,data.faceCascade)
        if len(facerects)==0: return 1
        rect=getBiggestFace(facerects)
        x0,y0,x1,y1=rect
        faceWidth=abs(x1-x0)
        #below formula calculated using my desired values and using a best fit 
        #linear regression
        scale=round(0.003*faceWidth-0.3,1)
    data.frameCounter+=1
    return scale

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
    else: 
        #if no face is found, it guesses
        guessx0=170
        guessy0=100
        guessx1=240
        guessy1=230
        return (guessx0,guessy0,guessx1,guessy1)

def updateTryOnImage(): #gets new frame from webcam feed every time it's called
    cap=cv2.VideoCapture(0)
    width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    ret,img=cap.read()
    frame=cv2.flip(img,1)
    data.frameCounter=0
    eyes="haarcascades/haarcascade_eye.xml"
    face="haarcascades/haarcascade_frontalface_alt.xml"
    data.eyeCascade=cv2.CascadeClassifier(eyes)
    data.faceCascade=cv2.CascadeClassifier(face)
    data.glassesx,data.glassesy=getEyeXAndY(frame)
    data.glassesScale=getGlassesScale(frame)
    frame=putOnGlasses(frame) 
    frame=cv2.resize(frame,(0,0),fx=0.59,fy=0.59)
    data.savedImage=frame
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img=Image.fromarray(cv2image)
    data.firstFrame=False
    tkImg=ImageTk.PhotoImage(image=img) #converts to tkinter image
    data.pausedTryOnImage=tkImg
    data.imageLabel._image_cache=tkImg
    data.frameCounter+=1
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
    #continually updates the entire screen and draws all
    img = updateImage()
    if data.pause==True: #checks for paused images
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
    framerate=5
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
    data.faceShape=None
    csvToGlassesDisplayObjects()

def storePhaseBooleans():
    data.start=False #hasn't started yet
    data.clicked=False #button isn't clicked
    data.showBestGlasses=False #it isn't showing best glasses screen
    data.doneWithDots=False #it isn't done with the dots screen
    data.pauseImg=None #there is no paused picture available
    data.faceShapeInfo=False #not displaying info about faceshape
    data.takeAPhoto=False #not displaying take a photo screen
    data.tryThemOn=False #person isn't trying glasses on
    data.browseFrames=False #person isn't browsing frames
    data.photoIconClicked=False #photo icon not clicked
    data.cameraClickedTryOn=False
    data.pausedTryOn=False
    data.clickedDot=None
    data.shadedPlayButton=False
    data.draggingDots=False 
    data.ableToClick=False
    data.canSeeBestGlasses=True #restrictions based on what part of program
    data.browseFramesCantBeClicked=False
    data.glassesType=None

def makeButtons(): #makes every button :)
    makeStartButton()
    makeDoneWithDotsButton()
    makeTryThemOnBackButton()
    makeBrowseFramesBackButton()
    makeSeeBestGlassesButton()
    makeBrowseFramesButton()
    makeTryThemOnButton()
    #makeResetButton()

def makeImageLabels(root):
    #you need an image label for every image per screen and one of my screens
    #displays four images
    data.imageLabel=tk.Label(root)
    data.imageLabel.pack()
    data.imageLabel2=tk.Label(root)
    data.imageLabel2.pack()
    data.imageLabel3=tk.Label(root)
    data.imageLabel3.pack()
    data.imageLabel4=tk.Label(root)
    data.imageLabel4.pack()

def initTryOnData():
    #there is a lot of data used in my try on function idk man
    data.glassesImgW=None
    data.glassesImgH=None
    width = int(data.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    height = int(data.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    data.frameCounter=0
    data.prevHorizontalDistances,data.prevVerticalDistances=None,None
    data.glasses=None
    data.glassesScale=1
    data.glassesTheta=0
    eyes="haarcascades/haarcascade_eye.xml"
    face="haarcascades/haarcascade_frontalface_alt.xml"
    data.eyeCascade=cv2.CascadeClassifier(eyes)
    data.faceCascade=cv2.CascadeClassifier(face)
    data.glassesx,data.glassesy=width/2,height/2
    data.firstFrame=True
    data.numPhotosTaken=0
    data.glassesPair=0
    data.tryOnImage=None
    data.frameCounter=0


def run():
    root=tk.Tk() #where it all begins :')
    root.wm_title("FourEyes")
    global data 
    data=Struct()
    resetData() 
    storePhaseBooleans() #tells us the phase in the program we're at
    makeButtons()
    initTryOnData()
    canvas=Canvas(root,width=data.width,height=data.height)
    canvas.bind("<Button-1>",onMouseDown)
    canvas.bind("<B1-Motion>",clickAndDrag)
    canvas.bind("<ButtonRelease-1>",onMouseUp)
    canvas.pack()
    canvas.after(0,func=lambda:updateAll(canvas)) #continually updates 
    makeImageLabels(root)
    drawBackground(canvas)
    root.mainloop()

run()