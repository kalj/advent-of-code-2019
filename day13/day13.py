#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day13.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>


import sys
import time

class Memory:
    def __init__(self,state):
        self.state = list(state)

    def read(self,addr):
        if addr < len(self.state):
            return self.state[addr]
        else:
            return 0

    def write(self,addr,data):
        if addr >= len(self.state):
            current_len = len(self.state)
            missing = addr-(current_len-1)
            self.state += [0]*missing
        self.state[addr] = data

    def __str__(self):
        s = ""
        nreps = 1
        prev = None
        for d in self.state:
            if d == prev:
                nreps += 1
            elif nreps > 1:

                s += " ... *{} ".format(nreps)
                # also print the next entry
                s += ", {}".format(d)
                nreps = 1
            else:
                s += ", {}".format(d)

            prev = d

        return "["+s[1:].strip()+"]"


class IntcodeComputer:
    def __init__(self,state):
        self.mem = Memory(state)
        self.pc = 0
        self.relative_base = 0
        self.halted = False

    def resolve_inarg(self,arg,opmode):
        if opmode == 1:
            return arg
        elif opmode == 0:
            return self.mem.read(arg)
        elif opmode == 2:
            return self.mem.read(self.relative_base + arg)
        else:
            return None

    def resolve_outarg_addr(self,arg,opmode):
        if opmode == 0:
            return arg
        elif opmode == 2:
            return self.relative_base + arg
        else:
            return None

    def execute(self, input_queue, output_queue):

        if self.halted:
            raise Exception("Cannot execute computer, already halted")

        while True:

            opcode = self.mem.read(self.pc) % 100
            opmode = self.mem.read(self.pc) // 100

            # print("pc: {}, opcode: {}, opmode: {}, relbase: {}, state: {}, output: {}".format(self.pc, opcode, opmode, self.relative_base, self.mem, output_queue))

            if opcode == 99:
                # halt
                self.halted = True
                break

            if opcode in [1,2,7,8]:

                if opcode == 1:
                    # add
                    operation = lambda a,b: a+b
                elif opcode == 2:
                    # multiply
                    operation = lambda a,b: a*b
                elif opcode == 7:
                    # less-than
                    operation = lambda a,b: 1 if a<b else 0
                elif opcode == 8:
                    # equals
                    operation = lambda a,b: 1 if a==b else 0

                in1 = self.mem.read(self.pc+1)
                in2 = self.mem.read(self.pc+2)
                out = self.mem.read(self.pc+3)

                opmode1 = opmode % 10
                opmode2 = (opmode//10) % 10
                opmode3 = (opmode//100) % 10

                arg1    = self.resolve_inarg(in1,opmode1)
                arg2    = self.resolve_inarg(in2,opmode2)
                outaddr = self.resolve_outarg_addr(out,opmode3)

                self.mem.write(outaddr,operation(arg1,arg2))

                self.pc += 4
            elif opcode == 3:
                # read input

                out = self.mem.read(self.pc+1)
                opmode1 = opmode % 10
                outaddr = self.resolve_outarg_addr(out,opmode1)

                if len(input_queue) == 0:
                    # waiting for input...
                    break

                # have enough input
                self.mem.write(outaddr,input_queue.pop(0))

                self.pc += 2

            elif opcode == 4:
                # write output
                in1 = self.mem.read(self.pc+1)
                opmode1 = opmode % 10
                arg1 = self.resolve_inarg(in1,opmode1)

                output_queue.append(arg1)
                self.pc += 2

            elif opcode in [5,6]:
                if opcode == 5:
                    # jump-if-true
                    cond = lambda a: a != 0
                elif opcode == 6:
                    # jump-if-false
                    cond = lambda a: a == 0

                in1 = self.mem.read(self.pc+1)
                in2 = self.mem.read(self.pc+2)

                opmode1 = opmode % 10
                opmode2 = (opmode//10) % 10

                arg1    = self.resolve_inarg(in1,opmode1)
                arg2    = self.resolve_inarg(in2,opmode2)

                if cond(arg1):
                    self.pc = arg2
                else:
                    self.pc += 3
            elif opcode == 9:
                in1 = self.mem.read(self.pc+1)
                opmode1 = opmode % 10
                arg1 = self.resolve_inarg(in1,opmode1)

                self.relative_base += arg1

                self.pc += 2

            else:
                raise Exception('invalid opcode {} at {}'.format(opcode, self.pc))

class Canvas:
    def __init__(self,h,w):
        self.height=h
        self.width=w
        self.the_canvas = []
        for y in range(h):
            self.the_canvas.append([' ']*w)

    def set(self,pos,tile):
        self.the_canvas[pos[1]][pos[0]] = tile

    def get(self,pos):
        return self.the_canvas[pos[1]][pos[0]]

    def display(self):
        for row in self.the_canvas:
            print(''.join(row))
    def count_tile(self,tile):
        count = 0
        for row in self.the_canvas:
            count += len([t for t in row if t==tile])
        return count


class ArcadeGame:
    def __init__(self,prog,h,w):
        self.computer = IntcodeComputer(prog)
        self.input_pipe = []
        self.output_pipe = []
        self.height=h
        self.width=w

        self.canvas = Canvas(self.height,self.width)

    def run(self):

        score = 0
        i=0
        while True:

            # execute program until input is needed or halted
            self.computer.execute(self.input_pipe,self.output_pipe)


            # read output
            tiles = ' |X-o'

            while len(self.output_pipe) > 0:
                x        = self.output_pipe.pop(0)
                y        = self.output_pipe.pop(0)
                data   = self.output_pipe.pop(0)
                if x==-1 and y==0:
                    score = data

                else:
                    tile_idx = data
                    tile = tiles[tile_idx]
                    self.canvas.set([x,y],tile)

            # print out state
            print(" ---- Iteration {:10d} Score: {:10d} ----".format(i,score))
            self.canvas.display()
            i += 1
            if self.computer.halted:
                break

            inpstr = input('Input:')
            if inpstr and inpstr[0] == '.':
                inp = 1
            elif inpstr and inpstr[0] == ',':
                inp = -1
            else:
                inp = 0

            self.input_pipe.append(inp)

        print("Number of blocks:",self.canvas.count_tile('X'))


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = open(sys.argv[1]).read()

state = list(map(int,prog.split(',')))

# state[0] = 2

h = 25
w = 40
game = ArcadeGame(state,h,w)

game.run()
