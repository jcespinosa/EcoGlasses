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
import sys

from FeatureDetection import FeatureDetector, loadKeypoints, PATHS
from time import sleep

sys.path.append('./lib/')

from KNN import run as runKNN
#from SVM import run as runSVM
from TemplateMatcher import run as runTemplateMatcher
from FeatureMatcher import run as runFeatureMatcher


# Posible logos to be detected
LOGO_NAMES = ['kellogs2']
LOGOS = dict()

# ======================================================================
# loadFeatures
#
# TODO
#
# ======================================================================
def loadFeatures():
  global LOGOS, LOGO_NAMES

  for name in LOGO_NAMES:
    LOGOS[name] = list()
    count = 1
    while(True):
      path = '%s/%d'%(name, count)

      a, keypoints = loadKeypoints(PATHS['keypoints'] + path + '.kp')
      
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
      LOGOS[name].append(template)
      count += 1
  return


# ======================================================================
# loadFeatures
#
# TODO
#
# ======================================================================
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


# ======================================================================
# smooth
#
# Applies three possible smooth techniques, Gaussian blur, median filter
# or binary threshold
# Return the processed frame.
#
# ======================================================================
def smooth(image, mat=(3,3)):
  #dst = cv.GaussianBlur(image, mat, 15)
  dst = cv.medianBlur(image, 3)
  dump, dst = cv.threshold(dst, 100, 250, cv.THRESH_BINARY)
  return dst


# ======================================================================
# getROI
#
# TODO
#
# ======================================================================
def calculateROI(im):
  fh, fw, fd = im.shape if(isinstance(im, np.ndarray)) else im
  bh, bw = (350, 350)

  x = (fw - bw)/2
  y = (fh - bh)/2

  return x, y, bh, bw

# ======================================================================
# getROI
#
# TODO
#
# ======================================================================
def getROI(im):
  x, y, bh, bw = calculateROI(im)
  roi = im[y:y+bh, x:x+bw]
  return roi


# ======================================================================
# combineFrames
#
# TODO
#
# ======================================================================
def combineFrames(im1, im2):
  im = im2
  x, y, bh, bw = calculateROI(im2)
  np.copyto(im[y:y+bh, x:x+bw], im1)
  return im


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
  frames['roi'] = getROI(frame)
  frames['gray'] = cv.cvtColor(frames['roi'], cv.COLOR_BGR2GRAY)
  frames['blur'] = smooth(frames['roi'], mat=(15,15))
  frames['hsv'] = cv.cvtColor(frames['roi'], cv.COLOR_BGR2HSV)
  frames['temp'] = FeatureDetector(cvImage=frames['roi'])
  return frames


# ======================================================================
# run
#
# Gets the frame to be processed and sends it to all the detection process
#
# ======================================================================
def run(frame, method=None):
  frames = preprocessFrame(frame)
  if(method):
    print '[!] Using %s'%(method)
    if(method == 'match'):
      runFeatureMatcher(frames['temp'], frames['roi'], LOGOS)
    elif(method == 'svm'):
      runSVM(frames['temp'], frames['roi'], LOGOS)
    elif(method == 'knn'):
      runKNN(frames['temp'], frames['roi'], LOGOS)
    else:
      runTemplateMatcher(frames['gray'], frames['roi'], LOGOS)
    frames['final'] = combineFrames(frames['roi'], frames['original'])
  else:
    frames['final'] = frames['original']
  return frames
