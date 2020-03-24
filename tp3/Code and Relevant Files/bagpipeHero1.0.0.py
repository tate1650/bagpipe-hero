##################################################
# Bagpipe Hero Version 1.0.0
#
# A 15-112 Term Project by Tate Mauzy
# (andrewID: tmauzy)
# (Section: G)
##################################################
# Description: This file runs the main Bagpipe
# Hero game. It calls functions from 
# musicAnalysis.py and gameData.py (respectively)
# to gather data about songs played and sprites
# in the game and then converts that data into a
# playable Guitar Hero spinoff with a Scottish
# theme
##################################################

import musicAnalysis as music
from gameData import *
# pyGame library pip installed. Documentation located at
# https://www.pygame.org/docs/
import pygame

# os module came with python installation, but documentation 
# used can be found at https://docs.python.org/3/library/os.html
import os

# random module came with python installation, but documentation
# used can be found at https://docs.python.org/3/library/random.html
import random

# math module came with python installation, but documentation
# used can be found at https://docs.python.org/3/library/random.html
import math

# design of pygame framework starter code acquired and modified 
# from the blog of ex-15-112 TA Lukas Peraza's blog at 
# http://blog.lukasperaza.com/getting-started-with-pygame/. Lines taken from
# this starter code are denoted with "###" at the end.

