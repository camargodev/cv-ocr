import numpy as np
import cv2 as cv
import os
import math
import matlab.engine
import matplotlib.pyplot as plt
from copy import deepcopy

inputFolder   = "input"
outputFolder  = "output"
baseCharsFolder = "lettersDB"

WHITE = (255,255,255)
WHITE2D = (255,255)

CHARACTER = 1
SPACE     = 2
LINEBREAK = 3

# MATLAB engine; needed to call MATLAB's functions
eng = matlab.engine.start_matlab()

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
    return outputFolder + "/" + str(filename) + "/letter" + str(imgNum).zfill(4) + "." + str(ext)

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
    return directory

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

# returns the folder where the images were saved    
def saveLetters(imgs, inputFilename, ext):
    directory = createFolder(inputFilename)
    retImgs = []
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
        letterImg.img = finalImg
        retImgs.append(letterImg)    
        index += 1
        
    return directory, retImgs

def identifyLines(img):
    hist = cv.reduce(img,1, cv.REDUCE_AVG).reshape(-1)
    th = int(sum(hist)/len(hist))
    H,W = img.shape[:2]
    uppers = [y for y in range(H-1) if hist[y]<=th and hist[y+1]>th]
    lowers = [y for y in range(H-1) if hist[y]>th and hist[y+1]<=th]
    return uppers, lowers  

def expectedLineHeight(uppers, lowers):
    maxHeight = 0
    for i in range(min(len(uppers), len(lowers))):
        height = uppers[i] - lowers[i]
        if height > maxHeight:
            maxHeight = height
    return height
  
def getLines(img):
    lines = []
    uppers, lowers = identifyLines(img)
    if len(uppers) == 0:
        return None
    avgLineHeigth = int((sum(uppers) - sum(lowers))/len(uppers))
    expLineHeight = expectedLineHeight(uppers, lowers)
    for i in range(min(len(uppers), len(lowers))):
        height = uppers[i] - lowers[i]
        if height > avgLineHeigth*0.8:
            lower = int(lowers[i] - avgLineHeigth)
            upper = int(uppers[i] + avgLineHeigth)
            lineImg = img[lower:upper, :]
            lines.append(lineImg)
    return lines
    
def proccessMultiContourLetters(letters):
    newLetters = []
    size = len(letters)
    cameFromI = False
    for i in range(size-1):
        if cameFromI:
           cameFromI = False
           continue
        letter = letters[i]
        nextLetter = letters[i+1]
        if nextLetter.x > letter.x and (nextLetter.x + nextLetter.img.shape[1]) < (letter.x + letter.img.shape[1]):
            h, w = letter.img.shape[:2]
            hn, wn = nextLetter.img.shape[:2]
            wdiff = int((w - wn)/2)
            fullLetter = np.zeros((h+hn, w), np.uint8)
            fullLetter[0:hn, 0:w] = 255
            fullLetter[0:hn, wdiff:wn+wdiff] = nextLetter.img
            fullLetter[hn:h+hn, 0:w] = letter.img
            full = ImgWithCoords(fullLetter, letter.x, nextLetter.y, CHARACTER)
            newLetters.append(full)
            cameFromI = True
        if not cameFromI:
            newLetters.append(letter)
        if i+1 == size-1:
            newLetters.append(nextLetter)
            
    return newLetters

def getLetters(path):
    letters = []
    img = threshold(path)
    lines = getLines(img)
    if lines != None:
        for i in range(len(lines)):
            line = lines[i]
            contours = getContours(line)
            lettersFromContours = getLettersFromContours(line, contours)
            fixedLetters = proccessMultiContourLetters(lettersFromContours)
            lettersWithSpaces = insertSpaces(fixedLetters)
            for tempLetter in lettersWithSpaces:
                letters.append(tempLetter)
            if i < len(lines)-1:
                letters.append(getLineBreak())
        return letters
    else:
        return None

# Arguments:
#       inputImagePath: Absolute path to the image we want to compare to other images.
#       baseImagesPath: Absolute path to the folder that contains the other images.
# Call example: findClosestLetter('D:/UFRGS/Sexto Semestre/Visao Computacional/Travalho 2/pngs/bonefishes.png', 'D:/UFRGS/Sexto Semestre/Visao Computacional/Travalho 2/pngs')
# Return: name of the image in baseImagesPath that is closest to inputImagePath
def findClosestLetter(inputImagePath, baseImagesPath):
    closest, distance = eng.cbir(inputImagePath, baseImagesPath, 3, nargout=2); # há um argumento a mais do que na função cbir original do matlab
                                                                                           # a fim de indicar quantos valores de retorno são esperados
    return closest[0]
    
