import numpy as np
import cv2 as cv

def getX(point):
  return point[0][0]

def getY(point):
  return point[0][1]

def bbox(minX, maxX, minY, maxY):
   return [minX, maxX, minY, maxY]

im = cv.imread('input/simple.jpeg')
imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 127, 255, 0)
im2, contours, hierarchy = cv.findContours(thresh, 1, 2)

#print("DIM = " + str(im.shape[1]))

final_contours = []
bboxes = []
for contour in contours:
  x,y,w,h = cv.boundingRect(contour)
  if (w) < (im.shape[1]-10):
    final_contours.append(contour)
    bboxes.append(bbox(x, y, w, h))

#outputimg = cv.drawContours(im, final_contours, -1, 255)
#cv.imwrite("tst.jpeg", outputimg)

counter = 0
for letter in bboxes: 
  letter_img = im[letter[0]:(letter[0]+letter[2]), letter[1]:(letter[1]+letter[3])]
  cv.imwrite(("output/letter" + str(counter) + ".jpeg"), letter_img);
  counter += 1