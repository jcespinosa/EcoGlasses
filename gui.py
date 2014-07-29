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

from cPickle import dumps, loads
from time import sleep
from Tkinter import *
from traceback import print_exc
from threading import Thread
from PIL import Image, ImageTk
from sys import argv
from Queue import Queue

from MySocket import ClientSocket

CAM_ID = 0


# ======================================================================
# App Class
#
# Builds and draws all the GUI
# Load each processed frame
#
# ======================================================================
class App(Frame):
  def __init__(self, parent, width, height):
    Frame.__init__(self, parent)
    parent.wm_protocol('WM_DELETE_WINDOW', self.onClose)
    self.windowSize = {'width': width, 'height': height}
    self.parent = parent
    self.buildUI() 
    self.queue = Queue()
    self.processQueue()
    return

  def onClose(self):
    print '[!] Terminating App thread, destroying GUI.'
    detect.stop = True
    capture.stop = True
    self.parent.destroy()
    self.parent.quit()

  def buildUI(self):
    print '[>] Creating UI ...'
    if(debug):
      print '[!] Debug mode.'

    self.parent.title('EcoGlasses debug window')

    self.menubar = Menu(self.parent)
    self.filemenu = Menu(self.menubar, tearoff=0)
    self.filemenu.add_command(label='Reset', command=detect.reset)
    self.filemenu.add_command(label='Close', command=self.onClose)
    self.menubar.add_cascade(label='Menu 1', menu=self.filemenu)
    self.parent.config(menu=self.menubar)

    self.outlineColor, self.canvasTextColor, self.backgroundColor = 'black', 'black', 'white'
    self.message = 'Esperando conexion con servidor ...'
    self.canvasText = ''
    self.text = 'Waiting for server data ...'

    if(debug):
      self.canvasFrame = Frame(self.parent)#.grid(row=0, column=0)
      self.canvasContainer = LabelFrame(self.canvasFrame, text="Capture", width=self.windowSize['width'], height=self.windowSize['height'])
      self.videoCanvas = Canvas(self.canvasContainer, width=self.windowSize['width'], height=self.windowSize['height'], bg=self.backgroundColor)
      self.videoCanvas.pack()
      self.canvasFrame.pack(side=LEFT)
      self.canvasContainer.pack(expand="yes", padx=5, pady=5)

      self.infoFrame = Frame(self.parent)#.grid(row=0, column=1)
      self.infoContainer = LabelFrame(self.infoFrame, text="Product information", padx=5, pady=5, width=self.windowSize['width']/2, height=self.windowSize['height'])
      self.infoText = Text(self.infoContainer, width=50, height=29, background='white')
      self.resetButton = Button(self.infoFrame, text="Reset detection", command=detect.reset)
      self.infoFrame.pack(side=LEFT)
      self.infoContainer.pack(expand="yes", padx=5, pady=5)
      self.infoText.pack()
      self.resetButton.pack()

      self.infoText.insert(INSERT, self.text)
      self.canvasFontSize = 20
    else:
      self.canvasFrame = Frame(self.parent)#.grid(row=0, column=0)
      self.videoCanvas = Canvas(self.canvasFrame, width=self.windowSize['width'], height=self.windowSize['height'], bg=self.backgroundColor)
      self.videoCanvas.pack(expand="yes")
      self.canvasFrame.pack(side=LEFT)
      self.canvasFontSize = 45

    print '[O] UI ready.'
    return

  def updateWidgets(self):
    if(debug):
      self.infoText.delete('1.0', END)
      self.infoText.insert(INSERT, self.text)
    else:
      if(feedback):
        pass
      else:
        self.videoCanvas.delete('all')
      pass
    x1, y1, h, w = calculateROI((self.windowSize['height'], self.windowSize['width'], None))
    x2, y2 = x1 + w, y1 + h
    self.videoCanvas.create_rectangle(x1, y1, x2, y2, width=8.0, dash=(10,15), outline=self.outlineColor)
    self.videoCanvas.create_text(self.windowSize['width']/2, (self.windowSize['height']/2)+250, font=("Ubuntu", self.canvasFontSize), fill=self.canvasTextColor, text=self.message)
    self.videoCanvas.create_text(self.windowSize['width']/2, (self.windowSize['height']/2), font=("Ubuntu", self.canvasFontSize), fill=self.canvasTextColor, text=self.canvasText)
    self.videoCanvas.configure(bg=self.backgroundColor)
    return

  def loadFrame(self, frame):
    w, h = self.windowSize['width'], self.windowSize['height']
    try:
      self.frame = ImageTk.PhotoImage(frame)
      self.videoCanvas.delete('all')
      self.videoCanvas.configure(width=w, height=h)
      self.videoCanvas.create_image(w/2, h/2, image=self.frame)
    except Exception, e:
      print e      
    return

  def processTask(self, task):
    t = task['task']
    if(t == 0):
      self.loadFrame(task['frame']);
    elif(t == 1):
      self.outlineColor = task['color1']
      self.backgroundColor = task['color2']
    elif(t == 2):
      self.message = task['message']
      self.text = task['text']
      self.canvasText = task['text']
    else:
      pass
    self.updateWidgets()
    return

  def processQueue(self):
    if(self.queue.qsize() > 0):
      task = self.queue.get(0)
      self.processTask(task)
    print self.queue.qsize()
    self.parent.after(50, self.processQueue)
    return


