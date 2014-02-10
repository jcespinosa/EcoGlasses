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

import cPickle as pickle
import cv2 as cv
import numpy as np

from FeatureDetection import FeatureDetector as SURFDetector
from FeatureDetection import PATHS


# Posible logos to be detected
LOGOS = ['kellogs']

TEMPLATES = dict()

# ------------------------------ NOTES ---------------------------------
# GIMP HSV range: (360,100,100)
# OpenCV HSV range:(180,255,255)
# ----------------------------------------------------------------------

# ======================================================================
# loadKeypoints
#
# TODO
#
# ======================================================================
def loadKeypoints(path):
  keypoints = []

  try:
    with open(PATHS['keypoints'] + path + '.kp', 'rb') as inputFile:
      kArray = pickle.load(inputFile)

    for point in kArray:
      feature = cv.KeyPoint(
        x=point[0][0],
        y=point[0][1],
        _size=point[1],
        _angle=point[2],
        _response=point[3],
        _octave=point[4],
        _class_id=point[5]
      )

      keypoints.append(feature)      

  except:
    return False

  return keypoints


# ======================================================================
# loadSURF
#
# TODO
#
# ======================================================================
def loadSURF():
  global TEMPLATES, LOGOS

  for logo in LOGOS:
    TEMPLATES[logo] = list()
    count = 1
    while(True):
      path = '%s/%d'%(logo, count)

      keypoints = loadKeypoints(path)
      
      if(not keypoints):
        print "[!] Template for '%s' not found, the sequence is broken, end reached"%(path)
        break

      descriptors = np.load(PATHS['descriptors'] + path + '.npy')
      array = np.load(PATHS['arrays'] + path + '.npy')

      template = {
        'keypoints': keypoints,
        'descriptors': descriptors,
        'array': array
      }

      print '[O] Loaded template for %s'%(path)
      TEMPLATES[logo].append(template)
      count += 1

  return


# ======================================================================
# SURFCompare
#
# Gets each individual ROI, keypoints and descriptors
# Compares the keypoints and descriptors with each signal template
# Returns True if the ROI corresponds to a possible signal template
#
# ======================================================================
def SURFCompare(temp, image):
  samples = temp['descriptors']
  responses = np.arange(len(temp['keypoints']), dtype=np.float32)

  knn = cv.KNearest()
  knn.train(samples, responses)

  for template in TEMPLATES:
    pattern = TEMPLATES[template]
    for t in pattern:
      for h, des in enumerate(t['descriptors']):
        des = np.array(des,np.float32).reshape((1,128))
        retval, results, neigh_resp, dists = knn.find_nearest(des,1)
        res, dist = int(results[0][0]), dists[0][0]

        if dist < 0.1: # draw matched keypoints in red color
          color = (0,0,255)
          print template
        else:  # draw unmatched in blue color
          color = (255,0,0)

        #Draw matched key points on original image
        x,y = temp['keypoints'][res].pt
        center = (int(x),int(y))
        cv.circle(image,center,2,color,-1)

  return True


# ======================================================================
# smooth
#
# Applies three possible smooth techniques, Gaussian blur, median filter
# or binary threshold
# Return the processed frame.
#
# ======================================================================
def smooth(image, mat=(3,3)):
  dst = cv.GaussianBlur(image, mat, 15)
  #dst = cv.medianBlur(image, 3)
  dump, dst = cv.threshold(dst, 100, 250, cv.THRESH_BINARY)
  return dst


# ======================================================================
# getROI
#
#
#
# ======================================================================
def getROI(image):
  fh, fw, fd = image.shape
  bh, bw = (350, 350)

  x = (fw - bw)/2
  y = (fh - bh)/2

  roi = image[y:y+bh, x:x+bw]
  return roi


# ======================================================================
# preprocessFrame
#
# Gets the original frame and converts it to the HSV space
# Applies a smoothing technique to the frame
# Saves each processed frame in a dictionary
#
# ======================================================================
def preprocessFrame(frame):
  frames = {'original': frame}
  roi = getROI(frame)
  frames['roi'] = roi
  frames['blur'] = smooth(roi, mat=(15,15))
  frames['hsv'] = cv.cvtColor(roi, cv.COLOR_BGR2HSV);
  #frames['temp'] = SURFDetector(cvImage=roi)
  return frames


# ======================================================================
# run
#
# Gets the frame to be processed and sends it to all the detection process
#
# ======================================================================
def run(frame):
  frames = preprocessFrame(frame)
  #SURFCompare(frames['temp'], frames['original'])
  return frames
