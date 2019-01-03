# Algo Description:

scan a row from left to right;
as soon as you find a light tile, click its lower-right neighbor

# Why does this even work?

case 1: the light tile is a singleton
this is the first light tile in the row.
(it's first because no light tiles were found before it)
by clicking lower-right, we shift this tile one to the right.
then when we scan again, this will STILL be the first light tile in the row
(we've shifted the first tile to the right, but it's still the first one)

case 2: the light tile is in a pair
then this light tile AND its paired one will be eliminated/become shadow tiles.
then, the next left-to-right scan will find the next light tile to deal with,
and that will become the "first light tile of the row"

case 3: if it's a singleton first and you can't click its lower-right neighbor--
by definition of being "first" there are no other light tiles
by definition of "can't shift" this implies it's the rightmost tile of the row

case 4: if it's a singleton first, on rightmost of row, and you CAN click its lower-right neighbor,
it gets eliminated as a singleton