# Creates the PygameGame class, which will be used to create the
# Bagpipe Hero Game
class PygameGame(object): ###
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GRAY = (150, 150, 150)
    DKGREEN = (15, 135, 35)
    # Dark green (forest green) rgb value acquired from 
    # https://www.htmlcsscolor.com/hex/0F8723

    DKBLUE = (0, 119, 190)
    # Dark blue (ocean boat blue) rgb value acquired from
    # https://www.colorhexa.com/0077be

    YELLOW = (255, 223, 0) 
    # Yellow rgb (gold) value acquired from 
    # https://www.pinterest.com/pin/677510337666738017/

    DKRED = (220, 20, 60)
    # Dark red (crimson) rgb value acquired from 
    # https://www.myidealhome.us/how-to-identify-different-shades-of-red/

    DEEPRED = (180, 0, 0)

    # Return whether a specific key is being held ###
    def isKeyPressed(self, key): ###
        return self._keys.get(key, False) ###

    # Initialize the PyGame game OBJECT
    def __init__(self, width=800, height=600, fps=50, title = 'Game'): ###
        self.width = width ###
        self.height = height ###
        self.fps = fps ###
        self.title = title ###

        self.modes = ['titleMode', 'songChoiceMode', 'gameMode', 
            'helpMode', 'scoreMode', 'enterNameMode']
        self.curMode = 'titleMode'
        pygame.init() ###
        self.score = 0
        self.increaseScore = False
        self.prevNote = None
        self.noteStreak = 0 
        # keeps track of how long a note has collided with the hitNote bar
        self.curMeterHeight = 0
        self.buttonDown = False
        self.buttonColor = PygameGame.GREEN
        self.makeDark = False
        self.songInput = ''
        self.songSelection = ''
        self.displayedSelection = ''
        self.songEntered = False
        self.noSongFound = False
        self.totalScore = 0
        self.increaseTotal = False
        self.startBoxCoords = (0, 0)
        self.startBoxHeight, self.startBoxWidth = (0, 0)
        self.helpBoxCoords= (0, 0)
        self.helpBoxWidth, self.helpBoxHeight = (0, 0)
        self.isPaused = False

    # creates all the NoteSprite objects to be drawn on the screen
    def createNoteSprites(self, songObject):
        rBagpipeNoteDict = songObject.reverseBagpipeScaleDict
        distanceDownScreen = self.screenLength
        lengthPerFragment = self.totalScreenLen / songObject.totalBeats
        for analyzedNote in songObject.analyzedNotes:
            noteSpriteLen = lengthPerFragment * analyzedNote.length
            noteX = distanceDownScreen
            noteSectionHeight = self.height * (3/4)
            heightIncrement = noteSectionHeight / 10
            noteY = (self.height - (heightIncrement / 4) - 
                (rBagpipeNoteDict[analyzedNote.noteValue] * heightIncrement))
            newNoteSprite = NoteSprite(noteX, noteY, noteSpriteLen - 3, 
                        analyzedNote.noteValue) 
            # decreased sprite length slightly to make gap between notes more 
            # obvious
            self.noteSprites.add(newNoteSprite)
            distanceDownScreen += noteSpriteLen 
            # moves x coord to make way for next noteSprite

    # Initializes the gameMode where core gameplay takes place
    def initGameMode(self, screen):
        self.score = 0
        self.curMeterHeight = 0
        self.increaseScore = False
        screen.fill(PygameGame.BLACK)
        loadText = self.gameFont.render(
            'Analyzing your song with Scottish Science, please wait...', 
            True, PygameGame.WHITE)
        screen.blit(loadText, (self.width // 10, self.height // 2))
        pygame.display.flip()
        songPath = f'Music/PlayableSongs/{self.songSelection}'
        analyzedSong = music.PlayableSong(songPath)
        # set the total screen length for the song (used to determine
        # how long each note rectangle will be)
        self.screenLength = self.width * (3/4)
        self.totalScreenLen = (self.screenLength * analyzedSong.duration)
        # Decrease the screen length for hard-code adjustment of note size
        self.totalScreenLen //= 31.5
        self.createNoteSprites(analyzedSong)
        self.backgroundSong = pygame.mixer.Sound(songPath)
        self.backgroundSong.play(loops = 0)

    # Sees if the player got a high score and gets to put their name on
    # the high score board
    def checkForCsvUpdate(self):
        playerScore = self.score
        for player, score in self.csvList:
            if playerScore > int(score): return True
        return False

    # Initializes score mode by resetting the background music and killing
    # all NoteSprites; also checks to see if player got a high score
    def initScoreMode(self, screen):
        if self.totalScore != 0:
            self.percentCorrect = (self.score / self.totalScore) * 100
        else:
            self.percentCorrect = 0
        self.csvList = self.readCsv('playerScores.csv')
        self.noteSprites.empty()
        self.backgroundSong.stop()
        self.backgroundTheme.play(loops = -1)
        if self.checkForCsvUpdate() == True:
            self.curMode = 'enterNameMode'
            self.startGame(screen)

    # Initializes the title screen for the game
    def initTitleMode(self, screen):
        loadText = self.gameFont.render(
                'Loading Bagpipe Hero, please wait...', True, PygameGame.WHITE)
        screen.blit(loadText, (self.width // 4, self.height // 2))
        pygame.display.flip()
        if music.TrainingSong.ignoredNotes == set():
            music.trainSongs()
        themeSong = 'Music/PlayableSongs/Bagpipe Hero Theme.wav'
        # Initialize pygame mixer object for playing music
        pygame.mixer.init()
        self.backgroundTheme = pygame.mixer.Sound(themeSong)
        self.backgroundTheme.play(loops = -1)

    # Initialize the PyGame game SCREEN by making a loading screen and 
    # training the game using the training songs; also begins playing song
    # at the end
    def startGame(self, screen):
        if self.curMode == 'titleMode':
            self.initTitleMode(screen)
        elif self.curMode == 'gameMode':
            self.initGameMode(screen)
        elif self.curMode == 'scoreMode':
            self.initScoreMode(screen)
        elif self.curMode == 'enterNameMode':
            self.playerName = ''
        elif self.curMode == 'songChoiceMode':
            self.songEntered = False
            self.noSongFound = False

    # Check for notes collided with the hit bar on the screen and change
    # Note colors if necessary
    def checkCollidedNotes(self):
        collidedNotes = pygame.sprite.spritecollide(self.hitNoteLine, 
                                            self.noteSprites, False)
        if collidedNotes != [ ]:
            note = collidedNotes[-1]
            if note != self.prevNote:
                self.noteStreak = 0
            self.prevNote = note
            self.noteStreak += 1
            if self.noteStreak > 15 and note.color == PygameGame.BLUE:
                note.color = PygameGame.RED
                self.increaseScore = False

    # Changes the bagpipe meter every time timerFired is called
    def incrementMeter(self):
        if self.buttonDown and self.curMeterHeight > 2:
            self.curMeterHeight -= 2
        elif self.curMeterHeight <= self.maxMeterHeight:
            self.curMeterHeight += 0.2

    # Changes game score and total score as player plays and hits notes
    def adjustScore(self):
        if self.increaseScore == True:
            self.increaseTotal = True
        if self.increaseTotal == True:
            self.totalScore += 1
        # Only increases total score after the notes start colliding

        if (self.increaseScore == True and 
                            self.curMeterHeight < self.maxMeterHeight):
            self.score += 1

    # Makes the fill bag button dark if you are hovering over it
    def makeButtonsDark(self):
        if self.curMeterHeight >= self.maxMeterHeight:
            if self.makeDark == True:
                self.buttonColor = PygameGame.DKRED
            else:
                self.buttonColor = PygameGame.RED
        else:
            if self.makeDark == True:
                self.buttonColor = PygameGame.DKGREEN
            else:
                self.buttonColor = PygameGame.GREEN

    # Updates all the sprites in the game every time the timer is fired
    def timerFired(self, time, screen):
        if self.curMode == 'gameMode':
            if self.isPaused == False:
                self.checkCollidedNotes()

                for group in self.spriteGroups:
                    group.update()
                
                self.adjustScore()
                self.incrementMeter()
                self.makeButtonsDark()
                
                if pygame.mixer.get_busy() == False:
                    self.curMode = "scoreMode"
                    self.startGame(screen)

    # Checks if moving mouse is hovering over the fill bag button
    def mouseMotion(self, x, y):
        if self.curMode == 'gameMode':
            if self.inBounds(x, y, self.boxX, self.boxX + self.boxWidth, 
                                        self.boxY, self.boxY + self.boxHeight):
                self.makeDark = True
            else:
                self.makeDark = False

    # checks if the mouse is over the 'fill bag' box in gameMode
    def inBounds(self, x, y, startX, endX, startY, endY):
        xInBounds = (startX <= x <= endX)
        yInBounds = (startY <= y <= endY)
        return xInBounds and yInBounds

    # Checks if a box was clicked on the screen
    def checkBoxClick(self, x, y, boxX, boxY, boxWidth, boxHeight):
        return self.inBounds(x, y, boxX, boxX + boxWidth, boxY, 
                                                        boxY + boxHeight)

    # Runs the mousePressed method specific to title mode
    def titleModeMousePress(self, x, y, screen):
        # check if 'start' box was clicked
        startX, startY = self.startBoxCoords
        startWidth, startHeight = self.startBoxWidth, self.startBoxHeight
        if self.checkBoxClick(x, y, startX, startY, startWidth, 
                                                            startHeight):
            self.curMode = 'songChoiceMode'
            self.startGame(screen)
        # check if 'help' box was clicked
        helpX, helpY = self.helpBoxCoords
        helpWidth, helpHeight = self.helpBoxWidth, self.helpBoxHeight
        if self.checkBoxClick(x, y, helpX, helpY, helpWidth, helpHeight):
            self.curMode = 'helpMode'

    # Runs the mousePressed Method specific to game mode
    def gameModeMousePress(self, x, y, screen):
        if self.inBounds(x, y, self.boxX, self.boxX + self.boxWidth, 
                                        self.boxY, self.boxY + self.boxHeight): 
            self.buttonDown = True

    # Runs the mousePressed Method specific to help mode
    def helpModeMousePress(self, x, y, screen):
        backButtonX, backButtonY = self.backToTitleRectPos
        backButtonWidth, backButtonHeight = self.backToTitleRectDims
        if self.inBounds(x, y, backButtonX, backButtonX + backButtonWidth,
                            backButtonY, backButtonY + backButtonHeight):
            self.curMode = 'titleMode'

    # Runs the mousePressed Method specific to score mode
    def scoreModeMousePress(self, x, y, screen):
        titleButtonX, titleButtonY = self.returnToTitleRectPos
        titleButtonWidth, titleButtonHeight = self.returnToTitleRectDims
        if self.inBounds(x, y, titleButtonX, 
            titleButtonX + titleButtonWidth, titleButtonY,
            titleButtonY + titleButtonWidth):
            self.curMode = 'titleMode'

    # Runs the mousePressed Method specific to song choice mode
    def songChoiceModeMousePress(self, x, y, screen):
        playButtonX, playButtonY = self.playBoxCoords
        playButtonWidth, playButtonHeight = self.playBoxDims
        if self.inBounds(x, y, playButtonX, playButtonX + playButtonWidth,
                playButtonY, playButtonY + playButtonHeight):
            self.curMode = 'gameMode'
            self.backgroundTheme.stop()
            self.startGame(screen)
            self.songInput = ''
            self.displayedSelection = ''
            self.songSelection = ''

    # checks if fill bag button is being pressed
    def mousePressed(self, x, y, screen):
        if self.curMode == 'titleMode':
            self.titleModeMousePress(x, y, screen)
        elif self.curMode == 'gameMode' and self.isPaused == False:
            self.gameModeMousePress(x, y, screen)
        elif self.curMode == 'helpMode':
            self.helpModeMousePress(x, y, screen)
        elif self.curMode == 'scoreMode':
            self.scoreModeMousePress(x, y, screen)
        elif self.curMode == 'songChoiceMode':
            self.songChoiceModeMousePress(x, y, screen)
                
    # says button is no longer being pressed
    def mouseReleased(self, x, y):
        if self.curMode == 'gameMode':
            self.buttonDown = False

    # Darkens fill bag button if you are hovering over it
    def mouseDrag(self, x, y):
        if self.curMode == 'gameMode':
            if self.inBounds(x, y, self.boxX, self.boxX + self.boxWidth, 
                                        self.boxY, self.boxY + self.boxHeight):
                if self.buttonColor == PygameGame.GREEN: 
                    self.buttonColor = PygameGame.DKGREEN
                elif self.buttonColor == PygameGame.RED:
                    self.buttonColor = PygameGame.DEEPRED

    # Rewrites the csv file with the new high scores
    def writeCsvFile(self, csvList):
        csvString = ''
        for data in csvList:
            for datum in data:
                csvString += datum
                csvString += ','
            csvString = csvString[:-1]
            csvString += '\n'
        csvString = csvString[:-1]
        csvFile = open('playerScores.csv', 'w')
        csvFile.write(csvString)
        csvFile.close()
  
    # Changes the high score csv file to add the new player to it
    def updateCsv(self):
        playerName = self.playerName
        playerScore = self.score
        replaceScore = False
        for i in range(len(self.csvList)):
            opponent, opponentScore = self.csvList[i]
            if playerScore > int(opponentScore):
                # You start with the highest score, so once you have a higher
                # score, then shift the board down, replace and STOP
                newData = [[playerName, str(playerScore)]]
                self.csvList = (
                            self.csvList[:i] + newData + self.csvList[i:-1])
                break
        # rewrite the csv file, too
        self.writeCsvFile(self.csvList)   

    # Gets a random song for the player to play from the 'Music/PlayableSongs'
    # directory
    def getRandomSong(self):
        songList = os.listdir('Music/PlayableSongs')
        while True:
            randomSong = random.choice(songList)
            if randomSong.endswith('.wav'):
                self.songSelection = randomSong
                self.displayedSelection = self.songSelection[:-4]
                # everything except .wav
                self.songEntered = True
                return

    # Checks to see if a song is present in the 'Music/PlayableSongs' directory 
    # and sets the song selection to it if it is present
    def checkForSong(self):
        for fileName in os.listdir('Music/PlayableSongs'):
            # get rid of case sensitivity first, and then check
            namesMatch = self.songInput.lower() in fileName.lower()
            if namesMatch and fileName.endswith('.wav'):
                self.songSelection = fileName
                self.displayedSelection = self.songSelection[:-4]
                # everything except .wav
                self.songEntered = True
                return
        self.songEntered = False
        self.noSongFound = True

    # Changes the colors of notes based on whether notes have been hit
    # correctly or not
    def changeCollidedNotes(self, key, mod, screen):
        asciiToNoteDict = {49: 'loG', 50: 'loA', 51: 'B', 52:'C', 53: 'D', 
                54: 'E', 55: 'F', 56: 'hiG', 57: 'hiA'}
        collidedNotes = pygame.sprite.spritecollide(self.hitNoteLine, 
                                    self.noteSprites, False) 
        if (collidedNotes != [ ]): # line collision with note
            for note in collidedNotes:
                noteNotYetChanged = (note.color == PygameGame.BLUE)
                if noteNotYetChanged:
                    if asciiToNoteDict[key] == note.noteValue:
                        note.color = PygameGame.GREEN
                        self.increaseScore = True
                    else:
                        note.color = PygameGame.RED
                        self.increaseScore = False

    # Runs the keyPressedMethod specifically for game mode
    def gameModeKeyPress(self, key, mod, screen):
        # Check if number key is pressed
        if key in range(49, 58): # ASCII values of number keys 1-9
            self.changeCollidedNotes(key, mod, screen)
        elif key == pygame.K_F1:
            self.curMode = 'scoreMode'
            self.startGame(screen)
        elif key == pygame.K_F2:
            self.score = 3000000
        elif key == pygame.K_x:
            self.curMode = 'titleMode'
            self.score = 0
            self.totalScore = 0
            self.curMeterHeight = 0
            self.backgroundSong.stop()
            self.backgroundTheme.play()
            self.noteSprites.empty()
        elif key == pygame.K_p:
            if self.isPaused == False:
                pygame.mixer.pause()
                self.isPaused = True
            else:
                pygame.mixer.unpause()
                self.isPaused = False

    # Runs the keyPress method specifically for enter name mode
    def enterNameModeKeyPress(self, key, mod, screen):
        if (key in range(97, 123) or key in range(65, 91) or key == 39
                                                                or key == 32):
            # ^^^ Lowercase letters, uppercase letters, apostrophe, or 
            # space, respectively
            character = chr(key)
            shiftPressed = (self.isKeyPressed(pygame.K_LSHIFT)
                        or self.isKeyPressed(pygame.K_RSHIFT))
            if character.isalpha() and shiftPressed == True:
                character = character.upper()
            self.playerName += character
        elif key == pygame.K_RETURN:
            self.updateCsv()
            self.curMode = 'scoreMode'
        elif key == pygame.K_BACKSPACE:
            self.playerName = self.playerName[:-1]

    # Runs the keyPress method specific to song choice mode
    def songChoiceModeKeyPress(self, key, mod, screen):
        if key in range(32, 127): 
            # ^^^ All basic ASCII alphanumeric values and symbols
            character = chr(key)
            shiftPressed = (self.isKeyPressed(pygame.K_LSHIFT)
                        or self.isKeyPressed(pygame.K_RSHIFT))
            if character.isalpha() and shiftPressed == True:
                character = character.upper()
            self.songInput += character
        elif key == pygame.K_BACKSPACE:
            self.songInput = self.songInput[:-1]
        elif key == pygame.K_RETURN:
            if self.songInput == '':
                self.getRandomSong()
            else:
                self.checkForSong()

    # Resets the high scores on the csv file:
    def resetCsv(self):
        resetFile = open('TextFiles/csvResetText.txt', 'r')
        resetText = resetFile.read()
        resetFile.close()
        csvFile = open('playerScores.csv', 'w')
        csvFile.write(resetText)
        csvFile.close()

    # Runs the keyPress method specific to title screen mode
    def titleModeKeyPress(self, key, mod, screen):
        if key == pygame.K_F3:
            self.resetCsv()
            print('High Scores Reset!!')

    # Determines if correct note is pressed and changes note color/score
    # accordingly
    def keyPressed(self, key, mod, screen):
        if self.curMode == 'gameMode':
            self.gameModeKeyPress(key, mod, screen)
        elif self.curMode == 'enterNameMode':
            self.enterNameModeKeyPress(key, mod, screen)
        elif self.curMode == 'songChoiceMode':
            self.songChoiceModeKeyPress(key, mod, screen)
        elif self.curMode == 'titleMode':
            self.titleModeKeyPress(key, mod, screen)

    # draws all the lines and rects on the screen to divide into all
    # the sections of the game screen
    def drawScreenRects(self, screen):
        # draw rect on right hand side for bagpipe meter and score
        (left, top) = (self.width * (3/4), 0)
        (width, height) = self.width * (1/4), self.height
        rightRect = ((left, top), (width, height))
        pygame.draw.rect(screen, PygameGame.DKBLUE, rightRect)
        pygame.draw.rect(screen, PygameGame.WHITE, rightRect, 3)
        # draw rect on top of screen for chanter diagram 
        # (also divides right rect into two segments)
        (left, top) = (0, 0)
        (width, height) = self.width, self.height / 4
        topRect = ((left, top), (width, height))
        pygame.draw.rect(screen, PygameGame.WHITE, topRect, 3)

    # draw lines on screen for note bars and line where player hits notes
    def drawScreenLines(self, screen):
        # draw lines for note bars
        for lineNum in range(1, 11): # for 9 notes
            lineStartX = 0
            lineEndX = self.width * (3/4)
            noteSectionTop = self.height / 4
            self.noteSectionSize = self.height * (3/4)
            lineHeightFactor = lineNum / 10 # 10 sections for 9 lines
            lineY = noteSectionTop + self.noteSectionSize * lineHeightFactor
            startPos = (lineStartX, lineY)
            endPos = (lineEndX, lineY)
            pygame.draw.line(screen, PygameGame.WHITE, startPos, endPos)
        # draw line where player hits notes
        self.hitNoteLineGroup.draw(screen)
    
    # draw numbers by key lines so player knows what keys to press
    def drawNoteKeyNumbers(self, screen):
        numX = 10
        for number in range(1, 10):
            numberText = self.gameFont.render(f'Key {number}', True, 
                                                        PygameGame.WHITE)
            numY = (self.height - self.noteSectionSize * number / 10 - 
                                                            self.height / 50)
            numCoords = (numX, numY)
            screen.blit(numberText, numCoords)

    # draws the box to press to refill the bag with air in the game
    def drawFillBagBox(self, screen):
        # draw box for filling bagpipe with air
        self.boxX = self.width * 0.775
        self.boxY = self.height * 0.85
        self.boxWidth = self.width / 5
        self.boxHeight = self.height / 10
        boxRect = (self.boxX, self.boxY, self.boxWidth, self.boxHeight)
        pygame.draw.rect(screen, self.buttonColor, boxRect)
        # draw text for box telling player to fill the bag
        boxText = self.gameFont.render(f'FILL BAG', True, PygameGame.BLUE)
        self.fillBoxSize = boxText.get_size()
        self.boxTextCoords = (self.width * (4/5), self.height * 0.88)
        screen.blit(boxText, self.boxTextCoords)

    # draw yellow lines of the the tartan plaid on the title screen
    def drawYellowLines(self, screen, rows, cols, squareSize):
        horizYelLines = rows // 2
        horizYelLineInc = self.height / horizYelLines
        for horizYelLine in range(horizYelLines):
            horizYelLineY = horizYelLineInc * horizYelLine
            startPos = (0, horizYelLineY + (squareSize / 2))
            endPos = (self.width, horizYelLineY + (squareSize / 2))
            pygame.draw.line(screen, PygameGame.YELLOW, startPos, endPos, 3)
        vertYelLines = cols // 2
        vertYelLineInc = squareSize * 2
        for vertYelLine in range(vertYelLines):
            vertYelLineX = (squareSize / 2) + vertYelLineInc * vertYelLine
            startPos = (vertYelLineX, 0)
            endPos = (vertYelLineX, self.height)
            pygame.draw.line(screen, PygameGame.YELLOW, startPos, endPos, 3)

    # Draws the checked tartan pattern on the title screen
    def drawCheckedPattern(self, screen, rows, cols, squareSize):
        colorList = [PygameGame.DKGREEN, PygameGame.DKBLUE]
        for row in range(rows):
            for col in range(cols):
                colorIndex = (row + col) % 2
                squareRect = (squareSize * col, squareSize * row, squareSize, 
                                                                squareSize)
                pygame.draw.rect(screen, colorList[colorIndex], squareRect)

    # Draws the red lines on the tartan pattern on the title screen
    def drawRedLines(self, screen, rows, cols, squareSize):
        horizRedLinePairs = rows
        horizRedLineInc = squareSize
        for horizRedLinePair in range(horizRedLinePairs):
            horizRedLineY1 = ((squareSize / 3) + 
                                            horizRedLineInc * horizRedLinePair)
            startPos1 = (0, horizRedLineY1)
            endPos1 = (self.width, horizRedLineY1)
            pygame.draw.line(screen, PygameGame.DKRED, startPos1, endPos1, 3)
            horizRedLineY2 = ((squareSize * (2/3)) + 
                                            horizRedLineInc * horizRedLinePair)
            startPos2 = (0, horizRedLineY2)
            endPos2 = (self.width, horizRedLineY2)
            pygame.draw.line(screen, PygameGame.DKRED, startPos2, endPos2, 3)

        vertRedLinePairs = cols
        vertRedLineInc = squareSize 
        for vertRedLinePair in range(vertRedLinePairs):
            vertRedLineX1 = ((squareSize / 3) + 
                                            vertRedLineInc * vertRedLinePair)
            startPos1 = (vertRedLineX1, 0)
            endPos1 = (vertRedLineX1, self.height)
            pygame.draw.line(screen, PygameGame.DKRED, startPos1, endPos1, 3)
            vertRedLineX2 = ((squareSize * (2/3)) + 
                                            vertRedLineInc * vertRedLinePair)
            startPos2 = (vertRedLineX2, 0)
            endPos2 = (vertRedLineX2, self.height)
            pygame.draw.line(screen, PygameGame.DKRED, startPos2, endPos2, 3)

    # Draw boxes for the button text on the title screen
    def drawTextBoxes(self, screen):
        self.startBoxCoords = (self.width * (37/100), self.height * (47/100))
        self.startBoxWidth = self.width * (24/100)
        self.startBoxHeight = self.height / 10
        startBoxDims = (self.startBoxWidth, self.startBoxHeight)
        startBoxRect = (self.startBoxCoords, startBoxDims)
        pygame.draw.rect(screen, PygameGame.GRAY, startBoxRect)
        self.helpBoxCoords = (self.width * (23/100), self.height * (72/100))
        self.helpBoxWidth = self.width * (53 / 100)
        self.helpBoxHeight = self.height / 10
        helpBoxDims = (self.helpBoxWidth, self.helpBoxHeight)
        helpBoxRect = (self.helpBoxCoords, helpBoxDims)
        pygame.draw.rect(screen, PygameGame.GRAY, helpBoxRect)

    # draw the text of the title screen
    def drawTitleText(self, screen):
        welcomeMsg = self.bigFont.render('Welcome to Bagpipe Hero!', True, 
                                                            PygameGame.WHITE)
        welcomeCoords = ((self.width / 4) - (self.width / 100),
                                                             self.height / 6)
        screen.blit(welcomeMsg, welcomeCoords)
        myName = self.gameFont.render('A 15-112 Term Project by Tate Mauzy',
                                                        True, PygameGame.WHITE)
        nameCoords = (self.width / 4, self.height / 4)
        screen.blit(myName, nameCoords)
        self.startMsg = self.gameFont.render('Start Game!', True, 
                                                            PygameGame.BLACK)
        self.startCoords = (self.width * (4/10), self.height / 2)
        screen.blit(self.startMsg, self.startCoords)
        self.helpMsg = self.gameFont.render('Help and More Info on Bagpiping',
                                                        True, PygameGame.BLACK)
        self.helpCoords = (self.width / 4, self.height * (3/4))
        screen.blit(self.helpMsg, self.helpCoords)

    # draws the title screen for Bagpipe Hero
    def drawTitleScreen(self, screen):
        self.drawTartanPlaid(screen)
        self.drawTextBoxes(screen)
        self.drawTitleText(screen)

    # Draws an informative diagram of the bagpipe on the help screen
    def drawBagpipeDiagram(self, screen):
        size = (self.width // 4, self.height // 3)
        diagramCoords = (self.width * (73/100), self.height / 6)
        bagpipeDiagram = pygame.image.load('Images/bagpipeDiagram.jpg')
        bagpipeDiagram = pygame.transform.scale(bagpipeDiagram, size)
        screen.blit(bagpipeDiagram, diagramCoords)

    # draws the contents of a text file onto the screen in pygame
    def drawTextFile(self, screen, filePath, startY, color = BLACK):
        infoTextFile = open(filePath, 'r')
        infoText = infoTextFile.read()
        infoTextFile.close()
        splitText = infoText.splitlines()
        for i in range(len(splitText)):
            line = splitText[i]
            textline = self.smallFont.render(line, True, color)
            x = self.width / 10
            yInc = (self.height * (1/30)) * i
            y = startY + yInc
            coords = (x, y)
            screen.blit(textline, coords)

    # Writes more information about playing the bagpipes in general
    def drawMoreInfo(self, screen):
        aboutBagpipesText = self.gameFont.render('More Info on Bagpipes', True,
                                                            PygameGame.BLACK)
        aboutBagpipesCoords = (self.width / 10, self.height / 20)
        screen.blit(aboutBagpipesText, aboutBagpipesCoords)
        startY = self.height / 10
        self.drawTextFile(screen, 'TextFiles/howToPlayBagpipes.txt', startY)

    # Writes information on how to play the game on the screen
    def drawHowToPlay(self, screen):
        howToPlayText = self.gameFont.render('How To Play The Game', True,
                                                            PygameGame.BLACK)
        howToPlayCoords = (self.width / 10, self.height / 2)
        screen.blit(howToPlayText, howToPlayCoords)
        startY = self.height * (55/100)
        self.drawTextFile(screen, 'TextFiles/howToPlayGame.txt', startY)

    # Draws keyboard diagram to help players develop finger placement strategy
    def drawKeyboardDiagram(self, screen):
        size = ((self.width * 3) // 8, (self.height * 3) // 16)
        diagramCoords = (self.width * (60/100), self.height * (57/100))
        keyboardDiagram = pygame.image.load('Images/keyboardDiagram.png')
        keyboardDiagram = pygame.transform.scale(keyboardDiagram, size)
        screen.blit(keyboardDiagram, diagramCoords)

    # Draws the help screen that players can access from the start screen
    def drawHelpScreen(self, screen):
        self.drawTartanPlaid(screen)
        # Draw gray background to make help text more readable
        backgroundRectCoords = (self.width / 15, self.height / 25)
        backgroundRectDims = (self.width * (65/100), self.height * (95/100))
        backgroundRect = (backgroundRectCoords, backgroundRectDims)
        pygame.draw.rect(screen, PygameGame.GRAY, backgroundRect)
        self.drawBagpipeDiagram(screen)
        self.drawMoreInfo(screen)
        self.drawHowToPlay(screen)
        self.backToTitleRectPos = (self.width * (73/100), self.height * (4/5))
        self.backToTitleRectDims = (self.width / 4, self.height / 10)
        backToTitleRect = (self.backToTitleRectPos, self.backToTitleRectDims)
        pygame.draw.rect(screen, PygameGame.GRAY, backToTitleRect)
        backToTitleText = self.gameFont.render('Back to Title', True, 
                                                            PygameGame.BLACK)
        backToTitleCoords = (self.width * (76/100), self.height * (83/100))
        screen.blit(backToTitleText, backToTitleCoords)
        self.drawKeyboardDiagram(screen)

    # Draws plaid background for title and help screens
    def drawTartanPlaid(self, screen, rows = 6, cols = 8):
        sqWidth = self.width / cols
        self.drawCheckedPattern(screen, rows, cols, sqWidth)
        self.drawRedLines(screen, rows, cols, sqWidth)
        self.drawYellowLines(screen, rows, cols, sqWidth)

    # Draws the bagpipe meter on the screen
    def drawBagpipeMeter(self, screen):
        # draw the bagpipe sprite
        self.bagpipes.draw(screen)
        # draw blue rect over bagpipe meter
        meterX = self.bagpipeX
        meterY = self.bagpipeY
        meterWidth = self.bagpipeMeter.size[0] # meter width
        meterHeight = self.curMeterHeight
        meterRect = (meterX, meterY, meterWidth, meterHeight)
        pygame.draw.rect(screen, PygameGame.DKBLUE, meterRect)

    # Draws the gameplay screen
    def drawGameScreen(self, screen):
        # draw the note lines on the screen
        self.drawScreenLines(screen)
        # draw the notes under the skeleton of the screen
        self.noteSprites.draw(screen)
        # draw numbers by key lines so player knows what keys to press
        self.drawNoteKeyNumbers(screen)
        # draw all the rects that make the bare game screen
        self.drawScreenRects(screen)
        # draw the score
        scoreText = self.gameFont.render(f'Score: {self.score}', True, 
                                                        PygameGame.WHITE)
        textCoords = (self.width * (4/5), self.height * 0.1)
        screen.blit(scoreText, textCoords)
        self.drawFillBagBox(screen)
        self.drawBagpipeMeter(screen)
        quitMsg = self.gameFont.render('Press "x" to quit', True, 
                                                            PygameGame.WHITE)
        quitCoords = (self.width / 5, self.height * (5/100))
        screen.blit(quitMsg, quitCoords)
        pauseMsg = self.gameFont.render('Press "p" to pause and unpause', True, 
                                                            PygameGame.WHITE)
        pauseCoords = (self.width / 5, self.height / 10)
        screen.blit(pauseMsg, pauseCoords)
        if self.isPaused == True:
            pausedText = self.bigFont.render('PAUSED', True, PygameGame.WHITE)
            pausedTextCoords = (self.width * (4/10), self.height / 2)
            screen.blit(pausedText, pausedTextCoords)

    # Reads a csv file and returns its contents as a list
    @staticmethod
    def readCsv(csvPath):
        csvFile = open(csvPath, 'r')
        csvText = csvFile.read()
        csvFile.close()
        resultList = []
        for line in csvText.splitlines():
            data = ()
            for item in line.split(','):
                data += (item, )
            resultList.append(data)
        return resultList    

    # Draws the game high scores on the screen
    def drawHiScores(self, screen):
        hiScore = self.gameFont.render('High Scores:', True, PygameGame.WHITE)
        hiScorePos = (self.width * (4/10), self.height * (28/100))
        screen.blit(hiScore, hiScorePos)
        hiScoreRectPos = (self.width / 6, self.height / 3)
        hiScoreRectDims = (self.width * (2/3), self.height * (1/2))
        hiScoreRect = (hiScoreRectPos, hiScoreRectDims)
        pygame.draw.rect(screen, PygameGame.GRAY, hiScoreRect)
        for i in range(len(self.csvList)):
            dataList = self.csvList[i]
            player, score = dataList
            playerText = self.gameFont.render(player, True, PygameGame.BLACK)
            playerXPos = self.width / 5
            playerYInc = (self.height / 12) * i
            playerYPos = self.height * (4/10) + playerYInc
            playerTextPos = (playerXPos, playerYPos)
            scoreText = self.gameFont.render(score, True, PygameGame.BLACK)
            scoreXPos = self.width * (2/3)
            scoreYPos = playerYPos
            scoreTextPos = (scoreXPos, scoreYPos)
            screen.blit(playerText, playerTextPos)
            screen.blit(scoreText, scoreTextPos)

    # Draws the player's score and their stats on the screen
    def drawResults(self, screen):
        scorePos = (self.width * (35/100), self.height / 6)
        scoreText = self.gameFont.render(f'Your Score Was: {self.score}', 
                                                        True, PygameGame.WHITE)
        screen.blit(scoreText, scorePos)
        percentCorrectText = self.gameFont.render(
                'Percent Correct: %0.0f!' % self.percentCorrect, True,
                                                            PygameGame.WHITE)
        percentCorrectCoords = (self.width * (36/100), self.height * (22/100))
        screen.blit(percentCorrectText, percentCorrectCoords)

    # Draws the player's score results, stats, and high scores on the screen
    def drawScore(self, screen):
        levelCompletePos = (self.width / 3, self.height / 10)
        levelCompleteText = self.bigFont.render('Song Complete!', True,
                                                            PygameGame.WHITE)
        screen.blit(levelCompleteText, levelCompletePos)
        self.drawResults(screen)
        self.drawHiScores(screen)

    # Draw the post-level screen where the player can see their score
    def drawScoreScreen(self, screen):
        self.drawTartanPlaid(screen)
        self.drawScore(screen)
        self.returnToTitleRectPos = (self.width * (35/100), 
                                                        self.height * (86/100))
        self.returnToTitleRectDims = (self.width * (32/100), self.height / 10)
        returnToTitleRect = (self.returnToTitleRectPos, 
                                                    self.returnToTitleRectDims)
        pygame.draw.rect(screen, PygameGame.GRAY, returnToTitleRect)
        returnText = self.gameFont.render('Return To Title', True,
                                                        PygameGame.BLACK)
        textPos = (self.width * (39/100), self.height * (89/100))
        screen.blit(returnText, textPos)

    # Draws the name writing screen for when players get a high score
    def drawNameScreen(self, screen):
        self.drawTartanPlaid(screen)
        congratsText = self.bigFont.render('CONGRATULATIONS!', True, 
                                                            PygameGame.WHITE)
        congratsCoords = (self.width / 3, self.height / 10)
        screen.blit(congratsText, congratsCoords)
        infoText = self.gameFont.render(
            ' You earned a place on the high score board! ', True, 
                                                            PygameGame.WHITE)
        infoTextCoords = (self.width / 5, self.height / 6)
        screen.blit(infoText, infoTextCoords)
        enterName = self.gameFont.render(
            'Please Enter Your Name. Press Enter to Submit', True, 
                                                            PygameGame.WHITE)
        enterNameCoords = (self.width / 5, self.height / 4)
        screen.blit(enterName, enterNameCoords)
        name = self.gameFont.render(f'Your Name: {self.playerName}', True,
                                                            PygameGame.WHITE)
        nameOffsetFactor = (50 - len(self.playerName)) / 100
        nameCoords = (self.width * nameOffsetFactor, self.height / 2)
        screen.blit(name, nameCoords)

    # Draws instructions for choosing a song to play
    def drawChoiceInstructions(self, screen):
        selectSongText = self.bigFont.render('Choose a song to play!', True,
                                                            PygameGame.WHITE)
        selectSongCoords = (self.width / 10, self.height / 10)
        screen.blit(selectSongText, selectSongCoords)
        instructionsRectCoords = (self.width * (8/100), self.height * (16/100))
        instructionsRectDims = (self.width * (2/3), self.height * (48/100))
        instructionsRect = (instructionsRectCoords, instructionsRectDims)
        pygame.draw.rect(screen, PygameGame.GRAY, instructionsRect)
        self.drawTextFile(screen, 'TextFiles/songChoiceInstructions.txt', 
                                    self.height / 6)

    # Draws the confirmation part of the screen so player can start the game
    def drawSongChoiceConfirmation(self, screen):
        choiceRectCoords = (self.width * (8/100), self.height * (70/100))
        choiceRectDims = (self.width * (2/3), self.height * (1/9))
        choiceRect = (choiceRectCoords, choiceRectDims)
        pygame.draw.rect(screen, PygameGame.GRAY, choiceRect)
        songSelectionText = self.smallFont.render(
            f'You Selected: {self.displayedSelection}', True, 
                                                        PygameGame.BLACK)
        songSelectionCoords = (self.width / 10, self.height * (7/10))
        screen.blit(songSelectionText, songSelectionCoords)
        self.playBoxCoords = self.width / 10, self.height * (85/100)
        self.playBoxDims = self.width / 6, self.height / 12
        playBoxRect = (self.playBoxCoords, self.playBoxDims)
        pygame.draw.rect(screen, PygameGame.GRAY, playBoxRect)
        changeText = self.smallFont.render(
            'To change the song, just resubmit your song choice!', True,
                                                        PygameGame.BLACK)
        changeCoords = self.width / 10, self.height * 75/100
        screen.blit(changeText, changeCoords)
        playText = self.gameFont.render('Play!', True, PygameGame.BLACK)
        playCoords = self.width * (15/100), self.height * (88/100)
        screen.blit(playText, playCoords)

    # draws the song choice screen where the player selects a song to play
    def drawSongChoiceScreen(self, screen):
        self.drawTartanPlaid(screen)
        self.drawChoiceInstructions(screen)
        songInputText = self.gameFont.render(
                    f'Your Song: {self.songInput}', True, PygameGame.WHITE)
        songInputCoords = (self.width / 10, self.height * (65/100))
        screen.blit(songInputText, songInputCoords)
        if self.songEntered == True:
            self.drawSongChoiceConfirmation(screen)
        elif self.noSongFound == True:
            noSongFoundText = self.gameFont.render(
                f"Sorry, we couldn't find that. Try entering a name again.",
                                                        True, PygameGame.WHITE)
            noSongFoundCoords = self.width / 10, self.height * (8/10)
            screen.blit(noSongFoundText, noSongFoundCoords)

    # draws all the vital components of the game screen
    def redrawAll(self, screen):
        if self.curMode == 'titleMode':
            self.drawTitleScreen(screen)
        elif self.curMode == 'gameMode':
            self.drawGameScreen(screen)
        elif self.curMode == 'helpMode':
            self.drawHelpScreen(screen)
        elif self.curMode == 'scoreMode':
            self.drawScoreScreen(screen)
        elif self.curMode == 'enterNameMode':
            self.drawNameScreen(screen)
        elif self.curMode == 'songChoiceMode':
            self.drawSongChoiceScreen(screen)

    # Initialize all the groups, some sprites, game font, and other 
    # related data
    def initializeGameData(self):
        # Initialize the text font used in the game
        self.gameFont = pygame.font.Font('FontFiles/RomanUncialModern.ttf', 24)
        self.bigFont = pygame.font.Font('FontFiles/RomanUncialModern.ttf', 35)
        self.smallFont = pygame.font.SysFont('georgia', 15)

        # Intialize the sprite groups in the game
        self.noteSprites = pygame.sprite.Group()
        self.bagpipes = pygame.sprite.Group()
        self.hitNoteLineGroup = pygame.sprite.Group()

        # Create bagpipe meter sprite
        self.bagpipeX = self.width * 0.76
        self.bagpipeY = self.height / 2
        bagpipeSize = ((self.width * 23) // 100, self.height // 3)
        self.bagpipeMeter = BagpipeSprite(self.bagpipeX, self.bagpipeY, 
                                                                bagpipeSize)
        self.bagpipes.add(self.bagpipeMeter)

        self.spriteGroups = [self.bagpipes, self.noteSprites, 
                        self.hitNoteLineGroup]
        
        # set height of bagpipe meter (for changing len of rect that covers it)
        self.maxMeterHeight = self.bagpipeMeter.size[1] # the rect height

        # Create hitNoteLineSprite
        startPos = ((self.width / 10), (self.height / 4))
        endPos = ((self.width / 10), self.height)
        self.hitNoteLine = HitNoteLine(startPos, endPos)
        self.hitNoteLineGroup.add(self.hitNoteLine)

    def reactToEvents(self, screen):
        for event in pygame.event.get(): ###
            if (event.type == pygame.MOUSEBUTTONDOWN and 
                                                    event.button == 1): ###
                self.mousePressed(*(event.pos), screen) ###
            elif (event.type == pygame.MOUSEBUTTONUP and 
                                                    event.button == 1): ###
                self.mouseReleased(*(event.pos)) ###
            elif (event.type == pygame.MOUSEMOTION and
                    event.buttons == (0, 0, 0)): ###
                self.mouseMotion(*(event.pos)) ###
            elif (event.type == pygame.MOUSEMOTION and
                    event.buttons[0] == 1): ###
                self.mouseDrag(*(event.pos)) ###
            elif event.type == pygame.KEYDOWN: ###
                self._keys[event.key] = True ###
                self.keyPressed(event.key, event.mod, screen) ###
            elif event.type == pygame.KEYUP: ###
                self._keys[event.key] = False ###
            elif event.type == pygame.QUIT: ###
                return False # playing == False
        return True

    # Runs the Pygame game
    def run(self): ###
        clock = pygame.time.Clock() ###
        screen = pygame.display.set_mode((self.width, self.height)) ###
        # set the title of the window ###
        pygame.display.set_caption(self.title) ###

        self.initializeGameData()
        # load the song and initialize the game screen
        self.startGame(screen)

        # stores all the keys currently being held down ###
        self._keys = dict() ###

        playing = True ###
        while playing: ###
            time = clock.tick(self.fps) ###
            self.timerFired(time, screen) ###
            playing = self.reactToEvents(screen)
            screen.fill(PygameGame.DKBLUE)
            self.redrawAll(screen) ###
            pygame.display.flip() ###

        pygame.quit() ###

if __name__ == '__main__':
    bagpipeHeroGame = PygameGame(title = 'Bagpipe Hero (v1.0.0)')
    bagpipeHeroGame.run()