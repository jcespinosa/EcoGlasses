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

# PATHS to save the corresponding data, 
PATHS = {
  "keypoints": "./keypoints/",
  "descriptors": "./descriptors/",
  "arrays": "./arrays/",
  "logos": "./logos/"
}

hessian_threshold = 5000

# ==========================================================================
# SURFDetector
#
# Gets an image
# If the parameter is a filename, sets the path to the filename and reads it
# If the parameter is a cv image, loads it in a variable.
# Process the image and uses the SURF method to get the keypoints and 
# descriptors
#
# ==========================================================================

def FeatureDetector(cvImage=None, filename=None):
  template = dict()
  hessian_threshold = 5000

  if(filename is not None):
    inputImage = cv.imread(filename)

  if(cvImage is not None):
    inputImage = cvImage

  imageGray = cv.cvtColor(inputImage, cv.COLOR_BGR2GRAY)

  detector = cv.SURF(hessian_threshold)
  keypoints, descriptors = detector.detectAndCompute(imageGray, None, useProvidedKeypoints = False)

  template["image"] = inputImage
  template["array"] = imageGray
  template["keypoints"] = keypoints
  template["descriptors"] = descriptors
  
  return template

def saveKeypoints(filename, keypoints):
  kArray = []

  for point in keypoints:
    keypoint = (point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
    kArray.append(keypoint)
  
  with open(filename, "wb") as outputFile:
    pickle.dump(kArray, outputFile)

  return

def showFeatures(filename, temp):
  for kp in temp["keypoints"]:
    x = int(kp.pt[0])
    y = int(kp.pt[1])
    cv.circle(temp["image"], (x, y), 3, (0, 0, 0), -1)

  print "[!] Press ESC to continue"
  while(True):
    cv.imshow("Features on %s"%(filename), temp["image"])
    if(cv.waitKey(33) == 1048603): #(ESC)
      cv.destroyWindow("Features on %s"%(filename))
      break

  return

def detection(inputName, extension, show=False):
  imagePath = PATHS["logos"] + inputName + "/"

  if(os.path.exists(imagePath)):
    count = 1
    while(True):
      filename = imagePath + str(count) + "." + extension

      if(not os.path.exists(filename)):
        print "[!] File '%s' not found, the sequence is broken, end reached"%(filename)
        break

      temp = FeatureDetector(filename = filename)

      saveKeypoints(PATHS["keypoints"] + inputName + "/" + str(count) + ".kp", temp["keypoints"])
      np.save(PATHS["descriptors"] + inputName + "/" + str(count) + ".npy", temp["descriptors"])
      np.save(PATHS["arrays"] + inputName + "/" + str(count) + ".npy", temp["array"])

      if(show):
        showFeatures(filename, temp)

      print "[O] Processed '%s'"%(filename)
      count += 1

  else:
    print "[X] Input name not found\n"

  return

def createPATHS(inputName):
  flag = False

  for path in PATHS:
    if(not os.path.exists(path)):
      os.mkdir(path)
      flag = True

    p = path + "/" + inputName + "/"
    if(not os.path.exists(p)):
      os.mkdir(p)
      flag = True

  return flag

def main():
  inputName = ""

  try:
    inputName = argv[1]
  except Exception, e:
    print "[X] Error, 1 argument expected (InputName), optional (extension [png, jpg])\n"
    return

  try:
    extension = argv[2]
  except Exception, e:
    print "[!] No extension specified, using default .png\n"
    extension = "png"

  if(createPATHS(inputName)):
    print "[O] Paths created\n"

  detection(inputName, extension, show=True)

  return

if(__name__ == "__main__"):
  main()
