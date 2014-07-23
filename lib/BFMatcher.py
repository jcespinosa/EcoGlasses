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


KNN_MATCHER = False

# ======================================================================
# BRUTE FORCE MATCHER
# ======================================================================
try:
  matcher = cv.BFMatcher(cv.NORM_HAMMING) if(KNN_MATCHER) else cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
except Exception, e:
  print e
  matcher = None


# ======================================================================
# exploreMatch
#
# TODO
#
# ======================================================================
def exploreMatch(img1, img2, kpPairs, status = None, H = None):
  h1, w1 = img1.shape[:2]
  h2, w2 = img2.shape[:2]
  vis = np.zeros((max(h1, h2), w1+w2), np.uint8)
  vis[:h1, :w1] = img1
  vis[:h2, w1:w1+w2] = img2
  vis = cv.cvtColor(vis, cv.COLOR_GRAY2BGR)

  if H is not None:
    corners = np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
    corners = np.int32(cv.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0))
    cv.polylines(vis, [corners], True, (255, 255, 255))

  if status is None:
    status = np.ones(len(kpPairs), np.bool_)

  p1 = np.int32([kpp[0].pt for kpp in kpPairs])
  p2 = np.int32([kpp[1].pt for kpp in kpPairs]) + np.int32([[w1, 0] for kpp in kpPairs])

  for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
    if inlier:
      col = (0, 255, 0)
      cv.circle(vis, (x1, y1), 2, col, -1)
      cv.circle(vis, (x2, y2), 2, col, -1)
    else:
      col = (0, 0, 255)
      cv.circle(vis, (x1, y1), 2, col, -1)
      cv.circle(vis, (x2, y2), 2, col, -1)

  for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
    if inlier:
      cv.line(vis, (x1, y1), (x2, y2), (0, 255, 0))

  matches = len(kpPairs)
    
  return matches, vis


# ======================================================================
# filterMatches
#
# TODO
#
# ======================================================================
def filterMatches(kp1, kp2, matches, ratio=0.50):
  global KNN_MATCHER

  mkp1, mkp2 = list(), list()
  threshold = None

  if(not KNN_MATCHER):
    matches = sorted(matches, key = lambda x:x.distance)
    distances = [m.distance for m in matches]
    threshold = (sum(distances) / len(distances)) * ratio

    for m in matches:
      if(m.distance < threshold):
        mkp1.append(kp1[m.queryIdx])
        mkp2.append(kp2[m.trainIdx])

  else:
    threshold = ratio
    for m in matches:
      if(len(m) == 2 and m[0].distance < (m[1].distance * threshold)):
        m = m[0]
        mkp1.append(kp1[m.queryIdx])
        mkp2.append(kp2[m.trainIdx])

  p1 = np.float32([kp.pt for kp in mkp1])
  p2 = np.float32([kp.pt for kp in mkp2])
  kpPairs = zip(mkp1, mkp2)
  return p1, p2, kpPairs


# ======================================================================
# run
#
# TODO
#
# ======================================================================
def run(temp, LOGOS):
  global KNN_MATCHER, matcher

  rawMatches, ratio, minMatches = None, None, None
  H, status = None, None

  if(matcher):
    for name, logo in LOGOS.iteritems():
      for template in logo:
        img1, img2 = template['array'], temp['array']
        desc1, desc2 = template['descriptors'], temp['descriptors']
        kp1, kp2 = template['keypoints'], temp['keypoints']

        if(KNN_MATCHER):
          rawMatches = matcher.knnMatch(desc1, trainDescriptors=desc2, k=2)
          ratio = 0.65
          minMatches = 10
        else:
          rawMatches = matcher.match(desc1, desc2)
          ratio = 0.50
          minMatches = 5

        p1, p2, kpPairs = filterMatches(kp1, kp2, rawMatches, ratio=ratio)

        if(len(p1) >= 4):
            H, status = cv.findHomography(p1, p2, cv.RANSAC, 5.0)
            print "[O] %d / %d  inliers/matched" % (np.sum(status), len(status))
        else:
            H, status = None, None
            print "[!] %d matches found, not enough for homography estimation" % len(p1)

        matches, image = exploreMatch(img1, img2, kpPairs, status, H)

        if(matches >= minMatches):
          print 'Matches > %d' % (matches)
          return (True, name, image)
  else:
    return False

  return False
