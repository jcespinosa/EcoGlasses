#!/usr/bin/python

########################################################################
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# at your option) any later version.                                   #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>. #
########################################################################

import cv2 as cv
import LogoDetection
import threading
import Queue

from time import time, sleep
from Tkinter import *
from PIL import Image, ImageTk


# ==========================================================================
# App Class
#
# Builds and draws all the GUI
# Load each processed frame
#
# ==========================================================================
class App(Frame):
  def __init__(self, parent):
    Frame.__init__(self, parent)
    self.windowSize = {'width': 640, 'height': 480}
    self.parent = parent
    #self.pack_propagate(1) # Experimental, comment and uncomment to check the behavior of the UI
    self.buildUI(parent) 
    self.parent.config(menu=self.menubar)
    self.queue = Queue.Queue()
    self.processQueue()
    return
        
  def buildUI(self, root):
    self.parent.title("Logo detection")
    #self.pack() # Experimental, comment and uncomment to check the behavior of the UI

    self.menubar = Menu(root)
    self.filemenu = Menu(self.menubar, tearoff=0)
    self.filemenu.add_command(label="Submenu 1")
    self.filemenu.add_command(label="Submenu 2")
    self.filemenu.add_command(label="Submenu 3")
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Close", command=self.parent.quit)
    self.menubar.add_cascade(label="Menu 1", menu=self.filemenu)

    self.canvasContainer = Frame(self.parent).grid(row=0, column=0)
    self.videoCanvas = Canvas(self.canvasContainer, width=self.windowSize['width'], height=self.windowSize['height'])
    self.videoCanvas.pack(side=LEFT, padx=5,pady=5)
    return

  def drawDetectionZone(self):
    ww, wh = self.windowSize['width'], self.windowSize['height']
    dw, dh = (350, 350)

    x1 = (ww - dw)/2
    y1 = (wh - dh)/2
    x2 = x1 + dw
    y2 = y1 + dh

    self.videoCanvas.create_rectangle(x1, y1, x2, y2, width=3.0)
    return

  def loadFrame(self, frame):
    w, h = self.windowSize['width'], self.windowSize['height']
    try:
      self.frame = ImageTk.PhotoImage(frame)
      self.videoCanvas.delete("all")
      self.videoCanvas.configure(width=w, height=h)
      self.videoCanvas.create_image(w/2, h/2, image=self.frame)
      self.drawDetectionZone()
    except Exception, e:
      print e      
    return

  def processQueue(self):
    try:
      message = self.queue.get(0)
      print "[>] Processing a job %s"%(message["description"])
      self.loadFrame(message["frame"]);
    except Exception, e:
      print "[X] No job on the queue %s"%(e)
    self.parent.after(200, self.processQueue)
    return


# ==========================================================================
# Detection Class
#
# Prepares the different ways to get the input data 
# Reads a frame from webcam
# Convert the frames from OpenCV to PIL images
# 
# ==========================================================================
class Detection(threading.Thread):
  def __init__(self, queue):
    threading.Thread.__init__(self)
    self.capture = None
    self.frame = None
    self.cvFrame = None
    self.queue = queue
    return

  def getFrame(self):
    cameraIndex = 0

    c = cv.waitKey(10)
    if(c == "n"):
      cameraIndex += 1
      self.capture = cv.VideoCapture(cameraIndex)
      frame = None
      if not self.capture:
        cameraIndex = 0
        self.capture = cv.VideoCapture(cameraIndex)
        frame = None   

    dump, self.cvFrame = self.capture.read()
    #self.cvFrame = cv.flip(self.cvFrame, 0) # Uncomment to flip the frame vertically
    #self.cvFrame = cv.flip(self.cvFrame, 1) # Uncomment to flip the frame horizonally
    self.frame = self.cv2pil(self.cvFrame)
    return self.cvFrame, self.frame

  def cv2pil(self, frame):
    h, w, d = frame.shape
    f = Image.fromstring("RGB", (w,h), frame.tostring(),'raw','BGR')
    return f

  def run(self):
    LogoDetection.loadFeatures()
    self.capture = cv.VideoCapture(0) # Uncomment to capture from webcam

    while True:
      self.getFrame()
      if(self.frame):
        frames = LogoDetection.run(self.cvFrame)
        frame = self.cv2pil(frames['final'])
        self.queue.put({'description': 'Update frame', 'frame': frame})
      sleep(0.2)
      if(self.queue.qsize() > 5):
        break
    return


# ==========================================================================
# Main
#
#
# ==========================================================================
def main():
  root = Tk()
  app = App(root)
  detect = Detection(app.queue)
  detect.start()
  root.mainloop()
  
if(__name__=="__main__"):
    main()
