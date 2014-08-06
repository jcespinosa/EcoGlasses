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

from cPickle import load
from os import listdir
from sys import path

path.append('./matchers/')
from BFMatcher import run as runBFMatcher
from FlannMatcher import run as runFlannMatcher
from KNN import run as runKNN
from TemplateMatcher import run as runTemplateMatcher


# The MATCHER
MATCHER = None

# MATCHERS calls 
MATCHERS = {
  'bf': runBFMatcher,
  'flann': runFlannMatcher,
  'knn': runKNN,
  'template': runTemplateMatcher
}

# The LOGOS
LOGOS = dict()

# Posible logos that could be detected
LOGO_NAMES = [name for name in listdir('./logos')]

# PATHS to load the saved data, 
PATHS = {
  'arrays': './arrays/',
  'descriptors': './descriptors/',
  'keypoints': './keypoints/',
  'logos': './logos/'
}


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

      keypoints = loadKeypoints(PATHS['keypoints'] + path + '.kp')
      
      if(not keypoints):
        print "[!] Template for '%s' not found, the sequence is broken, end reached." % (path)
        break

      descriptors = np.load(PATHS['descriptors'] + path + '.npy')
      array = np.load(PATHS['arrays'] + path + '.npy')

      template = {
        'keypoints': keypoints,
        'descriptors': descriptors,
        'array': array
      }

      print '[O] Loaded template for %s.' % (path)
      LOGOS[name].append(template)
      count += 1
  return


# ======================================================================
# loadTemplates
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

      if(template is None):
        print "[!] Template for '%s' not found, the sequence is broken, end reached." % (path)
        break

      template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
      print '[O] Loaded template for %s.' % (path)
      LOGOS[name].append(template)
      count += 1
  return


# ======================================================================
# loadKeypoints
#
# TODO
#
# ======================================================================
def loadKeypoints(filename):
  keypoints = list()

  try:
    with open(filename, 'rb') as inputFile:
      kArray = load(inputFile)

    for point in kArray:
      keypoint = cv.KeyPoint(
        x=point[0][0],
        y=point[0][1],
        _size=point[1],
        _angle=point[2],
        _response=point[3],
        _octave=point[4],
        _class_id=point[5]
      )

      keypoints.append(keypoint)
  except:
    return None
  return keypoints


# ======================================================================
# configureMatcher
#
# TODO
#
# ======================================================================
def configureMatcher(matcherMethod):
  global MATCHER

  if(matcherMethod == 'template'):
    print '[>] Loading templates ...'
    loadTemplates()
  else:
    print '[>] Loading features ...'
    loadFeatures()

  MATCHER = MATCHERS[matcherMethod]
  print '[O] Matcher loaded.\n'

  return


# ======================================================================
# runMatcher
#
# TODO
#
# ======================================================================
def runMatcher(frame, logo=None):
  result = MATCHER(frame, LOGOS, logo=logo)
  return result
