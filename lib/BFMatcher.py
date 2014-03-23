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


# ======================================================================
# BRUTE FORCE MATCHER
# ======================================================================
try:
  matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
except Exception, e:
  print e
  matcher = None


# ======================================================================
# exploreMatch
#
# TODO
#
# ======================================================================
def exploreMatch(image, kp_pairs, status = None, H = None):
  matches = len(kp_pairs)

  pt = np.int32([kpp[1].pt for kpp in kp_pairs])

  for p in pt:
    p = tuple(p)
    cv.circle(image, p, 3, (0, 255, 0), -1)
    
  return matches


# ======================================================================
# filterMatches
#
# TODO
#
# ======================================================================
def filterMatches(kp1, kp2, matches, ratio=0.60):
  mkp1, mkp2 = list(), list()

  matches = sorted(matches, key = lambda x:x.distance)
  distances = [m.distance for m in matches]
  threshold = (sum(distances) / len(distances)) * 0.5

  for m in matches:
    if m.distance < threshold:
      mkp1.append(kp1[m.queryIdx])
      mkp2.append(kp2[m.trainIdx])

  p1 = np.float32([kp.pt for kp in mkp1])
  p2 = np.float32([kp.pt for kp in mkp2])
  kp_pairs = zip(mkp1, mkp2)
  return p1, p2, kp_pairs


# ======================================================================
# run
#
# TODO
#
# ======================================================================
def run(temp, image, LOGOS):
  global matcher

  for name, logo in LOGOS.iteritems():
    for template in logo:
      desc1, desc2 = template['descriptors'], temp['descriptors']
      kp1, kp2 = template['keypoints'], temp['keypoints']

      raw_matches = matcher.match(desc1, desc2)

      p1, p2, kp_pairs = filterMatches(kp1, kp2, raw_matches)

      matches = exploreMatch(image, kp_pairs)

      if(matches >= 3):
        print 'Matches > %d' % (matches)
        return (True, matches, name)

  return False
