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
# run
#
# TODO
#
# ======================================================================
def run(temp, image, LOGOS):
  samples = temp['descriptors']
  responses = np.arange(len(temp['keypoints']), dtype=np.float32)

  if(samples == None):
    return False

  knn = cv.KNearest()
  knn.train(samples, responses)

  for name, logo in LOGOS.iteritems():
    for template in logo:
      for h, des in enumerate(template['descriptors']):
        des = np.array(des,np.float32).reshape((1,128))
        retval, results, neigh_resp, dists = knn.find_nearest(des,1)
        res, dist = int(results[0][0]), dists[0][0]

        if dist < 1.0: # draw matched keypoints in red color
          color = (0,0,255)
          print template
        else:  # draw unmatched in blue color
          color = (255,0,0)

        #Draw matched key points on original image
        x,y = temp['keypoints'][res].pt
        center = (int(x), int(y))
        cv.circle(image, center, 2, color, -1)
  return True
  