import cv2
import numpy as np

img = cv2.imread('pavo.jpg',0)

# Create SURF object. You can specify params here or later.
# Here I set Hessian Threshold to 400
surf = cv2.SURF(5000)

# Find keypoints and descriptors directly
kp, des = surf.detectAndCompute(img,None)

print len(kp)

img2 = cv2.drawKeypoints(img,kp,None,(0,0,255),4)

#plt.imshow(img2)

#plt.show()

cv2.imwrite('keypoints.png',img2)

#img = cv2.imread('logo2.png')
#gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#sift = cv2.SIFT()
#kp = sift.detect(gray,None)

#img=cv2.drawKeypoints(gray,kp,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

#cv2.imwrite('keypoints.png',img)
