#!/usr/bin/env python3
from PIL import Image, ImageDraw
from itertools import cycle
from operator import add
import argparse
from collections import deque
import numpy as np
import random
import math

def isRotationInvariant(patch):
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
    def __init__(self, rows = 4, cols = 4, patchsize = 3, seed = 0):
        self.rows = rows
        self.cols = cols
        self.patchsize = patchsize
        self.grid = []
        
    def construct(self):
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
            for r in range(self.rows - self.patchsize + 1):
                for c in range(self.cols - self.patchsize + 1):
                    patch = grid[r:r+self.patchsize, c:c+self.patchsize]
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
                            newGrid[r:r+self.patchsize, c:c+self.patchsize] = pcopy
                            grids.append(newGrid)
                            #processNext = True
                            #break
                        else:
                            #raise Exception("Failed to find valid patch. Try to decrease the number of rows or cols or increase patch size")
                            processNext = True
                            break

                    #grid[r:r+self.patchsize, c:c+self.patchsize] = patch
                    used.append(patch)
                    if processNext:
                        break
                if processNext:
                    break

        if not np.isnan(grid).any():
            self.grid = grid
        else:
            self.grid = None


    def print(self):
        print("patchsize = " + str(self.patchsize))
        print(self.grid)

    def isValid(self):
        for r in range(self.rows-self.patchsize+1):
            for c in range(self.cols-self.patchsize+1):
                patch = self.grid[r:r+self.patchsize, c:c+self.patchsize]
                if not isRotationInvariant(patch):
                    print("patch at " + str(r) + ":" + str(c) + " of size " + str(self.patchsize) + " is not rotation invariant")
                    return False

                for r_ in range(self.rows - self.patchsize + 1):
                    for c_ in range(self.cols - self.patchsize + 1):
                        if r_ == r and c_ == c:
                            continue
                        patch_ = self.grid[r_:r_+self.patchsize, c_:c_+self.patchsize]
                        if patchesEqual(patch, patch_):
                            print("patch at " + str(r) + ":" + str(c) + " of size " + str(self.patchsize) + " matches patch at " + str(r) + ":" + str(c))
                            return False

        return True

def draw(pixel_size=50, dpi = 150):
    """
    Draw chessboard on a A4 paper
    TODO add circles for unique determining camera position from a subset of squares
    """
    # A4 size paper
    width = 8.3 # inch
    height = 11.7 # inch
    # number of squares
    cols = int(width * dpi // pixel_size)
    rows = int(height * dpi // pixel_size)

    print("Drawing grid " + str(rows) + "x" + str(cols))

    def square(i, j):
        "Return the square corners, suitable for use in PIL drawings" 
        return (i * pixel_size, j * pixel_size,
                (i + 1) * pixel_size, (j+1) * pixel_size)

    def sq2ellipse(rect, pad=12):
        return list(map(add, rect, (pad, pad, -pad, -pad)))
    
    image = Image.new('L',
                 (int(width * dpi), int(height * dpi)),
                 (255) # white
            )

    for patchsize in range(4,6):
        grid = Grid(rows, cols, patchsize)
        grid.construct()
        if grid.isValid():
            break

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
            if grid.grid[r,c] == 0:
                draw_ellipse(sq2ellipse(square(c,r)), fill=color)
        off = (off + 1) % 2

    # draw circles


    
    return image

# Test isRotationInvariant function
assert(isRotationInvariant([[1,0],[0,0]]))
assert(not isRotationInvariant([[1,0],[0,1]]))

parser = argparse.ArgumentParser()
parser.add_argument("--rows","-r", help="number of rows", type=int)
parser.add_argument("--cols","-c", help="number of rows", type=int)
parser.add_argument("--patch","-p", help="size of patch", type=int)

args = parser.parse_args()

# Draw simple chessboard
#chessboard = draw_chessboard()
#chessboard.save("chessboard-a4.png")

#g = Grid(args.rows, args.cols, args.patch)
#
#g.construct()
#g.print()
#if g.isValid():
#    print("Hoorray")
#else:
#    print("Nada")

chessboard = draw()
chessboard.save("chessboard-a4.png")
