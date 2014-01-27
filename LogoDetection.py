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

import cv2 as cv
import numpy as np
import cPickle as pickle


# ------------------------------ NOTES ------------------------------
# GIMP HSV range: (360,100,100)
# OpenCV HSV range:(180,255,255)
# -------------------------------------------------------------------

# Posible signals to be detected
LOGOS = ["metrorrey", "lala", "chocokrispis"]

TEMPLATES = dict()

paths = {
  "keypoints": "./keypoints/",
  "descriptors": "./descriptors/",
  "arrays": "./arrays/",
  "images": "./logos/"
}

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

def SURFDetector(cvImage=None, filename=None):
  template = dict()
  hessian_threshold = 5000

  if(filename is not None):
    path = "./signals/" + filename + ".png"
    inputImage = cv.imread(path)

  if(cvImage is not None):
    inputImage = cvImage

  imageGray = cv.cvtColor(inputImage, cv.COLOR_BGR2GRAY)
  surfDetector = cv.SURF(hessian_threshold)
  keypoints, descriptors = surfDetector.detectAndCompute(imageGray, None)

  template["image"] = imageGray
  template["keypoints"] = keypoints
  template["descriptors"] = descriptors

  #print template
  
  return template

# ==========================================================================
# compare
#
# Gets the ROI's of each color frame
# Sends each ROI to the feature detection algorithm
# If the ROI is valid, draws a green rectange in the original frame
# Returns the valid ROI's
#
# ==========================================================================
def loadKeypoints(logoName):
  keypoints = []

  with open(paths["keypoints"] + logoName + ".kp", "rb") as inputFile:
    kArray = pickle.load(inputFile)

  for point in kArray:
    feature = cv.KeyPoint(x=point[0][0], y=point[0][1], _size=point[1], _angle=point[2], _response=point[3], _octave=point[4], _class_id=point[5])
    keypoints.append(feature)

  return keypoints

def loadSURF():
  global TEMPLATES, LOGOS

  for logo in LOGOS:
    TEMPLATES[logo] = {
      "keypoints": loadKeypoints(logo),
      "descriptors": np.load(paths["descriptors"] + logo + ".npy"),
      "image": np.load(paths["arrays"] + logo + ".npy")
    }

  return

# ==========================================================================
# SURFCompare
#
# Gets each individual ROI, keypoints and descriptors
# Compares the keypoints and descriptors with each signal template
# Returns True if the ROI corresponds to a possible signal template
#
# ==========================================================================
def SURFCompare(roi, image):
  #print roi["keypoints"]
  samples = roi["descriptors"]
  responses = np.arange(len(roi["keypoints"]), dtype=np.float32)

  knn = cv.KNearest()
  knn.train(samples, responses)

  for t in TEMPLATES:
    for h, des in enumerate(TEMPLATES[t]["descriptors"]):
      des = np.array(des,np.float32).reshape((1,128))
      retval, results, neigh_resp, dists = knn.find_nearest(des,1)
      res, dist = int(results[0][0]), dists[0][0]

      if dist < 0.1: # draw matched keypoints in red color
        color = (0,0,255)
        print t
      else:  # draw unmatched in blue color
        color = (255,0,0)

      #Draw matched key points on original image
      x,y = roi["keypoints"][res].pt
      center = (int(x),int(y))
      cv.circle(image,center,2,color,-1)

  return True

