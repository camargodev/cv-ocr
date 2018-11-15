import numpy as np
import cv2 as cv
import os
import math

inputFolder   = "input"
outputFolder  = "output"

WHITE = (255,255,255)

CHARACTER = 1
SPACE     = 2
LINEBREAK = 3

class ImgWithCoords:
	def __init__(self, img, x, y, charType):
		self.img  = img
		self.x    = x
		self.y    = y
		self.type = charType

def threshold(filename):
	img = cv.imread(filename)
	imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	_, threshold = cv.threshold(imgray, 127, 255, 0)
	return threshold

def getContours(img):
	_, contours, hierarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	outterContours = removeInnerContours(contours, hierarchy)
	sortedContours = sorted(outterContours, key=lambda ctr: cv.boundingRect(ctr)[0])
	return sortedContours

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
	  	return ImgWithCoords(charImg, x, y, CHARACTER)
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
		space = ImgWithCoords(newBlankImage(avgHeight, img2Begin-img1End), img1End, avgY, SPACE)
		return space
	return None

def getLineBreak():
	return ImgWithCoords(newBlankImage(10, 10), 0, 0, LINEBREAK)

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

def getMaxDimensions(imgs, scale):
	maxH = 0
	maxW = 0
	for img in imgs:
		if img.type == CHARACTER:
			h, w = img.img.shape[:2]
			maxH = max(maxH, h)
			maxW = max(maxW, w)
	return int(maxW*scale), int(maxH*scale)

def saveLetters(imgs, inputFilename, ext):
	createFolder(inputFilename)
	index = 1
	maxW, maxH = getMaxDimensions(imgs, 1.2)
	for letterImg in imgs:
		finalImg = newBlankImage(maxH, maxW)
		h, w = letterImg.img.shape[:2]
		dx = int(maxW/2) - int(w/2)
		dy = int(maxH/2) - int(h/2)
		if len(letterImg.img.shape) == 2:
			finalImg[dy:dy+h, dx:dx+w, 0] = letterImg.img
			finalImg[dy:dy+h, dx:dx+w, 1] = letterImg.img
			finalImg[dy:dy+h, dx:dx+w, 2] = letterImg.img
		else:
			finalImg[dy:dy+h, dx:dx+w] = letterImg.img	
		save(finalImg, index, inputFilename, ext)
		index += 1

def identifyLines(img):
	hist = cv.reduce(img,1, cv.REDUCE_AVG).reshape(-1)
	th = int(sum(hist)/len(hist))
	H,W = img.shape[:2]
	uppers = [y for y in range(H-1) if hist[y]<=th and hist[y+1]>th]
	lowers = [y for y in range(H-1) if hist[y]>th and hist[y+1]<=th]
	return uppers, lowers

def getLines(img):
	lines = []
	uppers, lowers = identifyLines(img)
	avgLineHeigth = int((sum(uppers) - sum(lowers))/len(uppers))
	for i in range(min(len(uppers), len(lowers))):
		lower = int(lowers[i] - (avgLineHeigth/2))
		upper = int(uppers[i] + (avgLineHeigth/2))
		lineImg = img[lower:upper, :]
		lines.append(lineImg)
	return lines

def getLetters(path):
	letters = []
	img = threshold(path)
	lines = getLines(img)
	for i in range(len(lines)):
		line = lines[i]
		contours = getContours(line)
		lettersFromContours = getLettersFromContours(line, contours)
		lettersWithSpaces = insertSpaces(lettersFromContours)
		for tempLetter in lettersWithSpaces:
			letters.append(tempLetter)
		if i < len(lines)-1:
			letters.append(getLineBreak())
	return letters

if __name__ == '__main__':
	path, filename, ext = getInputFilename("letrai.jpeg")
	letters = getLetters(path)
	saveLetters(letters, filename, ext)