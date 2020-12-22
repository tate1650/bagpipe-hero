##################################################
# Music Analysis for Bagpipe Hero Version 1.0.0
#
# By Tate Mauzy
# (andrewID: tmauzy)
# (Section: G)
##################################################
# NOTICE! This File uses modules that are not supported
# by Python 3.7. As such, you will need to run this
# file (and any file that uses this one) with Python
# 3.6 or earlier. My apologies for the inconvenience.
##################################################
# Description: This file contains all of the 
# code needed to extract and analyze the note and 
# beat data from any and all songs used in Bagpipe
# Hero
##################################################

# wave module pip installed. Documentation for module located at
# https://docs.python.org/3/library/wave.html
import wave
# aubio library pip installed. Documentation for library located at
# https://aubio.org/
from aubio import source, notes, tempo
# pydub library pip installed. Documentation for library located at
# https://pydub.com/
from pydub import AudioSegment

# Creates the AnalyzedNote Object, whose data will later be converted
# into a sprite
class AnalyzedNote(object):
    # Initializes the AnalyzedNote object with its note value and length
    def __init__(self, noteValue, length):
        self.noteValue = noteValue
        self.length = length

    # Creates a repr for the object for debugging purposes
    def __repr__(self):
        return f'{self.noteValue} with length {self.length}'


# Creates the Song Object, which stores music audio files with
# their note data
class Song(object):
    bagpipeScaleDict = {0: 'loG', 1: 'loA', 2: 'B', 3:'C', 4: 'D', 5: 'E',
                            6: 'F', 7: 'hiG', 8: 'hiA'}
    reverseBagpipeScaleDict = {'loG': 1, 'loA': 2, 'B' : 3,'C' : 4, 'D': 5, 
                        'E': 6, 'F': 7, 'hiG': 8, 'hiA': 9}
    # Initalizes the Song by extracting the song and generates note data
    def __init__(self, audioFilePath):
        self.audioFilePath = audioFilePath
        # Please note that audio file must be in .wav format
        self.audioFile = wave.open(self.audioFilePath)
        self.rawNoteAndBeatData = self.extractNotesAndBeats(self.audioFilePath)
        self.rawNotesData = self.rawNoteAndBeatData[:2] 
        self.totalBeats = int(self.rawNoteAndBeatData[2])
        # a length-2 tuple with a dict and a list of notes
        self.noteCountDict, self.notesList = self.rawNotesData
        audioSegment = AudioSegment.from_wav(audioFilePath)
        self.duration = audioSegment.duration_seconds
        self.audioFile.close()

    # Extracts note and bpm data from a song
    def extractNotesAndBeats(self, audioFilePath):
        # Format everything for analysis
        aubioSource = source(audioFilePath)
        sampleRate = aubioSource.samplerate
        hopSize = aubioSource.hop_size
        notesObject = notes()
        tempoObject = tempo()
        framesRead = 0
        noteCountDict = { }
        notesList = [ ]
        totalBeats = 0
        audioSamples, audioRead = aubioSource() 
        # Loop through song and extract all note data
        # And puts note counts into a dictionary
        while audioRead >= hopSize: # Run until you run out of audio to read
            audioSamples, audioRead = aubioSource() 
            noteFrame = notesObject(audioSamples)
            beatSample = tempoObject(audioSamples)[0]
            # noteFrame formatted as a list, [startNote, volume, endNote]
            # where notes are MIDI values
            startNote, endNote = noteFrame[0], noteFrame[2]
            if startNote != 0:
                print(noteFrame)
                # A lot of the note frames are just silence, so check to
                # make sure it isn't 0 before doing anything
                if startNote not in noteCountDict:
                    noteCountDict[startNote] = 0
                if endNote not in noteCountDict:
                    noteCountDict[endNote] = 0
                noteCountDict[startNote] += 1
                noteCountDict[endNote] += 1
                notesList.append(startNote)
                notesList.append(endNote)
            framesRead += audioRead
            if beatSample != 0:
                totalBeats += beatSample
        return (noteCountDict, notesList, totalBeats)


