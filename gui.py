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
import numpy as np
import threading
import Queue

from MySocket import ClientSocket

from sys import getsizeof
from time import sleep
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
    parent.wm_protocol ("WM_DELETE_WINDOW", self.onClose)
    self.windowSize = {'width': 640, 'height': 480}
    self.parent = parent
    #self.pack_propagate(1) # Experimental, comment and uncomment to check the behavior of the UI
    self.buildUI(parent) 
    self.parent.config(menu=self.menubar)
    self.queue = Queue.Queue()
    self.processQueue()
    return

  def onClose(self):
    print '[O] Terminating App thread, destroying GUI'
    self.parent.destroy()
    self.parent.quit()
    detect.stop = True
    capture.stop = True

  def buildUI(self, root):
    print '[>] Creating UI ...'
    self.parent.title('Logo detection')
    #self.pack() # Experimental, comment and uncomment to check the behavior of the UI

    self.menubar = Menu(root)
    self.filemenu = Menu(self.menubar, tearoff=0)
    self.filemenu.add_command(label='Submenu 1')
    self.filemenu.add_command(label='Submenu 2')
    self.filemenu.add_command(label='Submenu 3')
    self.filemenu.add_separator()
    self.filemenu.add_command(label='Close', command=self.parent.quit)
    self.menubar.add_cascade(label='Menu 1', menu=self.filemenu)

    self.canvasContainer = Frame(self.parent).grid(row=0, column=0)
    self.videoCanvas = Canvas(self.canvasContainer, width=self.windowSize['width'], height=self.windowSize['height'])
    self.videoCanvas.pack(side=LEFT, padx=5,pady=5)
    print '[O] UI ready ...'
    return

  def drawDetectionZone(self):
    x1, y1, h, w = calculateROI((self.windowSize['height'], self.windowSize['width'], None))

    x2, y2 = x1 + w, y1 + h

    self.videoCanvas.create_rectangle(x1, y1, x2, y2, width=3.0, dash=(4,8))
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
      #print "[>] Processing a job (%s) ..." % (message['description'])
      self.loadFrame(message["frame"]);
    except Exception, e:
      print "[X] No job on App queue %s" % (e)
    self.parent.after(100, self.processQueue)
    return


# ==========================================================================
# Detection
#
#
# ==========================================================================
class Detection(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.queue = Queue.Queue()
    self.state = None
    self.stop = False

  def encode(self, message):
    eSTR = message.tostring()
    return eSTR

  def decode(self, message):
    dPIL = Image.fromstring('RGB', (350, 350), message, 'raw', 'BGR')
    dCV = np.array(dPIL)
    dCV = cv.cvtColor(dCV, cv.COLOR_RGB2BGR)
    return dCV, dPIL

  def detect(self, frame):
    if(self.state == 'idle'):
      message = self.encode(frame)
      self.state = 'busy'
      self.queue.put(message)
    return

  def processQueue(self, s):
    try:
      message = self.queue.get(0)
      print '[>] Sending frame to detection server (%d bytes)...' % (getsizeof(message))
      s.send(message)
      s.send('END')
      data = s.receive()
      if(data):
        print data
      self.state = 'idle'
    except Exception, e:
      print "[X] No job on Detection queue %s" % (e)
    return

  def run(self):
    self.state = 'idle'

    s = ClientSocket()
    s.connect()

    while(True):
      self.processQueue(s)
      sleep(1.0)
      if(self.stop):
        break

    s.send('CLOSEEND')
    s.close()
    print '[!] Terminating Detection thread'
    return


# ==========================================================================
# Capture Class
#
# Prepares the different ways to get the input data 
# Reads a frame from webcam
# Convert the frames from OpenCV to PIL images
# 
# ==========================================================================
class Capture(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.capture = None
    self.frame = None
    self.cvFrame = None
    self.roi = None
    self.stop = False
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
    self.frame = cv2pil(self.cvFrame)
    self.roi = getROI(self.cvFrame)
    return

  def run(self):
    self.capture = cv.VideoCapture(0) # Uncomment to capture from webcam

    while True:
      self.getFrame()
      if(self.frame):
        detect.detect(self.roi)
        app.queue.put({'description': 'Update frame', 'frame': self.frame})
        sleep(0.1)
      if(self.stop):
        break

    print '[!] Terminating Capture thread'
    return


# ==========================================================================
# cv2pil
#
# Convert the frames from OpenCV to PIL images
# 
# ==========================================================================
def cv2pil(frame):
  h, w, d = frame.shape
  f = Image.fromstring('RGB', (w,h), frame.tostring(), 'raw','BGR')
  return f

# ==========================================================================
# calculateROI
#
# TODO
#
# ==========================================================================
def calculateROI(im):
  fh, fw, fd = im.shape if(isinstance(im, np.ndarray)) else im
  bh, bw = (350, 350)
  x = (fw - bw)/2
  y = (fh - bh)/2
  return x, y, bh, bw

# ==========================================================================
# getROI
#
# TODO
#
# ==========================================================================
def getROI(im):
  x, y, bh, bw = calculateROI(im)
  roi = im[y:y+bh, x:x+bw]
  return roi

# ==========================================================================
# Main
# ==========================================================================
if(__name__ == '__main__'):
  root = Tk()
  app = App(root)
  detect = Detection()
  detect.start()
  capture = Capture()
  capture.start()
  root.mainloop()
