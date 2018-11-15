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
	return processLetters(letters)

def createFolder(name):
	directory = outputFolder + "/" + name
	if not os.path.exists(directory):
		os.makedirs(directory)

def isXrangeInside(x, w, x2, w2):
	return x > x2 and (x+w) < (x2+w2)

def isYrangeInside(y, h, y2, h2):
	return y > y2 and (y+h) < (y2+h2)

def isLetterInsidePart(image1, image2):
	img1H, img1W = image1.img.shape
	img2H, img2W = image2.img.shape
	isXinside = isXrangeInside(image1.x, img1W, image2.x, img2W)
	isYinside = isYrangeInside(image1.y, img1H, image2.y, img2H)
	return isXinside or isYinside

def removeIncorrectShapes(imgs):
	correctImgs = []
	for image in imgs:
		isCorrect = True
		for comparingImage in imgs:
			if isLetterInsidePart(image, comparingImage):
				isCorrect = False
		if isCorrect:
			correctImgs.append(image)
	return correctImgs

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
		space = getSpace(nextLetter, letter, avgW)
		if space != None:
			textImgs.append(space)
		if i == size-2:
			textImgs.append(nextLetter)
	return textImgs

def processLetters(imgs):
	imgs = removeIncorrectShapes(imgs)
	imgs = insertSpaces(imgs)
	return imgs

def saveLetters(imgs, inputFilename, ext):
	createFolder(inputFilename)
	index = len(imgs)
	for letterImg in imgs:
		save(letterImg.img, index, inputFilename, ext)
		index -= 1

def getLetters(filename, shouldWrite):
	path, filename, ext = getInputFilename(filename)
	img, contours = threshold(path)
	letters = getLettersFromContours(img, contours)
	if (shouldWrite):
		saveLetters(letters, filename, ext)
	return letters

if __name__ == '__main__':
	getLetters("lowercase.jpeg", True)