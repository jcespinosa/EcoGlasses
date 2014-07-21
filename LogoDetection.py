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

import dbDriver

from json import dumps
from PIL import Image
from sys import argv, path
from traceback import print_exc

from FeatureExtraction import FeatureExtractor, loadFeatures, loadTemplates
from MySocket import ServerSocket

path.append('./lib/')

#from KNN import run as runKNN
#from TemplateMatcher import run as runTemplateMatcher
from FlannMatcher import run as runFlannMatcher
from BFMatcher import run as runBFMatcher


LOGOS = dict()

# ======================================================================
# Server
#
#
# ======================================================================
class Server():
  def __init__(self):
    self.socket = ServerSocket(port=9999)
    self.socket.bind()

  def encode(self, message):
    try:
      message = dumps(message)
    except Exception, e:
      print e
      message = '{"state":2,"data": None}'
    return message

  def decode(self, message):
    try:
      dPIL = Image.fromstring('RGB', (350, 350), message, 'raw','BGR')
      dCV = np.array(dPIL)
      dCV = cv.cvtColor(dCV, cv.COLOR_RGB2BGR)
    except Exception, e:
      print '[X] Error decoding message: %s.' % (e)
      dCV, dPIL = None, None
    return dCV, dPIL

  def send(self, message):
    message = self.encode(message)
    self.socket.send(message)
    return

  def receive(self):
    message = self.socket.receive()
    if('CLOSE' in message):
      return False
    message = self.decode(message)
    return message

  def wait(self):
    self.socket.wait()
    return

  def close(self):
    print '\n[O] Client connection closed.\n'
    self.socket.closeClient()
    #self.socket.close()
    return


# ======================================================================
# processResult
#
# TODO
#
# ======================================================================
def processResult(res, frames):
  result = {
    'state': 0,
    'data': None
  }
  if(res):
    state, logoName, image = res
    frames['final'] = image
    result = {
      'state': 1,
      'data': dbDriver.get(logoName)
    }
    print result
  return result, frames

# ======================================================================
# loadFeatures
#
# TODO
#
# ======================================================================
MATCHERS = {
  'bf': runBFMatcher,
  'flann': runFlannMatcher
}
#  'knn': runKNN,
#  'svm': runSVM,
#  'template': runTemplateMatcher
#}

def match(frames, method):
  if(method):
    frame = frames['temp'] if(method != 'template') else frames['gray']
    try:
      res = MATCHERS[method](frame, LOGOS)
    except Exception, e:
      print_exc()
      print '[X] Error calling matcher method: %s' % (e)
      res = False
  else:
    res = False
  res, frames = processResult(res, frames)
  return frames, res

# ======================================================================
# preprocessFrame
#
# TODO
#
# ======================================================================
def preprocessFrame(frame):
  print '[>] Preprocessing frame ...'
  frames = {'original': frame, 'final': frame}
  frames['blank'] = np.zeros(frame.shape, dtype=np.uint8)
  frames['gray'] = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  #frames['blur'] = smooth(frame, mat=(15,15))
  frames['hsv'] = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
  frames['temp'] = FeatureExtractor(cvImage=frame)
  print '[O] Frame is ready ...'
  return frames

# ======================================================================
# preprocessFrame
#
# TODO
#
# ======================================================================
def dispatch(matcherMethod):
  s = Server()
  
  while(True):
    s.wait()
    cv.namedWindow('Client Frame')
    cv.waitKey(30)
    while(True):
      print '[>] Waiting for a frame ...'

      data = s.receive()
      if(not data):
        break
      dCV, dPIL = data

      if(dCV is not None):
        frames = preprocessFrame(dCV)
        frames, result = match(frames, matcherMethod)
        cv.imshow('Client Frame', frames['final'])
        cv.waitKey(30)
      else:
        result = processResult(False)
      s.send(result)

    s.close()
    cv.destroyWindow('Client Frame')
    cv.waitKey(30)
    cv.imshow('Client Frame', frames['blank'])
    

  return

# ======================================================================
# Main
# ======================================================================
def main():
  matcherMethod = 'bf'

  try:
    matcherMethod = argv[1]
  except Exception, e:
    print '[!] One argument expected (matcherMethod [bf, flann, template, svm, knn]).'
  print "[!] Using matcher method %s." % (matcherMethod)

  global LOGOS
  if(matcherMethod == 'template'):
    print '[>] Loading templates ...'
    LOGOS = loadTemplates()
  else:
    print '[>] Loading features ...'
    LOGOS = loadFeatures()
  print '[O] Loaded.\n'

  dispatch(matcherMethod)

  return

if(__name__ == '__main__'):
  main()
