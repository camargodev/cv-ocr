import numpy as np
import cv2 as cv
import os

inputFolder   = "input"
outputFolder  = "output"
WHITE = (255,255,255)

class ImgWithCoords:
	def __init__(self, img, x, y, isLetter):
		self.img  = img
		self.x    = x
		self.y    = y
		self.isLetter = isLetter

def threshold(filename):
	img = cv.imread(filename)
	imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	_, threshold = cv.threshold(imgray, 127, 255, 0)
	_, contours, hierarchy = cv.findContours(threshold, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	outterContours = removeInnerContours(contours, hierarchy)
	sortedContours = sorted(outterContours, key=lambda ctr: cv.boundingRect(ctr)[0])
	return threshold, sortedContours

def removeInnerContours(contours, hierarchy):
	outterContours = []
	for i in range(len(hierarchy[0])):
		if not hierarchy[0][i][3] > 0:
			outterContours.append(contours[i]) 
	return outterContours

def getInputFilename(filenameWithExt):
	inputFilename, inputFileExt = filenameWithExt.split('.')
	completeName = inputFolder + "/" + filenameWithExt 
	return completeName, inputFilename, inputFileExt

def getOutputFilename(imgNum, filename, ext):
	return outputFolder + "/" + str(filename) + "/letter" + str(imgNum) + "." + str(ext)

def save(img, imgNum, filename, ext):
	filename = getOutputFilename(imgNum, filename, ext)
	cv.imwrite(filename, img)

def isImageContour(img, w):
	# check if is not the contour of the entire img
	return w > (img.shape[1]-10)

def proccessImg(img, contour):
	x,y,w,h = cv.boundingRect(contour)
	if not isImageContour(img, w):
	  	charImg = img[y:y+h, x:x+w]
	  	return ImgWithCoords(charImg, x, y, True)
	return None

def getLettersFromContours(img, contours):
	letters = []
	for contour in contours:
		letterImg = proccessImg(img, contour)
		if letterImg is not None:
			letters.append(letterImg)
	return letters

def createFolder(name):
	directory = outputFolder + "/" + name
	if not os.path.exists(directory):
		os.makedirs(directory)

def imagesAverageWidth(imgs):
	total = 0
	for image in imgs:
		total += image.img.shape[1]
	return total/len(imgs) 

def getSpace(img1, img2, avgW):
	img1End = img1.x + img1.img.shape[1]
	img2Begin = img2.x
	avgHeight = (img1.img.shape[0] + img2.img.shape[0])/2
	avgY = (img1.y + img2.y)/2
	if (img1End + (avgW/2)) < img2Begin:
		space = ImgWithCoords(newBlankImage(avgHeight, img2Begin-img1End), img1End, avgY, False)
		return space
	return None

def newBlankImage(h, w):
	blank = np.zeros((h, w, 3), np.uint8)
	blank[:, :] = WHITE
	return blank

def insertSpaces(imgs):
	textImgs = []
	size = len(imgs)
	avgW = imagesAverageWidth(imgs)
	for i in range(size-1):
		letter = imgs[i]
		nextLetter = imgs[i+1]
		textImgs.append(letter)
		space = getSpace(letter, nextLetter, avgW)
		if space != None:
			textImgs.append(space)
		if i == size-2:
			textImgs.append(nextLetter)
	return textImgs

def saveLetters(imgs, inputFilename, ext):
	createFolder(inputFilename)
	index = 1
	for letterImg in imgs:
		save(letterImg.img, index, inputFilename, ext)
		index += 1

def getLetters(filename, shouldWrite):
	path, filename, ext = getInputFilename(filename)
	img, contours = threshold(path)
	letters = getLettersFromContours(img, contours)
	lettersWithSpaces = insertSpaces(letters)
	if (shouldWrite):
		saveLetters(lettersWithSpaces, filename, ext)
	return lettersWithSpaces

if __name__ == '__main__':
	getLetters("lowercase.jpeg", True)