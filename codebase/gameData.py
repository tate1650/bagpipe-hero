##################################################
# Game Data Analysis for Bagpipe Hero Version 1.0.0
#
# By Tate Mauzy
# (andrewID: tmauzy)
# (Section: G)
##################################################
# Description: This file stores all the data about 
# the sprites in Bagpipe Hero. This includes the 
# bagpipe meter, the notes, and the bar where the 
# player "hits" notes.
##################################################

# pyGame library pip installed. Documentation located at
# https://www.pygame.org/docs/
import pygame

# Creates the BagpipeSprite class, which will contain the bagpipe meter in
# the game
class BagpipeSprite(pygame.sprite.Sprite):
    # Initialize the BagpipeSprite object
    def __init__(self, x, y, size):
        super(BagpipeSprite, self).__init__()
        self.x = x
        self.y = y
        self.size = size
        self.image = pygame.image.load('Images/bagpipeSilhouette.png')
        self.image = pygame.transform.scale(self.image, self.size)
        self.image = self.image.convert_alpha()
        self.rect = pygame.Rect((self.x, self.y), self.size)

    # Creates the update method, which is mainly just a placeholder so it
    # can be blitted onto the game screen
    def update(self):
        self.rect = pygame.Rect((self.x, self.y), self.size)

# Creates the NoteSprite class, which turns information from AnalyzedNote
# objects into usable sprite game data
class NoteSprite(pygame.sprite.Sprite):
    BLUE = (0, 0 , 255)

    # Intializes the NoteSprite object
    def __init__(self, x, y, length, noteValue):
        super(NoteSprite, self).__init__()
        self.color = NoteSprite.BLUE
        self.x = x
        self.y = y
        self.noteValue = noteValue
        self.length = int(length)
        self.size = (self.length, 20)
        self.image = pygame.Surface(self.size)
        self.image = self.image.convert_alpha()
        self.image.fill(self.color)
        self.rect = pygame.Rect((self.x, self.y), self.size)
        pygame.draw.rect(self.image, self.color, ((self.x, self.y), self.size))

    # Updates the note sprite
    def update(self, increment):
        self.x -= increment
        self.rect = pygame.Rect((self.x, self.y), self.size)
        self.image.fill(self.color)

# Creates the HitNoteLine class, which allows for collision detection between
# notes and the note line when a key is pressed
class HitNoteLine(pygame.sprite.Sprite):
    # initialize the HitNoteLine object
    def __init__(self, startPos, endPos):
        super(HitNoteLine, self).__init__()
        self.startPos = startPos
        self.endPos = endPos
        self.x = self.startPos[0]
        self.y = self.startPos[1]
        self.color = (255, 255, 255)
        startY = self.startPos[1]
        endY = self.endPos[1]
        self.height = abs(endY - startY)
        self.size = (5, self.height)
        self.image = pygame.Surface(self.size)
        self.image = self.image.convert_alpha()
        self.rect = pygame.Rect((self.x, self.y), self.size)
        pygame.draw.line(self.image, self.color, self.startPos, self.endPos)

    # Creates the update method, which is mainly just a placeholder so it
    # can be blitted onto the game screen
    def update(self):
        self.rect = pygame.Rect((self.x, self.y), self.size)
        self.image.fill(self.color)