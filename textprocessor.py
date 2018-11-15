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
	h = img.shape[0]
	w = img.shape[1]
	imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	
	counter2 = 0
	copyImg = imgray.copy()
	#threshold manual para remover junção de letrar devido ao noise
	# se a vizinhança superior,inferior,esq,dir de um pixel tiver 2 pixels totalmente brancos (255, provavelmente teremos que mudar na hora de trabalhar com fotos de textos), iremos eliminar ele desde que sua intensidade seja maior que 60 (possivelmente também teremos que mudar mais tarde)
	for y in range(0, h):
		for x in range(0, w):
			counter = 0
			if y > 0 and imgray[y-1, x] < 255:
				counter = counter + 1
			if y < h-1 and imgray[y+1, x] < 255:
				counter = counter + 1
			if x > 0 and imgray[y, x-1] < 255:
				counter = counter + 1
			if x < w-1 and imgray[y, x+1] < 255:
				counter = counter + 1
				
			if counter <= 2:
				counter2 = counter2 +1
			#
			if counter <= 2 and imgray[y, x] > 60:
				copyImg[y, x] = 255
				
	_, threshold = cv.threshold(copyImg, 200, 255, 0)
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
	blank = np.zeros((int(h), int(w), 3), np.uint8)
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
	if len(uppers) == 0:
		return None
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
	if lines != None:
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
	else:
		return None

if __name__ == '__main__':
	path, filename, ext = getInputFilename("felipe.jpg")
	if os.path.isfile(path):
		letters = getLetters(path)
		if letters is not None:
			saveLetters(letters, filename, ext)
		else:
			print("The selected image has no text")
	else:
		print("The selected file does not exist")
		