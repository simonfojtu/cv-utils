#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from itertools import cycle
from operator import add
import argparse
from collections import deque
import numpy as np
import random
import math

from unique_grid import Grid


def draw(*, cols = 0, rows = 0, patch_size = 0, square_size = 0, dpi = 1200):
    """
    Draw circle board wth optional circles grid
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

    def shrink(rect, pad):
        return list(map(add, rect, (pad, pad, -pad, -pad)))

    def square(i, j):
        "Return the square corners, suitable for use in PIL drawings" 
        return (i * square_size, j * square_size,
                (i + 1) * square_size-1, (j+1) * square_size-1)

    def sq2ellipse(rect):
        pad = int(square_size / 3)
        return list(map(add, rect, (pad, pad, -pad, -pad)))
    
    image = Image.new('L',
                 (int(width * dpi), int(height * dpi)),
                 (255) # white
            )

    if patch_size == 0:
        # Try progressively bigger patches, unitl it finds a solution
        for ps in range(4,8):
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

    draw_ellipse = ImageDraw.Draw(image).ellipse

    for r in range(rows):
        for c in range(cols):
            sq = square(c, r)
            draw_ellipse(shrink(sq, square_size / 6), fill='black')
            # draw circles
            if grid.grid[r,c] == 1:
                draw_ellipse(shrink(sq, square_size / 2.5), fill='white')

    fnt = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSerif.ttf', size=int(dpi/8))

    text = "cols = %i, rows = %i, patch size = %i, square size = %i, dpi = %i" % (cols, rows, patch_size, square_size, dpi)

    ImageDraw.Draw(image).text((int(dpi/30),dpi*height-int(dpi/6)), text, font=fnt, fill=(127))


    
    return image


parser = argparse.ArgumentParser()
parser.add_argument("--rows","-r", help="number of rows", type=int, default=0)
parser.add_argument("--cols","-c", help="number of rows", type=int, default=0)
parser.add_argument("--patch","-p", help="size of patch of circles", type=int, default=0)
parser.add_argument("--square","-s", help="size of square (px)", type=int, default=0)
parser.add_argument("--dpi", help="dots per inch (DPI)", type=int, default=1200)

parser.add_argument("--out","-o", help="output file", default="chessboard.png")

args = parser.parse_args()


chessboard = draw(cols = args.cols, rows = args.rows, patch_size = args.patch, square_size = args.square, dpi = args.dpi)
chessboard.save(args.out)

