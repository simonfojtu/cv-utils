#!/usr/bin/env python3
from collections import deque
import numpy as np

import unittest


class Grid:
    def __init__(self, rows = 4, cols = 4, patch_size = 3, seed = 0):
        assert(rows >= patch_size)
        assert(cols >= patch_size)
        self.rows = rows
        self.cols = cols
        self.patch_size = patch_size
        self.grid = []

    @staticmethod
    def isRotationInvariant(patch):
        """ Test if given patch is rotation invariant """
        # Assert square and of reasonable size
        assert(len(patch) >= 2)
        assert(len(patch) == len(patch[0]))
    
        for r in range(1,3):
            if np.array_equal(patch, np.rot90(patch, r)):
                return False
        return True
    
    @staticmethod
    def patchesEqual(p0, p1):
        """ Return True is p0 is equal to p1 rotated by 0,90,180, or 270 degrees """
        if np.array_equal(p0, p1):
            return True
        for r in range(1,4):
            if np.array_equal(p0, np.rot90(p1, r)):
                return True
        return False
        
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

                            if not Grid.isRotationInvariant(pcopy):
                                continue

                            usedAlready = False
                            for usedPatch in used:
                                if Grid.patchesEqual(usedPatch, pcopy):
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
                if not Grid.isRotationInvariant(patch):
                    print("patch at " + str(r) + ":" + str(c) + " of size " + str(self.patch_size) + " is not rotation invariant")
                    return False

                for r_ in range(self.rows - self.patch_size + 1):
                    for c_ in range(self.cols - self.patch_size + 1):
                        if r_ == r and c_ == c:
                            continue
                        patch_ = self.grid[r_:r_+self.patch_size, c_:c_+self.patch_size]
                        if Grid.patchesEqual(patch, patch_):
                            print("patch at " + str(r) + ":" + str(c) + " of size " + str(self.patch_size) + " matches patch at " + str(r_) + ":" + str(c_))
                            return False

        return True

class TestGrid(unittest.TestCase):
    def test_rotationInvariance(self):
        self.assertTrue(Grid.isRotationInvariant([[1,0],[0,0]]))

        self.assertFalse(Grid.isRotationInvariant([[1,0],[0,1]]))

    def test_patchesEqual(self):
        self.assertTrue(Grid.patchesEqual([[1,0],[0,0]], [[1,0],[0,0]]))
        self.assertTrue(Grid.patchesEqual([[1,0],[0,0]], [[0,1],[0,0]]))
        self.assertTrue(Grid.patchesEqual([[1,0],[0,0]], [[0,0],[1,0]]))
        self.assertTrue(Grid.patchesEqual([[1,0],[0,0]], [[0,0],[0,1]]))
