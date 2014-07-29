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
from sys import argv, path
from traceback import print_exc

import Matcher
from dbDriver import get
from FeatureExtraction import FeatureExtractor
from MySocket import ServerSocket


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
    message = dumps(message, 2)   
    return message

  def decode(self, message):
    try:
      message = loads(message)
    except Exception, e:
      message = None
      print "[X] Error decoding the message from the client %s." % (e)
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
  state, logoName, matches, image = res

  result = {
    'state': state,
    'data': None
  }

  if(state == 0):
    result['data'] = None
  elif(state == 1):
    result['data'] = get(logoName)
    frames['final'] = image
  else:
    result['data'] = None

  print result

  return result, frames


# ======================================================================
# loadFeatures
#
# TODO
#
# ======================================================================
def match(frames, matcherMethod):
  if(matcherMethod):
    frame = frames['temp'] if(matcherMethod != 'template') else frames['gray']
    try:
      res = Matcher.runMatcher(frame)
    except Exception, e:
      print '[X] Error calling matcher method: %s' % (e)
      print_exc()
      res = (2, None, 0, None)
  else:
    res = (2, None, 0, None)
  res, frames = processResult(res, frames)
  return res, frames


# ======================================================================
# preprocessFrame
#
# TODO
#
# ======================================================================
def preprocessFrame(frame):
  print '[>] Preprocessing frame ...'
  frames = {
    'original': frame,
    'final': frame,
    'blank': np.zeros(frame.shape, dtype=np.uint8),
    'gray': cv.cvtColor(frame, cv.COLOR_BGR2GRAY),
    'hsv': cv.cvtColor(frame, cv.COLOR_BGR2HSV),
    'temp': FeatureExtractor(cvImage=frame)
  }
  #frames['blur'] = smooth(frame, mat=(15,15))
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
    while(True):
      print '[>] Waiting for a frame ...'

      frame = s.receive()

      if(frame is None or 'CLOSE' in frame):
        break

      frames = preprocessFrame(frame)
      result, frames = match(frames, matcherMethod)
      cv.imshow('Client Frame', frames['final'])
      cv.waitKey(100)
      s.send(result)

    s.close()
    cv.destroyWindow('Client Frame')
    for a in range(10):
      cv.waitKey(100)
    
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
  print "[!] Using default matcher method %s." % (matcherMethod)

  Matcher.configureMatcher(matcherMethod)
  dispatch(matcherMethod)

  return


if(__name__ == '__main__'):
  main()
