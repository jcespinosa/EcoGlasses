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
from os import path as osPath, mkdir
from sys import argv, path
from traceback import print_exc

path.append('../')
from FeatureExtraction import FeatureExtractor, loadFeatures

path.append('../lib/')
from BFMatcher import run as runBFMatcher


PATHS = {
  'logos': './logos/',
  'results': {
    'rotate': './results/rotate/',
    'resize': './results/resize/',
    'noise': './results/noise/',
    'blur': './results/blur/',
    'brightness': './results/brightness/'
  }
}

LOGOS = loadFeatures()

# ======================================================================
# TEST FUNCTIONS
# ======================================================================
def rotate(image, angle):
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
  h, w = image.shape[:2]
  result = cv.resize(image, None, fx=value, fy=value, interpolation=cv.INTER_CUBIC)
  return result

def noise(image, value):
  empty = np.zeros(image.shape, dtype=np.uint8)
  noise = np.random.normal(loc=value, scale=1.0, size=image.shape)
  noiseImage = empty + noise
  result = cv.addWeighted(image, 1.0, noiseImage, 0.0, 0.0) 
  return noiseImage

def blur(image, kernel):
  result = cv.GaussianBlur(image, kernel, 0)
  return result

def brightness(image, value):
  result = cv.multiply(image, np.array([value]))
  return result


# ======================================================================


TESTS = {
  'rotate': {
    'test': rotate,
    'params': [angle for angle in range(10, 360, 10)]
  },
  'size': {
    'test': resize,
    'params':  [(a*0.25) for a in range(2, 9, 1)]
  },
  'noise': {
    'test': noise,
    'params': [(value*0.5) for value in range(2, 7, 1)]
  },
  'blur': {
    'test': blur,
    'params': [5, 9, 13, 17, 21, 25, 29, 33, 37, 41]
  },
  'brightness': {
    'test': brightness,
    'params': [(value*0.2) for value in range(1, 11, 1)]
  },
}


class Test:
  def __init__(self, tType, imageName):
    self.results = {
      'base': dict(),
      'results': dict(),
    }
    self.frame = cv.imread(PATHS['logos'] + imageName + '.png')
    self.imageName = imageName
    self.type = tType
    self.setup(imageName)

  def createPATHS(self, inputName):
    global PATHS

    flag = False
    PATHS = PATHS['results']
    for p in PATHS:
      p = PATHS[p]
      if(not osPath.exists(p)):
        mkdir(p)
        flag = True

      p = p + inputName + '/'
      if(not osPath.exists(p)):
        mkdir(p)
        flag = True

    return flag

  def setup(self, imageName):
    global TESTS

    self.test = TESTS[self.type]['test']
    self.params = TESTS[self.type]['params']

    if(self.createPATHS(imageName)):
      print '[O] Results paths created.'
    return

  def save(self):
    return

  def run(self):
    global LOGOS
    for param in self.params:
      param = (param, param) if(self.type == 'blur') else param
      frame = self.test(self.frame, param)
      self.temp = FeatureExtractor(cvImage=frame)
      state, logoName, matches, image = runBFMatcher(self.temp, LOGOS)
      image = image if(state==1) else self.temp['array']
      while(True):
        cv.imshow("Result", image)
        cv.moveWindow("Result", 100, 100)
        c = cv.waitKey(33)
        if((c % 256) == 27): #(ESC)
          cv.destroyWindow("Result")
          break
    return


def main():
  image = argv[1]
  method = argv[2]

  test = Test(method, image)
  test.run()

  return

if(__name__ == '__main__'):
  main()
