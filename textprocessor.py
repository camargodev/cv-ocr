import numpy as np
import cv2 as cv
import os

inputFolder   = "input"
outputFolder  = "output"

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

def getInputFilename(filenameWithExt):
	inputFilename, inputFileExt = filenameWithExt.split('.')
	completeName = inputFolder + "/" + filenameWithExt 
	return completeName, inputFilename, inputFileExt

def getOutputFilename(imgNum, filename, ext):
	return outputFolder + "/" + str(filename) + "/letter" + str(imgNum) + "." + str(ext)

def save(img, imgNum, filename, ext):
	filename = getOutputFilename(imgNum, filename, ext)
	print(filename)
	cv.imwrite(filename, img)

def isValidShape(img, w):
	# check if is not the contour of the entire img
	return w < (img.shape[1]-10)

def proccessImg(img, contour):
	x,y,w,h = cv.boundingRect(contour)
	if (isValidShape(img, w)):
	  	charImg = img[y:y+h, x:x+w]
	  	return charImg
	return None

def getLetters(img, contours):
	letters = []
	for contour in contours:
		letterimg = proccessImg(img, contour)
		if letterimg is not None:
			letters.append(letterimg)
	return letters

def createFolder(name):
	directory = outputFolder + "/" + name
	if not os.path.exists(directory):
		os.makedirs(directory)

def saveLetters(imgs, inputFilename, ext):
	size = len(imgs)
	index = size
	createFolder(inputFilename)
	for letterImg in imgs:
		save(letterImg, index, inputFilename, ext)
		index -= 1

#def main():
if __name__ == '__main__':
	path, filename, ext = getInputFilename("sample.jpeg")
	img, contours = threshold(path)
	letters = getLetters(img, contours)
	saveLetters(letters, filename, ext)