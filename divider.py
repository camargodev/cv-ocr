import numpy as np
import cv2 as cv

class bbox:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.w = 0
		self.h = 0

img = cv.imread('input/simple.jpeg')
imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 127, 255, 0)
im2, contours, hierarchy = cv.findContours(thresh, 1, 2)

final_contours = []
bboxes = []
counter = 0
for contour in contours:
  x,y,w,h = cv.boundingRect(contour)
  if w < (im2.shape[1]-10):
  	cv.rectangle(im2,(x,y),(x+w,y+h),(0,255,0),2)
  	charimg = im2[y:y+h, x:x+w]
  	cv.imwrite(("output/letter" + str(counter) + ".jpeg"), charimg)
  	counter += 1

cv.imwrite("results.jpeg", im2)