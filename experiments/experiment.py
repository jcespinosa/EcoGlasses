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

from sys import argv
from traceback import print_exc

class Test:
  def __init__(self):
    pass

  def setup(self):
    pass

  def run(self):
    pass

def rotate(image, angle):
  rows, cols = image.shape[:2]
  mat = cv.getRotationMatrix2D((cols/2, rows/2), angle, 1)
  result = cv.warpAffine(image , mat, (cols,rows))
  return result

def resize(image, value):
  h, w = image.shape[:2]
  result = cv.resize(image, None, fx=value, fy=value, interpolation=cv.INTER_CUBIC)
  return result

def noise(image, value):
  image = np.zeros(image.shape, dtype=np.uint8)
  noise = np.random.normal(loc=1.0, scale=1.0, size=image.shape)
  noiseImage = image + noise
  result = cv.addWeighted(image, 1.0, noiseImage, 0.0, 0.0) 
  return result

def blur(image, kernel):
  result = cv.GaussianBlur(image, kernel, 0)
  return result

def brightness(image, value):
  result = cv.multiply(image, np.array([value]))
  return result

TESTS = {
  'rotate': rotate,
  'resize': resize,
  'noise': noise,
  'blur': blur,
  'brightness': brightness
}

def main():
  image = argv[1]
  method = argv[2]
  params = (int(argv[3]), int(argv[3])) if(method == 'blur') else float(argv[3])

  inputImage = cv.imread(image)
  imageGray = cv.cvtColor(inputImage, cv.COLOR_BGR2GRAY)

  result = TESTS[method](imageGray, params)

  while(True):
    cv.imshow("Result", result)
    c = cv.waitKey(33)
    if((c % 256) == 27): #(ESC)
      cv.destroyWindow("Result")
      break
  return

if(__name__ == '__main__'):
  main()