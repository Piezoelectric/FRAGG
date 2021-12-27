import pyautogui
from tile import Tile

#States are kind of as follows:
#Game region on screen not found yet/Game() not fully initialized
#Game region on screen found, and we're in the "Play Again?" game loop

class Game:
    def __init__(self):
        '''Initialize the simulated game.

        The simulated game uses coordinates as described in hexutil.py:
        Odd rows have offset columns (e.g. (-3, -1)), even rows do not (e.g. (-2,0)).
        a Tile's row+col should be an even number

        NOTE from future self: maybe don't use hexutil idk
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
        
        playRegion = pyautogui.locateOnScreen("PlayGame.png", minSearchTime = 20)
        if playRegion == None:
            print("Play Game button couldn't be found. Exiting")
            return False
                
        self.gameRegion = (playRegion[0]-295, #MAGIC CONSTANTS
                           playRegion[1]-320,
                           700,
                           600)
        #pyautogui.screenshot("test.png", gameRegion)
        pyautogui.click(playRegion[0], playRegion[1])
        
        hardRegion = pyautogui.locateOnScreen("hard.png", minSearchTime = 20)
        if hardRegion == None:
            print("Hard button couldnt be found. exiting")
            return False
        pyautogui.click(hardRegion[0], hardRegion[1])
        
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
            
            #Gets the column we're on; number of columns per row varies
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

        img = pyautogui.screenshot()

        for i in self.board.keys():
            row = self.board[i]
            for j in row.keys():
                self.board[i][j].getStateFromScreen(img)
                #print(self.board[i][j])

    def _shiftTile(self, i, j, right=False):
        '''Shifts the Tile with virtual grid coordinates (i,j).
        Shift a tile in rowA by clicking the tile underneath it in rowA+1
        #Left by default
        '''
        #TODO -- another way we could do this is by using the linked tile, e.g. 
        #get tile.neighbors[4] and click it
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
            #Search for the first light tile in the row; remember its coordinates too
            columns = list(self.board[r].keys())
            for col in columns:
                tempTile = self.board[r][col]
                if tempTile.state == 1:
                    firstLightTileCol = col
                    break

            #No light tile was found in the row--exit
            if firstLightTileCol == None:
                print("No light tile was found in row", r, "; go to next row")
                rowActive = False
            else: #Else, a light tile exists:
                tempLightTile = self.board[r][firstLightTileCol]
                #But maybe this light tile is already on the right edge
                #and can't be eliminated
                if tempLightTile.neighbors[5] == None:
                    print("Last light tile in row", r, "is on right edge;",
                          "go to next row")
                    rowActive = False
                else:
                    print("Shifting or eliminating tile", r, firstLightTileCol)
                    self._shiftTile(r, firstLightTileCol, right=True)

    def solveGame(self):
        '''
        Calls Game.solveRow multiple times, for each row, to solve a GG game.
        '''

        #First iteration
        print(self.__str__())
        for r in range(-3,4):
            self.solveRow(r)
        print(self.__str__())
        #Click relevant tiles for iteration 2
        lastRowState = self.getRowStates(3)
        #Remember we're using list indxes here, not grid coords
        if lastRowState[0] == 1:
            print("Tile A == 1, flipping")
            self.board[-3][-3].click()
        if lastRowState[1] == 1:
            print("Tile B == 1, flipping")
            self.board[-3][-1].click()
        if lastRowState[2] != lastRowState[3]:
            print("Tile C != Tile D, flipping")
            self.board[-3][1].click()
        #Second iteration
        print(self.__str__())
        for r in range(-3,4):
            self.solveRow(r)
        print(self.__str__())

    def replay(self):
        playAgain = pyautogui.locateOnScreen("playAgain.png", minSearchTime = 20)
        if playAgain == None:
            print("Play Again button was not found.",
                  "The game will re-read the screen",
                  "and try to play the game, corrected with new screen data.")
            return False
        
        pyautogui.click(playAgain[0],playAgain[1])
        return True