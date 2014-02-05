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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.#
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
    self.parent = parent
    #self.pack_propagate(1) # Experimental, comment and uncomment to check the behavior of the UI
    self.buildUI(parent) 
    self.parent.config(menu=self.menubar)
    self.size = (640,480)
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
    self.videoCanvas = Canvas(self.canvasContainer, width=640, height=480)
    self.videoCanvas.pack(side=LEFT, padx=5,pady=5)

    self.infoContainer = Frame(self.parent).grid(row=0, column=1)
         
    return

  def loadFrame(self, frame):
    w,h = self.size
    try:
      self.frame = ImageTk.PhotoImage(frame)
      self.videoCanvas.delete("all")
      self.videoCanvas.configure(width=w, height=h)
      self.videoCanvas.create_image(w/2, h/2, image=self.frame)
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
    self.parent.after(100, self.processQueue)

# ==========================================================================
# Detection Class
#
# Prepares the different ways to get the input data 
# Reads a frame from webcam, video file or image
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

    # ======================================================
    # Comment this block if you are going to read a video file or image file
    c = cv.waitKey(10)
    if(c == "n"):
      cameraIndex += 1
      self.capture = cv.VideoCapture(cameraIndex)
      frame = None
      if not self.capture:
        cameraIndex = 0
        self.capture = cv.VideoCapture(cameraIndex)
        frame = None
    # ======================================================

    dump, self.cvFrame = self.capture.read()  # Uncomment if you are reading data from webcam or video file
    #self.cvFrame = cv.flip(self.cvFrame,0) # Uncomment to flip the frame vertically
    #self.cvFrame = cv.flip(self.cvFrame,1) # Uncomment to flip the frame horizonally
    self.frame = self.cv2pil(self.cvFrame)

    return self.cvFrame, self.frame

  def cv2pil(self, frame):
    h,w,n = frame.shape
    f = Image.fromstring("RGB", (w,h), frame.tostring(),'raw','BGR')
    return f

  def debug(self, frames): # Shows auxiliary windows from OpenCV
    for frame in frames:
      cv.imshow(frame, frames[frame])
    return

  def run(self):
    LogoDetection.loadSURF()
    self.capture = cv.VideoCapture(0) # Uncomment to capture from webcam

    #for i in range(10):
    #  self.getFrame()

    while True:
      self.getFrame()
      if(self.frame):
        frames = LogoDetection.run(self.cvFrame)
        frame = self.cv2pil(frames["original"])
        self.queue.put({"description": "Update frame", "frame":frame})
        #self.debug(frames)
      sleep(0.1)
      if(self.queue.qsize() > 5):
        break
    return

# ==========================================================================
# Main
#
# Initializes all the classes
# Loads the signal templates in memory
# Calculates the framerate
# Runs the signal detection algorithm
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