def minKeyPoints(img, baseImagesPath, featureDetectorName):
    #img = threshold(inputImagePath)
    minimumKeyPoints = []
    for file in os.listdir(baseImagesPath):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"): 
            absolutePath = os.path.join(baseImagesPath, filename)
            img2= threshold(absolutePath) # trainImage
            
            #img1 = cv.resize(img, (0,0), fx=(width2/width1), fy=(height2/height1))
            img1 = img
            height1, width1 = img1.img.shape[:2]
            height2, width2 = img2.shape
            
            if featureDetectorName == "BRISK":
                featureDetector = cv.BRISK_create()
            if featureDetectorName == "ORB":
                featureDetector = cv.ORB_create()
            if featureDetectorName == "SURF":
                featureDetector = cv.xfeatures2d.SURF_create()
            if featureDetectorName == "SIFT":
                featureDetector = cv.xfeatures2d.SIFT_create()
            
            # find the keypoints and descriptors
            kp1, des1 = featureDetector.detectAndCompute(img1.img,None)
            counter = 0
            while (len(kp1) == 0 or des1 is None or len(des1) < 10) and counter < 5:
                img1.img = cv.resize(img1.img, (0,0), fx=2, fy=2) 
                kp1, des1 = featureDetector.detectAndCompute(img1.img,None)
                counter = counter + 1
                
            kp2, des2 = featureDetector.detectAndCompute(img2,None)
            counter = 0
            while (len(kp2) == 0 or des2 is None or len(des2) < 10) and counter < 5:
                img2 = cv.resize(img2, (0,0), fx=2, fy=2) 
                kp2, des2 = featureDetector.detectAndCompute(img2,None)
                counter = counter + 1
                
            if des1 is None or des2 is None:
                return None
            minimumKeyPoints.append(len(des1))
            minimumKeyPoints.append(len(des2))
            
    minimumKeyPoints = sorted(minimumKeyPoints)
    return minimumKeyPoints[0]

# acha a distância da imagem de entrada para as imagens em baseImagesPath, de acordo com o feature detector definido por featureDetectorName
def distanceToBaseImages(img, baseImagesPath, featureDetectorName):
    #img = threshold(inputImagePath)
    closestImages = []
    
    #finds the minimum number of keypoints in all analyzed images (every image in baseImagesPath plus inputImagePath)
    minimumKeyPoints = minKeyPoints(img, baseImagesPath, featureDetectorName)
    if minimumKeyPoints is None:
        return None
    
    for file in os.listdir(baseImagesPath):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            absolutePath = os.path.join(baseImagesPath, filename)
            img2= threshold(absolutePath) # trainImage
            
            #img1 = cv.resize(img, (0,0), fx=(width2/width1), fy=(height2/height1))
            img1 = img
            height1, width1 = img1.img.shape[:2]
            height2, width2 = img2.shape

            if featureDetectorName == "BRISK":
                featureDetector = cv.BRISK_create()
            if featureDetectorName == "ORB":
                featureDetector = cv.ORB_create()
            if featureDetectorName == "SURF":
                featureDetector = cv.xfeatures2d.SURF_create()
            if featureDetectorName == "SIFT":
                featureDetector = cv.xfeatures2d.SIFT_create()
                
            # find the keypoints and descriptors
            kp1, des1 = featureDetector.detectAndCompute(img1.img,None)         
            counter = 0
            while (len(kp1) == 0 or des1 is None or len(des1) < 10) and counter < 5:
                img1.img = cv.resize(img1.img, (0,0), fx=2, fy=2) 
                kp1, des1 = featureDetector.detectAndCompute(img1.img,None)
                counter = counter + 1
                
            kp2, des2 = featureDetector.detectAndCompute(img2,None)
            counter = 0
            while (len(kp2) == 0 or des2 is None or len(des2) < 10) and counter < 5:
                img2 = cv.resize(img2, (0,0), fx=2, fy=2) 
                kp2, des2 = featureDetector.detectAndCompute(img2,None)
                counter = counter + 1
                
            bf = cv.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=minimumKeyPoints)
            distance = 0
            for descriptor in matches:
                for match in descriptor:
                    distance = distance + match.distance
            closestImages.append([distance, filename])
            
        else:
            continue
    return closestImages
    
def sumFeatureDescriptorsResults(sift, surf, orb, brisk):

    if sift is not None:
        listName = sift
    elif surf is not None:
        listName = surf
    elif orb is not None:
        listName = orb
    elif brisk is not None:
        listName = brisk
    else:
        return -1 #space

    if sift is not None:    
        # sort matches according to their distance to the input image
        sift.sort(key=lambda x: x[0])
        # and normalize the distances
        siftSum = [float(i[0]) for i in sift]
        siftSum = sum(siftSum)  
        siftNorm = [float(i[0])/siftSum for i in sift]
    else:
        siftNorm = [0 for i in listName]
    
    if surf is not None:
        surf.sort(key=lambda x: x[0])
        surfSum = [float(i[0]) for i in surf]
        surfSum = sum(surfSum)  
        surfNorm = [float(i[0])/surfSum for i in surf]
    else:
        surfNorm = [0 for i in listName]
    
    if orb is not None:
        orb.sort(key=lambda x: x[0])
        orbSum = [float(i[0]) for i in orb]
        orbSum = sum(orbSum)    
        orbNorm = [float(i[0])/orbSum for i in orb]
    else:
        orbNorm = [0 for i in listName]
    
    if brisk is not None:
        brisk.sort(key=lambda x: x[0])
        briskSum = [float(i[0]) for i in brisk]
        briskSum = sum(briskSum)    
        briskNorm = [float(i[0])/briskSum for i in brisk]
    else:
        briskNorm = [0 for i in listName]
    
    sumResult = []
    for i in range(0,len(listName)):
        sumResult.append([surfNorm[i]+siftNorm[i]+orbNorm[i]+briskNorm[i], listName[i][1]])
        
    return sumResult

