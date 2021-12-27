import sys
from game import Game
import time
import re

#There are two "games" being played
#One is the on-screen game, on the actual website; the other exists in-memory

#It's slower to read from the screen every time we want to make a move, 
#so we calculate all the moves in advance, then execute them all at once
        
def main(numGames, safe=True, numRetries = 5): 

    g = Game(safe)
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

        # Retry logic
        for j in range(numRetries):
            if launched:
                break
            print("Retrying game", i+1,"/",numGames, "; Attempt:", j+1)
            g.getStateFromScreen()
            g.solveGame()
            launched = g.replay()
        
        if not launched: #Somehow, the above retries failed to launch the next game
            #Probably due to wifi errors
            print("Unable to launch the next game. Exiting")
            sys.exit()
        

    print("[Main] Finished all games.")

def parse_args(arg_line):
    args_pattern = re.compile(
        r"""^(
            \s*(?P<numGames>\d*)? #for numgames
            \s*(?P<safe>.*)? #for safety option
        )$""",
        re.VERBOSE
    )

    args = {}
    match_object = args_pattern.match(arg_line)
    if match_object:
        args = {k: v for k, v in match_object.groupdict().items()
                if v is not None}
    return args


if __name__ == "__main__":
    arg_line = " ".join(sys.argv[1:])
    args = parse_args(arg_line)

    numGames = int(args['numGames']) if args['numGames'] != '' else 47
    safe = False if args['safe'] == '--unsafe' else True

    print("Requested %s games"%numGames)
    print("Starting in %s mode"%("SAFE" if safe else "UNSAFE"))

    main(numGames, safe)
