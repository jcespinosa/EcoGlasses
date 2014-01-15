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

from Tkinter import *
from PIL import Image, ImageTk
from time import time

import LogoDetection

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
    self.pack_propagate(1)
    self.buildUI(parent) 
    self.parent.config(menu=self.menubar)
    self.size = (640,480)
    return
        
  def buildUI(self, root):
    self.parent.title("Logo detection")
    self.pack()

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

# ==========================================================================
# Detection Class
#
# Prepares the different ways to get the input data 
# Reads a frame from webcam, video file or image
# Convert the frames from OpenCV to PIL images
# 
# ==========================================================================
class Detection():
  def __init__(self):
    self.cameraIndex = 0
    self.capture = cv.VideoCapture(self.cameraIndex) # Uncomment to capture the webcam
    #self.capture = cv.VideoCapture("/path/to/video/file.abc") # Uncomment to capture a video file
    self.frame = None
    self.cvFrame = None
    return

  def getFrame(self):
    self.cameraIndex = 0

    # Comment this block if you are going to read a video file
    c = cv.waitKey(10)
    if(c == "n"):
      self.cameraIndex += 1
      self.capture = cv.VideoCapture(self.cameraIndex)
      frame = None
      if not self.capture:
        self.cameraIndex = 0
        self.capture = cv.VideoCapture(self.cameraIndex)
        frame = None
    # ======================================================

    dump, self.cvFrame = self.capture.read()  # Uncomment if you are reading data from webcam or video file
    #self.cvFrame = cv.flip(self.cvFrame,0) # Uncomment to flip the frame vertically
    #self.cvFrame = cv.flip(self.cvFrame,1) # Uncomment to flip the frame horizonally
    #self.cvFrame = cv.imread("./test/sign3.jpg") # Uncomment if you are reading an image
    self.frame = self.cv2pil(self.cvFrame)

    return self.cvFrame, self.frame

  def cv2pil(self, frame):
    h,w,n = frame.shape
    f = Image.fromstring("RGB", (w,h), frame.tostring(),'raw','BGR')
    return f

  def debug(self, frames, colors, regions): # Shows auxiliary windows from OpenCV
    for color in colors:
      cv.imshow(color, colors[color])
    for frame in frames:
      cv.imshow(frame, frames[frame])
    for region in regions:
      for roi in regions[region]:
        cv.imshow("roi", roi["roi"])
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
  detect = Detection()
  LogoDetection.loadSURF()

  framerate, start = 0, time()

  for i in range(10):
    cvFrame, frame = detect.getFrame()

  while True:
    cvFrame, frame = detect.getFrame()
    if(frame):
      frames, colors, regions = LogoDetection.run(cvFrame)
      frame = detect.cv2pil(frames["original"])
      app.loadFrame(frame)
      #detect.debug(frames, colors, regions)
    root.update()

    framerate += 1
    if(time() - start) >= 1.0:
      #print framerate
      framerate, start = 0, time()
  return

if(__name__=="__main__"):
    main()

