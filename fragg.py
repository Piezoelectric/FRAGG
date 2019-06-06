import pyautogui
import time
import random
import pyautogui_ext
import sys

#This one uses pyautogui_extensions,
#available in my github 

#Basically there are two "games" being played
#One is the on-screen game, on FR's actual website,
#that you interact with by clicking on-screen

#The other is internal to the python program
#And is played automatically within the program

#We separate these because it's slower if it has to read from the screen
#every time it wants to do something.
#with the game in internal memory,
#the program can work much faster 
#since it doesn't have to work as hard to access memory
#as it does with screen

#There is also a difference between
#on-screen coordinates (actual pixel location of each tile)
#and virtual coordinates
#(abstract location of each tile relative to the others)

#Represents one individual board tile.
class Tile:
    def __init__(self, c = (0,0,0,0), s = 0):
        '''Creates a new Tile object.
        Initializes a blank list of the tile's neighbors.

        Parameters:
        c, the on-screen coordinate of the tile
        Default (0,0,0,0)
        s, the initial state (dark/light)
        Default 0 (dark)'''
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
            waitTime = random.uniform(.1, .25) 
        pyautogui_ext.wiggleClick(self.coord[0],self.coord[1], waitTime)
        self.flip()
        for n in self.neighbors:
            if n: #if this neighbor is not None
                #print("[Tile.click] Flipping neighbor", n)
                n.flip()
        
        time.sleep(waitTime)

    def getStateFromScreen(self):
        '''Using the Tile's coordinates,
        looks at the screen to get the state of the Tile.
        '''
        #filename = str(time.time())+".png"
        img = pyautogui.screenshot(region=self.coord) #Will be 25x25 img
        pixel = img.getpixel((12,12))
        self.state = int(pixel[1] > 100) #If green>100 state=1

    def __str__(self):
        return str(self.coord) + " | " + str(self.state)

#Implementation of the "program-internal game"
#Maybe will move these into a separate file
#And make them not a class

#States are kind of as follows:
#Game region on screen not found yet/Game() not fully initialized
#Game region on screen found, and we're in the "Play Again?" game loop

