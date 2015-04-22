#April 10: THIS IS PRETTY COOL 

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
    differentSizeRatio=1.3
    #checking if the forehead is significantly the widest part of the face
    return foreheadJawRatio>differentSizeRatio
def isOvalFace(faceDimensions):
    forehead,jaw,faceLength,faceWidth=faceDimensions
    #A face is oval shaped if the face is approx 1.5 times as long as 
    #it is wide or more
    lengthWidthRatio=1.0*faceLength/faceWidth
    idealOvalRatio=1.5
    return lengthWidthRatio>=idealOvalRatio
def isSquareFace(faceDimensions):
    forehead,jaw,faceLength,faceWidth=faceDimensions
    foreheadJawRatio=1.0*forehead/jaw
    idealSquareForeheadJawRatio=1.0
    return areSimilarRatios(foreheadJawRatio,idealSquareForeheadJawRatio)
def getFaceShape(faceDimensions):
    #heart is the most distinctive, if the forehead is the widest, that
    #person's face is definitely a heart. therefore, it gets checked first.
    if isHeartFace(faceDimensions)==True:
        return "heart"
    #after heart, oval is the next most distinctive. If the length is about 
    #1.5 times the width, it's an oval.
    elif isOvalFace(faceDimensions)==True:
        return "oval"
    #then comes square, with angular features and similar widths everywhere
    elif isSquareFace(faceDimensions)==True:
        return "square"
    #last remaining face shape
    else: return "round"
def getFaceDimensions(points):
    (ax,ay)=points[0]
    (bx,by)=points[1]
    (cx,cy)=points[2]
    (dx,dy)=points[3]
    (ex,ey)=points[4]
    (fx,fy)=points[5]
    foreheadWidth=((fx-bx)**2+(fy-by)**2)**0.5
    jawWidth=((ex-cx)**2+(ey-cy)**2)**0.5
    faceLength=((ax-dx)**2+(ay-dy)**2)**0.5
    faceWidth=(foreheadWidth+jawWidth)/2
    return (foreheadWidth,jawWidth,faceLength,faceWidth)
D=(384, 410)
A=(377, 121)
B=(469, 223)
F=(284, 229)
C=(454, 346)
E=(310, 353)
points=[A,B,C,D,E,F]
faceDimensions=getFaceDimensions(points)
faceShape=getFaceShape(faceDimensions)

print faceShape