# voto de cada descritor pra qual letra ele acha que é; dois considerando uma letra como a segunda melhor > um considerando a primeira letra melhor
def vote(sift, surf, orb, brisk):
    sumResult = sumFeatureDescriptorsResults(sift, surf, orb, brisk)
    if sumResult == -1:
        return -1
    '''print(sift)
    print(surf)
    print(orb)
    print(brisk)'''
    if sift is not None:
        votes = deepcopy(sift)
        listName = sift
    elif surf is not None:
        votes = deepcopy(surf)
        listName = surf
    elif orb is not None:
        votes =  deepcopy(orb)
        listName = orb
    elif brisk is not None:
        votes =  deepcopy(brisk)
        listName = brisk
        
    for i in range(0,len(listName)):
        votes[i][0] = 0.0
    for i in range(0,len(listName)):
        if sift is not None:
            if votes[i][1] == sift[0][1]:
                votes[i][0] = votes[i][0] + 0.75
            if votes[i][1] == sift[1][1]:
                votes[i][0] = votes[i][0] + 0.5
        
        if surf is not None:
            if votes[i][1] == surf[0][1]:
                votes[i][0] = votes[i][0] + 0.75
            if votes[i][1] == surf[1][1]:
                votes[i][0] = votes[i][0] + 0.5
                
        if orb is not None:     
            if votes[i][1] == orb[0][1]:
                votes[i][0] = votes[i][0] + 0.75
            if votes[i][1] == orb[1][1]:
                votes[i][0] = votes[i][0] + 0.5
            
        if brisk is not None:
            if votes[i][1] == brisk[0][1]:
                votes[i][0] = votes[i][0] + 0.75
            if votes[i][1] == brisk[1][1]:
                votes[i][0] = votes[i][0] + 0.5
                
        if votes[i][1] == sumResult[0][1]:
            votes[i][0] = votes[i][0] + 0.75
        if votes[i][1] == sumResult[1][1]:
            votes[i][0] = votes[i][0] + 0.5
            
    votes.sort(key=lambda x: x[0], reverse=True)
    #print("------")
    
    return votes, sumResult

def charToText(letter, baseImagesPath):
    print("\tSift will measure")
    sift = distanceToBaseImages(letter, baseImagesPath, "SIFT")
    print("\tSurf will measure")
    surf = distanceToBaseImages(letter, baseImagesPath, "SURF")
    print("\tOrb will measure")
    orb = distanceToBaseImages(letter, baseImagesPath, "ORB")
    print("\tBrisk will measure")
    brisk = distanceToBaseImages(letter, baseImagesPath, "BRISK")
    
    print("\Let the votes begin")
    votes, sumResult = vote(sift, surf, orb, brisk)
    if votes == -1:
        print(" - SPACE - ")
    else:
        if votes[0][0] == votes[1][0]:
            answer = sumResult[0][1]
        else:
            answer = votes[0][1]
        
        answer = answer.split("_")
        if answer[1] == "Big":
            print(answer[0].capitalize())
            #print(answer[0].capitalize(), end='')
        else:
            print(answer[0])
            #print(answer[0], end='')

def imgToText(letters, baseImagesPath):
    counter = 0
    for letter in letters:
        counter += 1
        if letter.type == CHARACTER:
            print("Image " + str(counter) + " is a character")
            charToText(letter, baseImagesPath)
        #filename = os.fsdecode(file)
        #if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        #    filename = os.path.join(separatedCharsPath, filename)
        #    charToText(filename, baseImagesPath)
    
if __name__ == '__main__':
    path, filename, ext = getInputFilename("alef.png")
    if os.path.isfile(path):
        letters = getLetters(path)
        if letters is not None:
            directory, separatedLetters = saveLetters(letters, filename, ext)
            print(str(len(letters)) + " letters detected and saved in " + str(directory))
            imgToText(separatedLetters, baseCharsFolder)
        else:
            exit("The selected image has no text")
    else:
        exit("The selected file does not exist")
    
    #eng.rectify('D:/UFRGS/Sexto Semestre/Visao Computacional/IMG_2621.JPG', nargout=0);