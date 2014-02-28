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
# FLANN BASED MATCHER
# ======================================================================
try:
  FLANN_INDEX_KDTREE = 1
  flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
  search_params = dict(checks=50) 
  matcher = cv.FlannBasedMatcher(flann_params, search_params)
except:
  matcher = None


# ======================================================================
# exploreMatch
#
# TODO
#
# ======================================================================
def exploreMatch(image, kp_pairs, status = None, H = None):
  #h1, w1 = (350, 350)
  #h2, w2 = img2.shape[:2]
  #vis = np.zeros((max(h1, h2), w1+w2), np.uint8)
  #vis[:h1, :w1] = img1
  #vis[:h2, w1:w1+w2] = img2
  #vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

  #if H is not None:
  #  corners = np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
  #  corners = np.int32(cv2.perspectiveTransform(corners.reshape(1, -1, 2), H).reshape(-1, 2) + (w1, 0) )
  #  cv2.polylines(vis, [corners], True, (255, 255, 255))
  matches = 0
  if status is None:
    status = np.ones(len(kp_pairs), np.bool_)

  p = np.int32([kpp[1].pt for kpp in kp_pairs])
  #p2 = np.int32([kpp[1].pt for kpp in kp_pairs]) + (w1, 0)

  for (x1, y1), inlier in zip(p, status):
    cv.circle(image, (x1, y1), 3, (255, 0, 0), -1)
    if inlier:
      matches += 1
      cv.circle(image, (x1, y1), 3, (0, 255, 0), -1)
    
  return matches


# ======================================================================
# filterMatches
#
# TODO
#
# ======================================================================
def filterMatches(kp1, kp2, matches, ratio=0.60):
  mkp1, mkp2 = [], []
  for m in matches:
    if len(m) == 2 and m[0].distance < m[1].distance * ratio:
      m = m[0]
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
  for name, logo in LOGOS.iteritems():
    for template in logo:
      desc1, desc2 = template['descriptors'], temp['descriptors']
      kp1, kp2 = template['keypoints'], temp['keypoints']

      raw_matches = matcher.knnMatch(np.asarray(desc1, dtype=np.float32), trainDescriptors=np.asarray(desc2, dtype=np.float32), k=2) #2
      p1, p2, kp_pairs = filterMatches(kp1, kp2, raw_matches)

      if len(p1) >= 5:
        H, status = cv.findHomography(p1, p2, cv.RANSAC, 5.0)
        #print '%d / %d  inliers/matched' % (np.sum(status), len(status))
      else:
        H, status = None, None
        #print '%d matches found, not enough for homography estimation' % len(p1)

      matches = exploreMatch(image, kp_pairs, status, H)
      print matches

  return