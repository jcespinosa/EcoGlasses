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
  for name, logo in LOGOS.iteritems():
    for template in logo:
      res = cv.matchTemplate(temp,template,cv.TM_CCOEFF_NORMED)
      threshold = 0.8
      loc = np.where( res >= threshold)
      for pt in zip(*loc[::-1]):
        cv.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
  return True

