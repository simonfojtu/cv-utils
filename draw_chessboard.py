#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from itertools import cycle
from operator import add
import argparse
from collections import deque
import numpy as np
import random
import math

def isRotationInvariant(patch):
    """ Test if given patch is rotation invariant """
    # Assert square and of reasonable size
    assert(len(patch) >= 2)
    assert(len(patch) == len(patch[0]))

    for r in range(1,3):
        if np.array_equal(patch, np.rot90(patch, r)):
            return False
    return True

def patchesEqual(p0, p1):
    """ Return True is p0 is equal to p1 rotated by 0,90,180, or 270 degrees """
    if np.array_equal(p0, p1):
        return True
    for r in range(1,4):
        if np.array_equal(p0, np.rot90(p1, r)):
            return True
    return False

class Grid:
    def __init__(self, rows = 4, cols = 4, patch_size = 3, seed = 0):
        assert(rows >= patch_size)
        assert(cols >= patch_size)
        self.rows = rows
        self.cols = cols
        self.patch_size = patch_size
        self.grid = []
        
    def construct(self):
        """ Construct a grid, so that each patch of size `patch_size` or grater is unique. """
        grid = np.array([np.nan,]*self.rows * self.cols).reshape((self.rows, self.cols))

        # list of used patches
        grids = deque()

        grids.append(grid)

        processNext = False

        while len(grids) > 0:
            grid = grids.pop()
            if not np.isnan(grid).any():
                break

            #print("Constructing from:")
            #print(grid)
            used = []
            processNext = False
            for r in range(self.rows - self.patch_size + 1):
                for c in range(self.cols - self.patch_size + 1):
                    patch = grid[r:r+self.patch_size, c:c+self.patch_size]
                    nans = np.isnan(patch)
                    if nans.any():
                        # fill all np.nan positions with 0 or 1
                        count = sum(nans.flatten())
                        for i in range(2 ** count):
                            pcopy = patch.copy()
                            pcopy[nans] = list(np.binary_repr(i, count))

                            if not isRotationInvariant(pcopy):
                                continue

                            usedAlready = False
                            for usedPatch in used:
                                if patchesEqual(usedPatch, pcopy):
                                    usedAlready = True
                                    break

                            if usedAlready:
                                continue

                            newGrid = grid.copy()
                            newGrid[r:r+self.patch_size, c:c+self.patch_size] = pcopy
                            grids.append(newGrid)
                            #processNext = True
                            #break
                        else:
                            #raise Exception("Failed to find valid patch. Try to decrease the number of rows or cols or increase patch size")
                            processNext = True
                            break

                    used.append(patch)
                    if processNext:
                        break
                if processNext:
                    break

        # Test if final grid is valid (no np.nan elements)
        if not np.isnan(grid).any():
            self.grid = grid
        else:
            self.grid = None

    def hash(self):
        flat=[str(int(item)) for sublist in self.grid for item in sublist]
        return int(''.join(flat),2)

    def print(self):
        """ Print grid to console """
        print("patch_size = " + str(self.patch_size))
        print("hash = " + str(self.hash()))

    def isValid(self):
        """
        Test if grid is valid:
            1) All patches are rotation invariant
            AND
            2) Every patch is unique even when rotated
        """
        for r in range(self.rows-self.patch_size+1):
            for c in range(self.cols-self.patch_size+1):
                patch = self.grid[r:r+self.patch_size, c:c+self.patch_size]
                if not isRotationInvariant(patch):
                    print("patch at " + str(r) + ":" + str(c) + " of size " + str(self.patch_size) + " is not rotation invariant")
                    return False

                for r_ in range(self.rows - self.patch_size + 1):
                    for c_ in range(self.cols - self.patch_size + 1):
                        if r_ == r and c_ == c:
                            continue
                        patch_ = self.grid[r_:r_+self.patch_size, c_:c_+self.patch_size]
                        if patchesEqual(patch, patch_):
                            print("patch at " + str(r) + ":" + str(c) + " of size " + str(self.patch_size) + " matches patch at " + str(r_) + ":" + str(c_))
                            return False

        return True

def draw(*, cols = 0, rows = 0, patch_size = 0, square_size = 0, dpi = 300):
    """
    Draw chessboard wth optional circles grid

    TODO: write grid identification number to the output file
    """
    # A4 size paper
    width = 8.3 # inch
    height = 11.7 # inch

    # number of squares
    if cols == 0 or rows == 0:
        if square_size == 0:
            # default square size in pixels
            square_size = int(dpi / 3)

        cols = int(width * dpi // square_size)
        rows = int(height * dpi // square_size)
    else:
        if cols == 0 or rows == 0:
            print("Specify either both number of rows and cols or none of them")
            return
        if square_size == 0:
            square_size = int(min(dpi * width / cols, dpi * height / rows))
            print("Automatic square size = " + str(square_size) + "px")
        width = cols * square_size / dpi
        height = rows * square_size / dpi

    assert(rows != 0)
    assert(cols != 0)
    assert(square_size != 0)

    print("Drawing grid " + str(rows) + "x" + str(cols))

    def square(i, j):
        "Return the square corners, suitable for use in PIL drawings" 
        return (i * square_size, j * square_size,
                (i + 1) * square_size-1, (j+1) * square_size-1)

    def sq2ellipse(rect):
        pad = int(square_size / 5)
        return list(map(add, rect, (pad, pad, -pad, -pad)))
    
    image = Image.new('L',
                 (int(width * dpi), int(height * dpi)),
                 (255) # white
            )

    if patch_size == 0:
        for ps in range(4,6):
            grid = Grid(rows, cols, ps)
            grid.construct()
            if grid.isValid():
                break
        else:
            print("Failed to construct grid with given parameters")
            return
    else:
        grid = Grid(rows, cols, patch_size)
        grid.construct()
        if not grid.isValid():
            print("Failed to construct grid with given parameters")
            return


    grid.print()

    draw_square = ImageDraw.Draw(image).rectangle
    draw_ellipse = ImageDraw.Draw(image).ellipse

    # top left is black
    off = 0
    for r in range(rows):
        for c in range(cols):
            color = 'black'
            if (c + off) % 2 == 0:
                draw_square(square(c, r), fill='black')
                color = 'white'
            # draw circles
            if grid.grid[r,c] == 0:
                draw_ellipse(sq2ellipse(square(c,r)), fill=color)
        off = (off + 1) % 2

    fnt = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSerif.ttf', size=int(dpi/8))

    text = "cols = %i, rows = %i, patch size = %i, square size = %i, dpi = %i" % (cols, rows, patch_size, square_size, dpi)

    ImageDraw.Draw(image).text((int(dpi/30),dpi*height-int(dpi/6)), text, font=fnt, fill=(127))


    
    return image

# Test isRotationInvariant function
# TODO convert to TestCase
assert(isRotationInvariant([[1,0],[0,0]]))
assert(not isRotationInvariant([[1,0],[0,1]]))

parser = argparse.ArgumentParser()
parser.add_argument("--rows","-r", help="number of rows", type=int, default=0)
parser.add_argument("--cols","-c", help="number of rows", type=int, default=0)
parser.add_argument("--patch","-p", help="size of patch of circles", type=int, default=0)
parser.add_argument("--square","-s", help="size of square (px)", type=int, default=0)
parser.add_argument("--dpi", help="dots per inch (DPI)", type=int, default=300)

parser.add_argument("--out","-o", help="output file", default="chessboard.png")

args = parser.parse_args()


chessboard = draw(cols = args.cols, rows = args.rows, patch_size = args.patch, square_size = args.square, dpi = args.dpi)
chessboard.save(args.out)

