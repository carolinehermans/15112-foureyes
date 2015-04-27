import os
import csv

class GlassesDisplay(object):
    def __init__(self,name,price,image,brand,link):
        self.name=name
        self.price=price
        self.image="browseglasses/"+image
        self.brand=brand
        self.link=link
    def __repr__(self):
        result=("GlassesDisplay(name="+self.name+", price="+self.price+
            ", image="+self.image+", brand="+self.brand+", link="+self.link+")")
        return result



def csvToGlassesDisplayObjects():
    filename="Glasses.csv"
    allGlasses=[]
    with open(filename, "rt") as f:
        for pairOfGlasses in csv.DictReader(f):
            name=pairOfGlasses["Name"]
            price=pairOfGlasses["Price"]
            image=pairOfGlasses["Image"]
            brand=pairOfGlasses["Brand"]
            link=pairOfGlasses["Link"]
            newPair=GlassesDisplay(name,price,image,brand,link)
            allGlasses.append(newPair)
    return allGlasses




