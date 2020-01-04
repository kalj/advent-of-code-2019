#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day24.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys


class Grid:
    def __init__(self,inp=None):
        self.size = 5
        self.data = [[0]*self.size for i in range(self.size)]
        if inp:
            for i in range(self.size):
                for j in range(self.size):
                    self.set(i,j,1 if inp[i][j]=='#' else 0)

    def print(self):
        for i in range(self.size):
            line = ['#' if d==1 else '.' for d in self.data[i]]
            print(''.join(line))

    def size(self):
        return self.size

    def set(self,i,j,v):
        self.data[i][j] = v

    def get(self,i,j):
        return self.data[i][j]

def do_iter(grid_new,grid):

    for i in range(self.size):
        for j in range(self.size):


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

the_input = open(sys.argv[1]).read().splitlines()

grid = Grid(the_input)
grid_new = Grid()

grid.print()
grid_new.print()

niter = 0

while niter < 10:

    do_iter(grid_new,grid)

    grid,grid_new = grid_new,grid

    niter+=1

    print("=== Iteration {} ===".format(niter))
    grid.print()
