#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)day19.py
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
    def __init__(self,height,width):
        self.canvas = []
        for i in range(height):
            self.canvas.append([' ']*width)
        self.height = height
        self.width  = width

    def print(self):
        for line in self.canvas:
            print(''.join(line))

    def set(self,pos,val):
        i,j = pos
        self.canvas[i][j] = val

    def get(self,pos):
        i,j = pos
        return self.canvas[i][j]

    def n_affected(self):
        return len([c for row in self.canvas for c in row if c=='#'])

    def max_square(self):
        # first '#' in last line
        lastline = self.canvas[-1]
        j1st = [j for j,c in enumerate(lastline) if c=='#'][0]

        side=1
        while self.get([self.height-1-(side), j1st+side]) == '#':
            side += 1

        for i in range(self.height-side,self.height):
            for j in range(j1st,j1st+side):
                self.set([i,j],'O')

        return side,[self.height-side,j1st]

    def compute_beam_coverage(self, prog, compute_slope=False, slope_env=None, truncated_size=None):

        if compute_slope:
            maxslope=0
            minslope=1000

        for i in range(self.height):
            for j in range(self.width):


                if truncated_size and (i<(self.height-truncated_size-1) or j<(self.width-3*truncated_size)):
                    continue

                if slope_env and i>0:
                    slope=(i-j)/i
                    if slope < slope_env[0] or slope > slope_env[1]:
                        continue

                computer = IntcodeComputer(prog)

                input_pipe = [j,i]
                output_pipe = []
                computer.execute(input_pipe,output_pipe)
                if output_pipe[0]:
                    self.set([i,j],'#')
                    if compute_slope and i>0:
                        slope=(i-j)/i
                        maxslope = max(slope,maxslope)
                        minslope = min(slope,minslope)
                else:
                    canvas.set([i,j],'.')

                if not computer.halted:
                    raise Exception("Excpeted a halt")

        if compute_slope:
            return [minslope, maxslope]

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = [int(c) for c in open(sys.argv[1]).read().split(',')]

## Part 1

canvas = Canvas(50,50)
slope_env = canvas.compute_beam_coverage(prog,compute_slope=True)

canvas.print()
print("Min slope:",slope_env[0])
print("Max slope:",slope_env[1])
print("Number of affected points:",canvas.n_affected())

## Part 2

canvas_size = 1340
slope_env = [0.02, 0.17]
target_side = 100
side = target_side
while True:

    canvas = Canvas(canvas_size,canvas_size)
    canvas.compute_beam_coverage(prog,slope_env=slope_env,truncated_size=side)

    side,ul = canvas.max_square()

    print("Size:",canvas_size,"Side:",side,"Upper left:",ul)

    if side>=target_side:
        print("Done!")
        break
    # canvas.print()

    canvas_size += 1