# ======================================================================
# Client
#
#
# ======================================================================
class Client():
  def __init__(self):
    self.socket = ClientSocket()
    self.socket.connect()

  def encode(self, message):
    message = dumps(message, 2)
    return message

  def decode(self, message):
    try:
      message = loads(message)
    except Exception, e:
      message = None
      print "[X] Error decoding the message from the server %s." % (e)
    return message

  def send(self, message):
    message = self.encode(message)
    self.socket.send(message)
    return

  def receive(self):
    message = self.socket.receive()
    if(message):
      message = self.decode(message)
    else:
      message = None
    return message

  def close(self):
    print '\n[O] Closing connection with the server.\n'
    message = self.encode('CLOSE')
    self.socket.send(message)
    self.socket.close()
    return


# ======================================================================
# Detection
#
#
# ======================================================================
class Detection(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.frame = None
    self.state = None
    self.stop = False

  def reset(self):
    self.state = 'idle'
    #print "Reset"
    return

  def setFrame(self, frame):
    if(self.state == 'idle'):
      self.frame = frame
      self.state = 'busy'
    return

  def processResult(self, res):
    if(res):
      state = int(res['state'])
      if(state == 0):
        app.queue.put({'task': 1, 'color1': 'black', 'color2': 'white'})
        app.queue.put({'task': 2, 'message': 'Nada se ha detectado.', 'text': ''})
        self.reset()
      elif(state == 1):
        text = "Marca: %s\nProducto: %s\nHecho en: %s\nCodigo: %s\n"%(res['data']['name'],res['data']['product'],res['data']['madein'],res['data']['barcode'])
        message = "Se detecto %s"%(res['data']['name'])
        app.queue.put({'task': 1, 'color1': 'green', 'color2': 'green'})
        app.queue.put({'task': 2, 'message': message, 'text': text})
      else:
        app.queue.put({'task': 1, 'color1': 'red', 'color2': 'red'})
        app.queue.put({'task': 2, 'message': 'Ocurrio un error en la deteccion.', 'text': 'Error'})
        self.reset()
    return

  def sendFrame(self, s):
    if(self.frame is not None):
      print '[>] Sending frame to detection server ...'
      s.send(self.frame)
      self.frame = None
      result = s.receive()
      self.processResult(result)
    return

  def run(self):
    self.state = 'idle'

    s = Client()
    while(not self.stop):
      self.sendFrame(s)
      sleep(1.5)
    s.close()

    print '[!] Terminating Detection thread.'
    return


# ======================================================================
# Capture Class
#
# Reads a frame from webcam
# Convert the frames from OpenCV to PIL images
# 
# ======================================================================
class Capture(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.capture = None
    self.frame = None
    self.cvFrame = None
    self.roi = None
    self.stop = False
    return

  def getFrame(self):
    cameraIndex = CAM_ID

    c = cv.waitKey(100)
    if(c == 'n'):
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
    self.capture = cv.VideoCapture(CAM_ID)

    while(not self.stop):
      self.getFrame()
      if(self.frame):
        detect.setFrame(self.roi)
        app.queue.put({'task': 0, 'frame': self.frame})
        sleep(0.1)

    print '[!] Terminating Capture thread.'
    return


# ======================================================================
# cv2pil
#
# Convert the frames from OpenCV to PIL images
# 
# ======================================================================
def cv2pil(frame):
  h, w, d = frame.shape
  frame = Image.fromstring('RGB', (w,h), frame.tostring(), 'raw', 'BGR')
  return frame


# ======================================================================
# calculateROI
#
# TODO
#
# ======================================================================
def calculateROI(im):
  fh, fw, fd = im.shape if(isinstance(im, np.ndarray)) else im
  bh, bw = (350, 350)
  x = (fw - bw)/2
  y = (fh - bh)/2
  return x, y, bh, bw


# ======================================================================
# getROI
#
# TODO
#
# ======================================================================
def getROI(im):
  x, y, bh, bw = calculateROI(im)
  roi = im[y:y+bh, x:x+bw]
  return roi


# ======================================================================
# Main
# ======================================================================
if(__name__ == '__main__'):
  debug, feedback = False, False
  if(len(argv) > 1):
    debug = True if(argv[1] == '-d') else False
    feedback = True if(argv[1] == '-f') else False

  root = Tk()
  w, h = (640, 480)
  if(not debug):
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set() # <-- move focus to this widget
    root.bind("<Key>", lambda e: e.widget.quit())

  detect = Detection()
  detect.start()
  app = App(root, w, h)
  capture = Capture()
  capture.start()
  root.mainloop()
