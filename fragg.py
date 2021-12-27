import sys
from game import Game
import time

#There are two "games" being played
#One is the on-screen game, on the actual website; the other exists in-memory

#It's slower to read from the screen every time we want to make a move, 
#so we calculate all the moves in advance, then execute them all at once
        
def main(numGames): 

    g = Game()
    launched = g.launchGame()
    if not launched:
        sys.exit()

    g.createTiles()
    g.linkTiles()

    for i in range(numGames):
        print("[Main] Beginning game", i+1, "/", numGames)
        time.sleep(3) #Wait for game to load
        g.getStateFromScreen()
        print("[Main] Initial board state")

        g.solveGame()

        if i < numGames-1: #Don't hit replay when you're on the last game
            launched = g.replay()

        numRetries = 5
        j = 0
        while not launched and j < numRetries:
            print("Retrying game", i+1,"/",numGames, "; Attempt:", j+1)
            g.getStateFromScreen()
            g.solveGame()
            launched = g.replay()
            if launched: #OK we played the next game
                break
            else:
                j = j+1
        
        if not launched: #Somehow, the above retries failed to launch the next game
            #Probably due to wifi errors
            print("Unable to launch the next game. Exiting")
            sys.exit()
        

    print("[Main] Finished all games.")

if __name__ == "__main__":
    numGames = int(sys.argv[1]) if len(sys.argv) >1 else 47
    #It takes 47 games to cap lucky streak
    print("Requested %s games"%numGames)
    main(numGames)
