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

def get_letters(img, contours):
	letters = []
	for contour in contours:
		letterimg = proccessimg(img, contour)
		if letterimg is not None:
			letters.append(letterimg)
	return letters

def save_letters(imgs):
	size = len(imgs)
	index = size
	for letterimg in imgs:
		save(letterimg, index)
		index -= 1

#def main():
if __name__ == '__main__':
	img, contours = threshold('input/sample.jpeg')
	letters = get_letters(img, contours)
	save_letters(letters)