class Game:
    def __init__(self):
        '''Initialize the program-internal game.

        The program internal game uses coordinates as described in hexutil.py:
        Odd rows have offset columns (e.g. (-3, -1));
        Even rows do not (e.g. (-2,0)).
        a Tile's row+col should be an even number
        '''
        #use a dict-of-dicts to allow negative indices
        #Dicts-of-dicts are slow but allow unambiguous internal coordinates
        self.board = {
            -3: {},
            -2: {},
            -1: {},
            0: {},
            1: {},
            2: {},
            3: {}
            }
        self.rowLengths = {
            -3: 4,
            -2: 5,
            -1: 6,
            0: 7,
            1: 6,
            2: 5,
            3: 4
            }
        #MAGIC CONSTANTS--MODIFY HERE
        self.tileWidth = 60                 #Width of each tile
        self.rowOffset = 53                 #Pixel diff between each row
        self.colOffset = self.tileWidth/2   #Column offset for switching rows
        #Since the row above and below are offset by half a tile

    def getRowStates(self, i):
        '''Returns the state of every tile in a given row i.
        Implemented because dicts aren't directly iterable.
        '''
        row = self.board[i]
        tileStates = []
        for j in row.keys():
            tileStates.append(self.board[i][j].state)
        return tileStates

    def __str__(self):
        retval = ""
        for rowKey in self.board.keys():
            retval += ("Row [" + str(rowKey) + "]: ")
            retval += str(self.getRowStates(rowKey))
            retval += "\n"
        return retval
    
    #Click on the "play game" button then the "hard" button
    def launchGame(self):
        '''From the main menu, clicks the "play game" button,
        and identifies the region on-screen
        where the game is played.'''
        
        #playRegion = pyautogui_ext.safeLocateOnScreen("PlayGame.png")
        playRegion = pyautogui.locateOnScreen("PlayGame.png", minSearchTime = 5)
        if playRegion == None:
            print("Play Game button couldn't be found. Exiting")
            return False
                
        self.gameRegion = (playRegion[0]-295, #MAGIC CONSTANTS
                           playRegion[1]-320,
                           700,
                           600)
        #pyautogui.screenshot("test.png", gameRegion)
        pyautogui.click(playRegion[0], playRegion[1])
        #time.sleep(.25)
        #hardRegion = pyautogui_ext.safeLocateOnScreen("hard.png")
        hardRegion = pyautogui.locateOnScreen("hard.png", minSearchTime = 5)
        if hardRegion == None:
            print("Hard button couldnt be found. exiting")
            return False
        pyautogui.click(hardRegion[0], hardRegion[1])
        #time.sleep(.25)

        return True

    #Calculate coordinates of each tile
    def createTiles(self):
        '''Creates Tiles.
        1) initializes the Game's internal Board object with Tile objects.
        2) sets the on-screen coordinates for each Tile,
        using the gameRegion to calculate them.

        Should initialize gameRegion with launchGame() first.
        This should only be run once at the start of the program,
        NOT run for every iteration of the loop
        '''
        #Centermost tile (0,0) gives an anchor point
        centerTileCoord = (self.gameRegion[0]+338, #MAGIC CONSTANTS
                         self.gameRegion[1]+298,
                         25,
                         25)
        #print("centerTileCoord", centerTileCoord)

        #Gets the row we're on
        for i, row in enumerate(self.board, start=-3):
            rowBase = (centerTileCoord[0],
                       centerTileCoord[1] + self.rowOffset*(i),
                       0,
                       0)
            #print("rowbase", rowBase)

            rowParity = i%2
            #Rows in hexgrid are offset, some use even X vals only
            #Even rows (even y vals) -> even x vals
            
            #Gets the column we're on;
            #Number of columns per row varies
            rowLen = self.rowLengths[i]
            for j in range(-rowLen+1, rowLen, 2):#step by 2 to match virtual grid
                offset = rowParity * -1 * self.colOffset
                #If rowParity = 1, row is offset; push the offset left

                #Int as floor(), needed on odd rows s.t. len/2 isn't decimal
                #c = (rowBase[0] + int(self.tileWidth*j/2) + offset,
                c = (rowBase[0] + int(self.tileWidth*j/2),
                     rowBase[1],
                     25,
                     25)
                self.board[i][j] = Tile(c)
                #print("[Game.createTiles]", i, j, c)
                #print(c)

    #Link each tile to its neighbors
    def linkTiles(self):
        '''
        Links each Tile object to its neighbors.
        Needed bc if a Tile is clicked,
        its state changes,
        and all its neighbors' states change too.
        '''
        for i in self.board.keys():
            row = self.board[i] #References...
            for j in row.keys():
                til = row[j]
                #POTENTIAL neighbors --not all of these are valid
                #Depending on where the tile is on the board
                potentialNeighbors = [ (i-1, j-1), #up-left
                                       (i-1, j+1), #up-right
                                       (i, j-2), #same-row-left
                                       (i, j+2), #same-row-right
                                       (i+1, j-1), #lower-left
                                       (i+1, j+1) #lower-right
                                       ]

                #Try to assign tiles
                for k, neighbor in enumerate(potentialNeighbors):
                    success = None
                    try:
                        til.neighbors[k] = self.board[neighbor[0]][neighbor[1]]
                        success = True
                    except KeyError as e: #Gross, but it uses less code
                        success = False
                    #print("[Game.linkTiles] Tile", i, j, "Attempt Neighbor", neighbor,
                    #      "succeeded" if success else "failed")
                

    def getStateFromScreen(self):
        '''Using coordinates of each tile,
        Extract game state from screen (which tiles are light, which are shadow)'''
        for i in self.board.keys():
            row = self.board[i]
            for j in row.keys():
                self.board[i][j].getStateFromScreen()
                #print(self.board[i][j])

    def _shiftTile(self, i, j, right=False):
        '''Shifts the Tile with virtual grid coordinates (i,j).
        Shift a tile in rowA by clicking the tile underneath it in rowA+1
        #Left by default
        '''
        #TODO -- another way we could do this
        #Is by using the linked tile notion
        #Get tile.neighbors[4] and click it
        row = i+1
        col = j+1 if right else j-1
        success = None
        try:
            self.board[row][col].click()
            success = True
        except KeyError as e:
            success = False
        #print("[Game._shiftTile] shifting tile", "right" if right else "left",
        #      "by clicking (", row, col, ");",
        #      "success" if success else "failure")

    def solveRow(self, r):
        '''In a row r, uses a faster method (not bubblesort)
        to solve the row.
        (Solving: Eliminates as many light tiles as possible,
        pushes the tiles it can't eliminate to the right edge.)
        '''

        rowActive = True
        while rowActive:
            firstLightTileCol = None
            #Search for the first light tile in the row,
            #Remember its coordinates too
            columns = list(g.board[r].keys())
            for col in columns:
                tempTile = g.board[r][col]
                if tempTile.state == 1:
                    firstLightTileCol = col
                    break

            #No light tile was found in the row--exit
            if firstLightTileCol == None:
                print("No light tile was found in row", r, "; go to next row")
                rowActive = False
            else: #Else, a light tile exists:
                tempLightTile = g.board[r][firstLightTileCol]
                #But maybe this light tile is already on the right edge
                #and can't be eliminated
                if tempLightTile.neighbors[5] == None:
                    print("Last light tile in row", r, "is on right edge;",
                          "go to next row")
                    rowActive = False
                else:
                    print("Shifting or eliminating tile", r, firstLightTileCol)
                    g._shiftTile(r, firstLightTileCol, right=True)

    def replay(self):
        #playAgain = pyautogui_ext.safeLocateOnScreen("playAgain.png",
        #                                             region=self.gameRegion)
        playAgain = pyautogui.locateOnScreen("playAgain.png", minSearchTime = 5)
        if playAgain == None:
            print("Play Again button was not found.",
                  "This is eventually where the game will re-read the screen",
                  "and try to play the game, corrected with new screen data.")
            return False
        
        pyautogui_ext.wiggleClick(playAgain[0], playAgain[1])
        