# Initializes the PlayableSong class, which goes through extra note
# data cleaning before being played
class PlayableSong(Song):
    # Intializes the PlayableSong object and cleans up the music data
    # So that it can be played in the game
    def __init__(self, audioFilePath):
        super().__init__(audioFilePath)
        self.totalSongFrags = 0
        self.noteCountDict, self.notesList = self.removeIgnoredNotes(
                                            self.noteCountDict, self.notesList)
        self.bagpipeNotes = self.getMostNotes(self.noteCountDict)
        self.bagpipeNotes = sorted(self.bagpipeNotes)
        self.bagpipeNoteDict = self.buildBagpipeNoteDict()
        self.notesList = self.normalizeNotesList(self.notesList)
        self.analyzedNotes = self.generateNoteObjects(self.notesList)

    # Associates the midi note values extracted from the file with notes
    # on the bagpipe scale
    def buildBagpipeNoteDict(self):
        bagpipeNoteDict = { }
        # get the midi note and map it to the letter value
        for i in range(len(self.bagpipeNotes)):
            midiNote = self.bagpipeNotes[i]
            bagpipeNoteDict[midiNote] = Song.bagpipeScaleDict[i]
        return bagpipeNoteDict

    # Remove background noise notes from the music
    def removeIgnoredNotes(self, noteCountDict, notesList):
        betterNoteCountDict = { }
        for note in noteCountDict:
            if note not in TrainingSong.ignoredNotes:
                betterNoteCountDict[note] = noteCountDict[note]
        for note in notesList:
            if note in TrainingSong.ignoredNotes:
                notesList.remove(note)
        return (betterNoteCountDict, notesList)

    # Removes inconsistencies in the notes list and make all notes
    # fit on our bagpipe scale
    def normalizeNotesList(self, notesList):
        changingVals = False
        for i in range(1, len(notesList) - 1):
            note = notesList[i]
            prevNote = notesList[i - 1]
            nextNote = notesList[i + 1]
            # Leave a little bit of empty space at the beginning
            # For the snare drums before the bagpipes play
            if note in self.bagpipeNotes:
                changingVals = True
            if changingVals:
                noteNotInRange = note not in self.bagpipeNotes
                noteDoesNotMatch = note != prevNote and note != nextNote
                if noteNotInRange or noteDoesNotMatch:
                    if prevNote == nextNote:
                        notesList[i] = prevNote
                    else:
                        notesList[i] = nextNote 
                        # arbitrary choice; a guess
        return notesList

    # gets the 9 notes that occur the most often in the song
    # (that is, the 9 bagpipe notes to be played in the song)
    def getMostNotes(self, noteCountDict):
        mostNotes = [ ]
        totalNotes= sum(noteCountDict.values())
        for note in noteCountDict:
            thresholdCount = totalNotes // 30
            if noteCountDict[note] > thresholdCount:
                # Enough notes to be considered significant
                mostNotes.append(note)
                if len(mostNotes) >= 10:
                    mostNotes.remove(min(mostNotes))
        return mostNotes

    # Generates a list of AnalyzedNote objects for the song to be played
    def generateNoteObjects(self, notesList):
        noteObjectList = [ ]
        prevNoteValue = None
        noteCount = 0
        for note in notesList:
            if prevNoteValue == None or note == prevNoteValue:
                noteCount += 1
            else:
                if prevNoteValue in self.bagpipeNoteDict:
                    # Store letter value and length in an AnalyzedNote object 
                    newNoteObject = AnalyzedNote(
                                self.bagpipeNoteDict[prevNoteValue], noteCount)
                    noteObjectList.append(newNoteObject)
                    self.totalSongFrags += noteCount
                noteCount = 1
            prevNoteValue = note
        return noteObjectList


# Creates subclass TrainingSong, which trains our game and tells
# it which notes not to pay attention to (background noise
# like snare drums and bagpipe drones)
class TrainingSong(Song):
    ignoredNotes = set()
    # Intializes our song and gets the notes the game should ignore
    def __init__(self, audioFilePath):
        super().__init__(audioFilePath)
        self.getIgnoredNotes(self.noteCountDict)

    # Determines which notes should be ignored in the
    # game based off of which
    def getIgnoredNotes(self, noteCountDict):
        totalNotes = sum(noteCountDict.values())
        for note in noteCountDict:
            thresholdCount = totalNotes // 15
            # Makes up more than a certain fraction 
            # of notes in song --> ignore it
            if noteCountDict[note] >= thresholdCount:
                TrainingSong.ignoredNotes.add(note)

# allows songs for game to be trained on command (since it takes a bit of time)
def trainSongs():
    trainingSongPath1 = 'Music/TrainingSongs/10 Drum Salute (Live).wav'
    trainingSongPath2 = 'Music/TrainingSongs/02 Bagpipe Drone a#_Bb.wav'
    trainingSongPath3 = 'Music/TrainingSongs/03 Bagpipe Drone B.wav'
    TrainingSong(trainingSongPath1)
    TrainingSong(trainingSongPath2)
    TrainingSong(trainingSongPath3)

if (__name__ == '__main__'):
    print('This may take a bit...')
    trainSongs()
    playableSongPath = 'Music/PlayableSongs/MacGregor of Rora.wav'
    song = PlayableSong(playableSongPath)
    print(song.analyzedNotes)