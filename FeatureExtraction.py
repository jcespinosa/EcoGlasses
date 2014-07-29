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

from cPickle import dump
from os import mkdir, path
from sys import argv


# PATHS to save the data, 
PATHS = {
  'arrays': './arrays/',
  'descriptors': './descriptors/',
  'keypoints': './keypoints/',
  'logos': './logos/'
}


# ======================================================================
# FeatureExtractor
#
# Gets an image
# If the parameter is a filename, sets the path to the filename and reads it
# If the parameter is a cv image, loads it in a variable.
# Process the image and uses the ORB method to get the keypoints and descriptors
#
# ======================================================================
def FeatureExtractor(cvImage=None, filename=None):
  template = dict()

  if(filename is not None):
    inputImage = cv.imread(filename)

  if(cvImage is not None):
    inputImage = cvImage

  imageGray = cv.cvtColor(inputImage, cv.COLOR_BGR2GRAY)

  detector = cv.ORB(nfeatures=1000)
  keypoints, descriptors = detector.detectAndCompute(imageGray, None, useProvidedKeypoints=False)

  template['image'] = inputImage
  template['array'] = imageGray
  template['keypoints'] = keypoints
  template['descriptors'] = descriptors
  return template


# ======================================================================
# saveKeypoints
#
# TODO
#
# ======================================================================
def saveKeypoints(filename, keypoints):
  kArray = list()

  for point in keypoints:
    keypoint = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
    kArray.append(keypoint)
  
  with open(filename, 'wb') as outputFile:
    dump(kArray, outputFile)
  return


# ======================================================================
# showFeatures
#
# TODO
#
# ======================================================================
def showFeatures(filename, temp):
  for kp in temp['keypoints']:
    x = int(kp.pt[0])
    y = int(kp.pt[1])
    cv.circle(temp['image'], (x, y), 3, (0, 0, 0), -1)

  print '[!] Press ESC to continue.'
  while(True):
    cv.imshow("Features on %s" % (filename), temp['image'])
    c = cv.waitKey(100)
    #print "You pressed %d (0x%x), LSB: %d (%s)." % (c, c, c % 256, repr(chr(c%256)) if c%256 < 128 else '?')
    if((c % 256) == 27): #(ESC)
      cv.destroyWindow("Features on %s"%(filename))
      break
  return


# ======================================================================
# extraction
#
# TODO
#
# ======================================================================
def extraction(inputName, extension, show=False):
  imagePath = PATHS['logos'] + inputName + '/'

  if(path.exists(imagePath)):
    count = 1
    while(True):
      filename = imagePath + str(count) + '.' + extension

      if(not path.exists(filename)):
        print "[!] File '%s' not found, the sequence is broken, end reached." % (filename)
        break

      temp = FeatureExtractor(filename = filename)

      saveKeypoints(PATHS['keypoints'] + inputName + '/' + str(count) + '.kp', temp['keypoints'])
      np.save(PATHS['descriptors'] + inputName + '/' + str(count) + '.npy', temp['descriptors'])
      np.save(PATHS['arrays'] + inputName + '/' + str(count) + '.npy', temp['array'])

      if(show):
        showFeatures(filename, temp)

      print "[O] Processed '%s'."%(filename)
      count += 1

  else:
    print '[X] Input name not found.'
  return


# ======================================================================
# createPATHS
#
# TODO
#
# ======================================================================
def createPATHS(inputName):
  flag = False

  for p in PATHS:
    p = PATHS[p]
    if(not path.exists(p)):
      mkdir(p)
      flag = True

    p = p + inputName + '/'
    if(not path.exists(p)):
      mkdir(p)
      flag = True

  return flag


# ======================================================================
# main
# ======================================================================
def main():
  inputName, extension = '', ''

  try:
    inputName = argv[1]
  except Exception, e:
    print '[X] Error, 1 argument expected (InputName), optional (extension [png, jpg]).'
    

  try:
    extension = argv[2]
  except Exception, e:
    print '[!] No extension specified, using default .png.'
    extension = 'png'

  from os import listdir 
  LOGO_NAMES = [name for name in listdir('./logos')]
  for inputName in LOGO_NAMES:
    if(createPATHS(inputName)):
      print '[O] Paths created.'
      extraction(inputName, extension, show=True)
  return


if(__name__ == '__main__'):
  main()
