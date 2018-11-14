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

bboxes = []
for contour in contours:
  contour = cv.approxPolyDP(contour,0.01*cv.arcLength(contour, True), True)
  counter = 0
  minX = 0
  maxX = 0
  minY = 0
  maxY = 0
  for point in contour:
    if counter == 0:
      minX = getX(point)
      maxX = getX(point)
      minY = getY(point)
      maxY = getY(point)
    else:
      minX = min(minX, getX(point))
      maxX = max(maxX, getX(point))
      minY = min(minY, getY(point))
      maxY = max(maxY, getY(point))
    counter += 1
  bboxes.append(bbox(minX, maxX, minY, maxY))

counter = 0
for letter in bboxes:
  letter_img = im[letter[0]:letter[1], letter[2]:letter[3]]
  cv.imwrite(("output/letter" + str(counter) + ".jpeg"), letter_img);
  counter += 1