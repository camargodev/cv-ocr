import numpy as np
import cv2 as cv

class bbox:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.w = 0
		self.h = 0

def threshold(filename):
	img = cv.imread(filename)
	imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	ret, threshold = cv.threshold(imgray, 127, 255, 0)
	binimg, contours, hierarchy = cv.findContours(threshold, 1, 2)
	return binimg, contours

def save(img, imgnum):
	filename = "output/letter" + str(imgnum) + ".jpeg"
	cv.imwrite(filename, img)

def proccessimg(img, contour):
	x,y,w,h = cv.boundingRect(contour)
	if w < (img.shape[1]-10):
	  	charimg = img[y:y+h, x:x+w]
	  	return charimg
	return None

#def main():
if __name__ == '__main__':
	letter_counter = 0
	img, contours = threshold('input/simple.jpeg')
	for contour in contours:
  		letterimg = proccessimg(img, contour)
  		if letterimg is not None:
  			save(letterimg, letter_counter)
  			letter_counter += 1