#====
#main
#====

numGames = 21
#From 0 luckstreak, is 47 games

g = Game()
launched = g.launchGame()
if not launched:
    sys.exit()

g.createTiles()
g.linkTiles()
print(g)

for i in range(numGames):
    print("[Main] Beginning game", i, "/", numGames)
    time.sleep(3) #Wait for game to load
    g.getStateFromScreen()
    print("[Main] Initial board state")
    #First iteration
    print(g)
    for r in range(-3,4):
        #g.formPairs(i)
        #g.elimPairs(i)
        g.solveRow(r)
    print(g)
    #Click relevant tiles for iteration 2
    lastRowState = g.getRowStates(3)
    #Remember we're using list indxes here, not grid coords
    if lastRowState[0] == 1:
        print("Tile A == 1, flipping")
        g.board[-3][-3].click()
    if lastRowState[1] == 1:
        print("Tile B == 1, flipping")
        g.board[-3][-1].click()
    if lastRowState[2] != lastRowState[3]:
        print("Tile C != Tile D, flipping")
        g.board[-3][1].click()
    #Second iteration
    print(g)
    for r in range(-3,4):
        #g.formPairs(i)
        #g.elimPairs(i)
        g.solveRow(r)
    print(g)

    #time.sleep(3) #In case the replay button is taking some time to load
    if i < numGames-1: #Don't hit replay when you're on the last game
        g.replay()

print("[Main] Finished all games.")
