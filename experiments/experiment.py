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

from math import ceil, sqrt
from os import listdir, mkdir, path as osPath
from random import random
from sys import argv, path
from time import time
from traceback import print_exc

path.append('../')
import Matcher
from FeatureExtraction import FeatureExtractor


# ======================================================================
# TEST FUNCTIONS
# ======================================================================
def rotate(image, angle):
  #print "Rotation > %s" % (str(angle))
  h, w = image.shape[:2]
  size = int(ceil(sqrt(pow(h, 2) + pow(w, 2))))
  center = size / 2
  offsetX, offsetY = (size - h)/2, (size - w)/2
  result = np.zeros((size, size, 3), dtype=np.uint8)
  mat = cv.getRotationMatrix2D((center, center), angle, 1)
  result[offsetX:(offsetX + h), offsetY:(offsetY + w), :] = image
  result = cv.warpAffine(result, mat, (size, size), flags=cv.INTER_LINEAR)
  return result

def resize(image, value):
  #print "Resize > %s" % (str(value))
  h, w = image.shape[:2]
  result = cv.resize(image, None, fx=value, fy=value, interpolation=cv.INTER_CUBIC)
  return result

def noise(image, value):
  #print "Noising > %s" % (str(value))
  pepper = np.array([0, 0, 0], dtype=np.uint8)
  result = np.copy(image)
  for i, l in enumerate(image):
    for j, p in enumerate(l):
      result[i][j] = pepper if(random() > value) else result[i][j]
  return result

def obstruction(image, value, segments=20):
  #print "Obstructing > %s" % (str(value))
  result = np.copy(image)
  h, w = image.shape[:2]
  segmentSize = (w / segments)
  obsSegment = segmentSize * value
  pos = 0
  for i in range(segments):
    result[0:h, pos:pos+obsSegment, :] = np.array([0, 0, 0], dtype=np.uint8)
    pos += segmentSize
  return result

def blur(image, value):
  #print "Blurring > %s" % (str(value))
  kernel = (value, value)
  result = cv.GaussianBlur(image, kernel, 0)
  return result

def brightness(image, value):
  #print "Brightness > %s" % (str(value))
  result = cv.multiply(image, np.array([value]))
  return result
# ======================================================================

PARAMS = {
  'size': {
    'p': [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0], # 8
    'i': 0
  },
  'blur': {
    'p': [1, 5, 9, 13, 17, 21], # 6
    'i': 1
  },
  'noise': {
    'p': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0], # 7
    'i': 2
  },
  'obstruction': {
    'p': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5], # 6
    'i': 3
  },
  'brightness': {
    'p': [0.13, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0], # 9
    'i': 4
  },
  'rotate': {
    'p': [180, 135, 90, 45, 0, 315, 270, 225, 180], # 9
    'i': 5
  }
}

PARAMSA = {
  'size': {
    'p': [1.0],
    'i': 0
  },
  'blur': {
    'p': [1],
    'i': 1
  },
  'noise': {
    'p': [1.05],
    'i': 2
  },
  'obstruction': {
    'p': [0.0],
    'i': 3
  },
  'brightness': {
    'p': [1.0],
    'i': 4
  },
  'rotate': {
    'p': [0],
    'i': 5
  }
}

LOGOS = [name.split('.')[0] for name in listdir('logos')]

class Test:
  def __init__(self, tType=None):
    self.tType = tType if(tType is not None) else 'all'
    self.show = False
    self.resultFile = './results/' + self.tType + '.csv'
    self.setup()

  def setup(self):
    global PARAMS
    if(self.tType == 'all'):
      from itertools import product 
      allParams = [
        PARAMSA['size']['p'],
        PARAMSA['blur']['p'],
        PARAMSA['noise']['p'],
        PARAMSA['obstruction']['p'],
        PARAMSA['brightness']['p'],
        PARAMSA['rotate']['p'],
      ]
      self.params = list(product(*allParams))
      with open(self.resultFile, 'w+') as resultFile:
        resultFile.write('size,blur,noise,obstruction,brightness,rotate,trues,falses,error,time\n')
    else:
      self.params = list()
      testParams = PARAMS[self.tType]['p']
      for param in testParams:
        params = [0, 0, 0, 0, 0, 0]
        params[PARAMS[self.tType]['i']] = param
        self.params.append(tuple(params))
      with open(self.resultFile, 'w+') as resultFile:
        resultFile.write('value,trues,falses,error,time\n')

    print '[>] Executing %d experiments ...' % (len(self.params))
    return

  def configFrame(self, frame, params):
    frame = resize(frame, params[0]) if(params[0]) else frame
    frame = blur(frame, params[1]) if(params[1]) else frame
    frame = noise(frame, params[2]) if(params[2]) else frame
    frame = obstruction(frame, params[3]) if(params[3]) else frame
    frame = brightness(frame, params[4]) if(params[4]) else frame
    frame = rotate(frame, params[5]) if(params[5]) else rotate(frame, 0)
    return frame

  def showImage(self, image):
    while(True):
      cv.imshow("Result", image)
      cv.moveWindow("Result", 100, 100)
      c = cv.waitKey(33)
      if((c % 256) == 27): #(ESC)
        cv.destroyWindow("Result")
        break
    return

  def save(self, result, params):
    if(self.tType == 'all'):
      values = list(map(str, params))
      results = values + map(str,result)
    else:
      value = str(max(params))
      results = [value] + map(str,result)
    with open(self.resultFile, 'a') as resultFile:
      resultFile.write(','.join(results) + '\n')
    return

  def printAdvance(self, a, time):
    advance = (float(a) * 100.0) / float(len(self.params))
    print "Time > %s sec, Advance > %.2f" % (time, advance)
    return

  def run(self):
    global LOGOS
    for a, params in enumerate(self.params):
      t, f, e = 0, 0, 0
      startTestTime = time()
      for logo in LOGOS:
        frame = cv.imread('./logos/' + logo + '.png')
        frame = self.configFrame(frame, params)
        temp = FeatureExtractor(cvImage=frame)
        state, matchedLogo, matches, image = Matcher.runMatcher(temp)
        image = image if(image is not None) else temp['array']
        if(state == 1):
          if(matchedLogo == logo):
            t += 1
          else:
            e += 1
        else:
          f += 1
        if(self.show):
          self.showImage(image)
      endTestTime = "%.2f" % (time() - startTestTime)
      self.printAdvance(a, endTestTime)
      self.save([t, f, e, endTestTime], params)
    self.printAdvance(len(self.params), endTestTime)

    return


def main():
  testType = None
  try:
    testType = argv[1]
  except Exception, e:
    print '[!] One argument expected (testType [rotate, size, noise, blur, obstruction, brightness]).'

  Matcher.configureMatcher('bf')

  for i, testType in enumerate(['size', 'blur', 'noise', 'obstruction', 'brightness', 'rotate']):
    print "Experiment %d > %s" % ((i+1), testType)
    test = Test(tType=testType)
    startExperimentTime = time()
    test.run()
    print "Total time > %.2f seconds" % (time() - startExperimentTime)
    print '[O] Experiments completed.\n'

  return

if(__name__ == '__main__'):
  main()

#'[O] [X] [!] [>] [?] >> << > <'
