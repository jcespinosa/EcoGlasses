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

import cPickle as pickle
import cv2 as cv
import numpy as np

from json import dumps, loads
from PIL import Image
from sys import argv, path

from FeatureDetection import FeatureDetector, loadKeypoints, PATHS
from MySocket import ServerSocket

path.append('./lib/')

from KNN import run as runKNN
#from SVM import run as runSVM
from TemplateMatcher import run as runTemplateMatcher
from FeatureMatcher import run as runFeatureMatcher


# Posible logos to be detected
LOGO_NAMES = ['kellogs', 'lala', 'quaker']
LOGOS = dict()


# ==========================================================================
# Server
#
#
# ==========================================================================
class Server():
  def __init__(self):
    self.socket = ServerSocket(port=9999)
    self.socket.bind()
    self.socket.wait()

  def encode(self, message):
    try:
      message = dumps(message) + '|END'
    except Exception, e:
      print e
      message = '{"state":2}|END'
    return message

  def decode(self, message):
    try:
      dPIL = Image.fromstring('RGB', (350, 350), message, 'raw','BGR')
      dCV = np.array(dPIL)
      dCV = cv.cvtColor(dCV, cv.COLOR_RGB2BGR)
    except Exception, e:
      print '[X] Error decoding message: %s' % (e)
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

  def close(self):
    self.socket.closeClient()
    self.socket.close()
    return


# ==========================================================================
# loadFeatures
#
# TODO
#
# ==========================================================================
def loadFeatures():
  global LOGOS, LOGO_NAMES

  for name in LOGO_NAMES:
    LOGOS[name] = list()
    count = 1
    while(True):
      path = '%s/%d'%(name, count)

      a, keypoints = loadKeypoints(PATHS['keypoints'] + path + '.kp')
      
      if(not keypoints):
        print "[!] Template for '%s' not found, the sequence is broken, end reached" % (path)
        break

      descriptors = np.load(PATHS['descriptors'] + path + '.npy')
      array = np.load(PATHS['arrays'] + path + '.npy')

      template = {
        'keypoints': keypoints,
        'descriptors': descriptors,
        'array': array
      }

      print '[O] Loaded template for %s' % (path)
      LOGOS[name].append(template)
      count += 1
  return

# ==========================================================================
# loadFeatures
#
# TODO
#
# ==========================================================================
def loadTemplates():
  global LOGOS, LOGO_NAMES

  for name in LOGO_NAMES:
    LOGOS[name] = list()
    count = 1
    while(True):
      path = '%s/%d'%(name, count)

      try:
        template = cv.imread(PATHS['logos'] + path + '.png')
      except Exception, e:
        print "[X] %s" % (e)
        break

      if(template == None):
        print "[!] Template for '%s' not found, the sequence is broken, end reached" % (path)
        break

      template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
      print '[O] Loaded template for %s'%(path)
      LOGOS[name].append(template)
      count += 1
  return

# ==========================================================================
# processResult
#
# TODO
#
# ==========================================================================
def processResult(res):
  result = {
    'state': 0,
    'message': 'Nothing detected'
  }
  if(res):
    state, matches, logoName = res
    result = {
      'state': 1,
      'message': 'Detected %s' % (logoName)
    }
  return result

# ==========================================================================
# loadFeatures
#
# TODO
#
# ==========================================================================
def detect(frames, method):
  if(method):
    if(method == 'matcher'):
      res = runFeatureMatcher(frames['temp'], frames['final'], LOGOS)
    elif(method == 'svm'):
      res = runSVM(frames['temp'], frames['final'], LOGOS)
    elif(method == 'knn'):
      res = runKNN(frames['temp'], frames['final'], LOGOS)
    else:
      res = runTemplateMatcher(frames['gray'], frames['final'], LOGOS)
  else:
    frames['final'] = frames['hsv']
  res = processResult(res)
  return frames, res

# ==========================================================================
# preprocessFrame
#
# TODO
#
# ==========================================================================
def preprocessFrame(frame):
  print '[>] Preprocessing frame ...'
  frames = {'original': frame, 'final': frame}
  frames['gray'] = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  #frames['blur'] = smooth(frame, mat=(15,15))
  frames['hsv'] = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
  frames['temp'] = FeatureDetector(cvImage=frame)
  print '[O] Frame is ready ...'
  return frames

# ==========================================================================
# Main
# ==========================================================================
def main():
  detectionMethod = 'matcher'

  try:
    detectionMethod = argv[1]
  except Exception, e:
    print '[!] One argument expected (detectionMethod [matcher, template, svm, knn])'
    
  print '[!] Using detection method "%s"\n' % (detectionMethod)

  if(detectionMethod == 'template'):
    print '[>] Loading templates ...'
    loadTemplates()
  else:
    print '[>] Loading features ...'
    loadFeatures()
  print '[O] Loaded'

  s = Server()
  while(True):
    print '[>] Waiting for a frame ...'

    data = s.receive()

    if(not data):
      break

    dCV, dPIL = data

    if(dCV is not None):
      frames = preprocessFrame(dCV)
      frames, result = detect(frames, detectionMethod)
      cv.imshow('from socket', frames['final'])
      if(cv.waitKey(1) == 23):
        break
    else:
      result = processResult(False)
    print result
    s.send(result)

  s.close()
  cv.destroyAllWindows()
  return

if(__name__ == '__main__'):
  main()