# ==========================================================================
# fill
#
# Thresholds the color frame to find the countours of the objects
# If the countour and the area (pixels inside the countour) ar big enough
# fills each countour
# Gets the bounding rectangle of each object and the ROI
#
# ==========================================================================
def fill(color, original):
  minArea = 2000
  ROI = list()
  ret, color = cv.threshold(color, 127, 255, 0)
  contours, hierachy = cv.findContours(color, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  
  for c in contours:
    area = cv.contourArea(c)
    if(area > minArea):
      roi = dict()
      x, y ,w, h = cv.boundingRect(c)
      cv.drawContours(color, contours, -1, (255,255,255), -1)
      roi["rect"] = (x,y,w,h)
      roi["roi"] = original[y:y+h, x:x+h]
      ROI.append(roi)

  return color, ROI

# ==========================================================================
# smooth
#
# Applies three possible smooth techniques, Gaussian blur, median filter
# or binary threshold
# Return the processed frame.
#
# ==========================================================================
def smooth(image, mat=(3,3)):
  dst = cv.GaussianBlur(image, mat, 15)
  #dst = cv.medianBlur(image, 3)
  dump, dst = cv.threshold(dst, 100, 250, cv.THRESH_BINARY)
  return dst


# ==========================================================================
# compareROI
#
# Gets the ROI's of each color frame
# Sends each ROI to the feature detection algorithm to get it keypoints
# and descriptors
# Sends the keypoints and descriptors of each ROI to the feature comparison
# algorithm
# If the ROI is valid, draws a green rectange in the original frame
# Returns the valid ROI's
#
# ==========================================================================
def compareROI(regions, original):
  for region in regions:
    for a, roi in enumerate(regions[region]):
      roiSURF = SURFDetector(cvImage=roi["roi"])
      result = SURFCompare(roiSURF, original)
      if(result):
        x,y,w,h = roi["rect"]
        cv.rectangle(original, (x,y), (x+w,y+h), (0,255,0), 2)
  return regions
                
# ==========================================================================
# getROI
#
# Gets the frames and color frames and pass each one to the
# countour detection algorithm
# Saves the detected regions in a dictionary
#
# ==========================================================================
def getROI(frames, colors):
  regions = dict()
  
  for color in colors:
    #colors[color] = smooth(colors[color], mat=(15,15))
    colors[color], roi = fill(colors[color], frames["original"])        
    if(roi):
      regions[color] = roi

  return regions

# ==========================================================================
# colorSegmentation
#
# Gets the HSV frame and applies the color masks
# Calculates the two possible levels of red.
# Save each color frame ina dictionary
#
# ==========================================================================
def colorSegmentation(frameHSV):
  colorFrames = dict()

  # Color masks
  minLowRed, maxLowRed = np.array([0, 90, 90],np.uint8), np.array([10, 255, 255],np.uint8)
  minHighRed, maxHighRed = np.array([170, 90, 90],np.uint8), np.array([180, 255, 255],np.uint8)
  minYellow, maxYellow = np.array([20, 95, 95], np.uint8), np.array([30, 255, 255],np.uint8)
  minBlue, maxBlue = np.array([105, 80, 80], np.uint8), np.array([130, 255, 255], np.uint8)
  
  # Composite red mask
  lowRed = cv.inRange(frameHSV, minLowRed, maxLowRed)
  highRed = cv.inRange(frameHSV, minHighRed, maxHighRed)

  # Apply masks and get color segments
  colorFrames["red"] = cv.add(lowRed,highRed)
  colorFrames["yellow"] = cv.inRange(frameHSV, minYellow, maxYellow)
  colorFrames["blue"] = cv.inRange(frameHSV, minBlue, maxBlue)
  
  return colorFrames

# ==========================================================================
# preprocessFrame
#
# Gets the original frame and converts it to the HSV space
# Applies a smoothing technique to the frame
# Saves each processed frame in a dictionary
#
# ==========================================================================
def preprocessFrame(frame):
  frames = {"original": frame}
  frames["blur"] = smooth(frame, mat=(15,15))
  frames["hsv"] = cv.cvtColor(frame, cv.COLOR_BGR2HSV);
  frames["temp"] = SURFDetector(cvImage=frame)
  return frames

# ==========================================================================
# run
#
# Gets the frame to be processed and sends it to all the detection process
#
# ==========================================================================
def run(frame):
  frames = preprocessFrame(frame)
  colors, regions = {}, {}
  #colors = colorSegmentation(frames["hsv"])
  #regions = getROI(frames, colors)
  #regions = compareROI(regions, frames["original"])
  SURFCompare(frames["temp"], frames["original"])
  return frames, colors, regions

