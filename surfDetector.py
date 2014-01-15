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

from sys import argv
import cv2 as cv
import numpy as np
import cPickle as pickle
import os

# ======================================================================
# surfDetector
#
# Gets an external filename
# Uses the SURF Feature detection method to obtain the keypoints
# and descriptors from the image
# Saves the keypoints on a *.kp file
# Saves the image and descriptors on a *.npy file
# Show the features in a cv window
#
# ======================================================================

# Paths to save the corresponding data, 
# please create the folders before using the tool

paths = {
  "keypoints": "./keypoints/",
  "descriptors": "./descriptors/",
  "arrays": "./arrays/",
  "logos": "./logos/"
}

hessian_threshold = 5000

def saveKeypoints(keypoints, filename):
  kArray = []

  for point in keypoints:
    keypoint = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
    kArray.append(keypoint)
  
  with open(filename, "wb") as outputFile:
    pickle.dump(kArray, outputFile)

  return

def detection(inputImageName):
  imagePath = paths["logos"] + inputImageName
  name = inputImageName.split(".")[0]

  inputImage = cv.imread(imagePath)
  imageGray = cv.cvtColor(inputImage, cv.COLOR_BGR2GRAY)

  surfDetector = cv.SURF(hessian_threshold)
  keypoints, descriptors = surfDetector.detectAndCompute(imageGray, None, useProvidedKeypoints = False)

  saveKeypoints(keypoints, paths["keypoints"] + name + ".kp")
  np.save(paths["descriptors"] + name + ".npy", descriptors)
  np.save(paths["arrays"] + name + ".npy", imageGray)

  for kp in keypoints:
    x = int(kp.pt[0])
    y = int(kp.pt[1])
    cv.circle(inputImage, (x, y), 3, (0, 0, 0))

  while True:
    cv.imshow("features", inputImage)

    if cv.waitKey(10) == 10:
      break

  return

def createPaths():
  flag = False

  for path in paths:
    if(not os.path.exists(path)):
      os.mkdir(path)
      flag = True

  return flag


def main():
  inputImageName = ""

  if(createPaths()):
    print "[O] Paths created"
    return
  else:
    try:
      inputImageName = argv[1]
    except Exception, e:
      print "[X] Error, 1 argument expected (inputImage)"
      return

    detection(inputImageName)

  return

if(__name__ == "__main__"):
  main()