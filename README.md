# FRAGG

Automatically solves FR's GG minigame.

Usage:

`python3 -m fragg NUMGAMES SAFETY` 

Options: 
* `NUMGAMES` for number of games. If unspecified, defaults to 47. 
* `SAFETY`: if `--unsafe`, then the program does not look for certain menu elements (the hardmode button, the playagain button), and instead calculates their positions based on the initial position of the "Play Game" button. This might cause the program to behave strangely.