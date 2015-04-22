from Tkinter import *
import cv2
import PIL.Image
import PIL.ImageTk
import Tkinter as tk

def drawBackground(canvas):
    img=canvas.data.imgCapture
    image_label.configure(image=img)
    color="SlateBlue3"
    canvas.create_rectangle(0,0,canvas.data.width*2,canvas.data.height*5,fill=color,
        width=0)

def update_image(image_label, cv_capture):
    cv_image = cv_capture.read()[1]
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = PIL.Image.fromarray(cv_image)
    tk_image = PIL.ImageTk.PhotoImage(image=pil_image)
    canvas.data.imgCapture=tk_image
    drawBackground(canvas)
    #image_label.configure(image=tk_image)
    #image_label._image_cache = tk_image  # avoid garbage collection
    canvas.update()

def update_all(root, image_label, cv_capture):
    if root.quit_flag:
        root.destroy()  # this avoids the update event being in limbo
    else:
        update_image(image_label, cv_capture)
        root.after(10, func=lambda: update_all(root, image_label, cv_capture))

if __name__ == '__main__':
    cv_capture = cv2.VideoCapture()
    cv_capture.open(0)  # have to use whatever your camera id actually is
    cv_capture.set(3,1000)
    cv_capture.set(4,580)
    root = tk.Tk()
    width=1000
    height=200
    global canvas
    canvas=Canvas(root,width=width,height=height)
    canvas.pack()
    class Struct: pass
    canvas.data=Struct()
    canvas.data.width=width
    canvas.data.height=height
    setattr(canvas, 'quit_flag', False)
    image_label = tk.Label(master=root)  # the video will go here
    image_label.pack()
    root.after(0, func=lambda: update_all(canvas, image_label, cv_capture))
    root.mainloop()