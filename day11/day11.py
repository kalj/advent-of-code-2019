#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day11.py
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

    def set(self,pos,color):
        self.the_canvas[pos[1]][pos[0]] = color

    def get(self,pos):
        return self.the_canvas[pos[1]][pos[0]]

    def display(self,pos,direction):
        for y,row in reversed(list(enumerate(self.the_canvas))):
            for x,c in enumerate(row):
                if pos == [x,y]:
                    icons = '^>v<'
                    print(icons[direction],end='')
                else:
                    print('#' if c=='#' else ' ',end='')
            print()

    def count_painted(self):
        count = 0
        for row in self.the_canvas:
            for c in row:
                if c != ' ':
                    count+= 1
        return count

class PaintRobot:
    def __init__(self,prog,h,w):
        self.computer = IntcodeComputer(prog)
        self.input_pipe = []
        self.output_pipe = []
        self.height=h
        self.width=w
        self.pos = [self.width//2,self.height//2]
        self.direction = 0 # 0-3 , 0 is up, 1 right, 2 down, and 3 left

        self.canvas = Canvas(self.height,self.width)

        # self.canvas.display(self.pos,self.direction)


    def run(self):

        # Part 2: set starting position to white
        self.canvas.set(self.pos,'#')

        i=0
        while True:

            # pass color at current position as input
            current_color = self.canvas.get(self.pos)
            self.input_pipe.append(1 if current_color == '#' else 0)

            # execute program until input is needed or halted
            self.computer.execute(self.input_pipe,self.output_pipe)

            if self.computer.halted:
                break

            # read output
            color = self.output_pipe.pop(0)
            turn = self.output_pipe.pop(0)

            # paint canvas
            self.canvas.set(self.pos,'#' if color == 1 else '.')

            # perform turn
            if turn == 0:
                self.direction = (self.direction-1)%4
            else:
                self.direction = (self.direction+1)%4

            # move one step
            if self.direction == 0:
                self.pos[1] += 1
            elif self.direction == 1:
                self.pos[0] += 1
            elif self.direction == 2:
                self.pos[1] -= 1
            elif self.direction == 3:
                self.pos[0] -= 1

            # print out state
            # print(" ---- Canvas iteration {} ----".format(i))

            # self.canvas.display(self.pos,self.direction)
            i += 1

            # time.sleep(0.01)

        print("Finished after {} iterations".format(i))
        print(" ==================== Result ==================== ")

        self.canvas.display(self.pos,self.direction)

        print("Number of painted tiles:",self.canvas.count_painted())



if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = open(sys.argv[1]).read()

state = list(map(int,prog.split(',')))
h = 201
w = 201
robot = PaintRobot(state,h,w)

robot.run()
