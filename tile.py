import pyautogui
import time
import random
import sys

#Represents one individual board tile.

#Note the difference between
#on-screen coordinates (actual pixel location of each tile)
#and virtual coordinates (abstract location of each tile relative to the others)

class Tile:
    def __init__(self, c = (0,0,0,0), s = 0):
        '''Creates a new Tile object.
        Initializes a blank list of the tile's neighbors.

        Parameters:
        c, the on-screen coordinate of the tile; Default (0,0,0,0)
        s, the initial state (dark/light); Default 0 (dark)'''
        self.coord = c
        self.state = s
        self.neighbors = [None]*6
        #Neighbor layout:
        #  1  2 
        #3      4
        #  5  6

    def flip(self):
        '''Flips the Tile's state
        from shadow to light and vice versa.
        This only affects the program's internals,
        not the actual game being played.'''
        self.state = int(not self.state)

    def click(self, waitTime = None):
        '''Clicks on the Tile's on-screen coordinate.
        Waits for some seconds to space out each click,
        instead of all clicks happening instantly.

        Parameters:
        waitTime: if not specified, uses a random waittime;
        If specified, always waits that amount of time.
        (Used for debugging purposes.)
        '''
        if not waitTime: #Randomness makes it look more human?
            waitTime = random.uniform(.05, .1)
        pyautogui.click(x=self.coord[0],y=self.coord[1],interval=waitTime)
        self.flip()
        for n in self.neighbors:
            if n: #if this neighbor is not None
                n.flip()
        
        time.sleep(waitTime)

    def getStateFromScreen(self, img):
        '''Using the Tile's coordinates,
        looks at the screen to get the state of the Tile.
        '''
        #filename = str(time.time())+".png"
        #img = pyautogui.screenshot(region=self.coord) #Will be 25x25 img
        #pixel = img.getpixel((12,12))

        pixel = img.getpixel((self.coord[0]+12, self.coord[1]+12))
        # Each tile is about 25x25 pixels, so add +12 to get the center of the tile
        self.state = int(pixel[1] > 100) #If RGB green value>100, state=1

    def __str__(self):
        return str(self.coord) + " | " + str(self.state)