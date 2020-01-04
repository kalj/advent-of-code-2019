#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day15.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import time
import pygame

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_HOME,
    K_PAGEUP,
    K_PAGEDOWN,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

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

def get_new_pos(old_pos,direction):
    if direction == 1:
        return [old_pos[0],old_pos[1]-1]
    elif direction == 2:
        return [old_pos[0],old_pos[1]+1]
    elif direction == 3:
        return [old_pos[0]-1,old_pos[1]]
    elif direction == 4:
        return [old_pos[0]+1,old_pos[1]]

class RepairDroidGame:
    def __init__(self,prog):
        self.computer = IntcodeComputer(prog)
        self.input_pipe = []
        self.output_pipe = []

        self.height=50
        self.width=50

        self.droid_pos = [self.width//2,self.height//2]

        self.canvas = Canvas(self.height,self.width)
        self.canvas.set(self.droid_pos,'.')

        pygame.init()
        self.screen = pygame.display.set_mode([20*self.width,20*self.height])
        self.clock = pygame.time.Clock()

    def draw(self, show_bot=True):

        self.screen.fill((255,255,255))
        # Draw a solid blue circle in the center

        for y in range(self.height):
            for x in range(self.width):
                if show_bot and [x,y] == self.droid_pos:
                    pygame.draw.circle(self.screen, (150, 0, 0), (20*x+10, 20*y+10), 10)
                else:

                    tile = self.canvas.get([x,y])
                    if tile == '#':
                        pygame.draw.rect(self.screen, (0, 0, 200), pygame.Rect(20*x+1,20*y+1,18,18))
                    elif tile == ' ':
                        pygame.draw.rect(self.screen, (0, 150, 0), pygame.Rect(20*x+1,20*y+1,18,18))
                    elif tile == '*':
                        pygame.draw.circle(self.screen, (255, 0, 255), (20*x+10, 20*y+10), 5)
                    elif tile == '.':
                        pass # we can pass through here, then just leave it blank!

        # Flip the display
        pygame.display.flip()

    def run(self):

        i=0
        trajectory = [self.droid_pos]
        explore = True
        stack = []

        if explore:
            print("Exploring...")

        while True:

            self.draw()

            if explore:

                directions = [1,2,3,4]
                tiles = [self.canvas.get(get_new_pos(self.droid_pos,d)) for d in directions]

                unexplored_directions = [d for d,t in zip(directions,tiles) if t==' ']

                if len(unexplored_directions) == 0:
                    # backtrack
                    if len(stack) == 0:
                        print("Done exploring.")
                        # done exploring
                        explore = False
                    else:
                        # print("Backtracking...")
                        last_dir = stack.pop(-1)
                        inverted = {1:2,2:1,3:4,4:3}
                        inp = inverted[last_dir]
                else:
                    inp = unexplored_directions[0]
                    stack.append(inp) # actually don't know if this will happen, undo later if didn't move
                    # print("Trying to move in direction {}".format('North' if inp==1 else 'South' if inp==2 else 'West' if inp==3 else 'East'))
            else:
                # handle input
                stop = False
                inp = None
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        stop = True
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            stop = True
                        elif event.key == K_UP:
                            inp = 1
                        elif event.key == K_DOWN:
                            inp = 2
                        elif event.key == K_LEFT:
                            inp = 3
                        elif event.key == K_RIGHT:
                            inp = 4
                if stop:
                    break

            if inp:
                self.input_pipe.append(inp)

                # execute program until input is needed or halted
                self.computer.execute(self.input_pipe,self.output_pipe)

                # read output
                out = self.output_pipe.pop(0)

                requested_pos = get_new_pos(self.droid_pos,inp)

                if out == 0:
                    # there is a block in the requested direction
                    self.canvas.set(requested_pos,'#')

                    if explore:
                        # undo save move dir if blocked
                        stack.pop(-1)
                else:
                    # moving in the requested direction was no problem
                    self.droid_pos = requested_pos
                    if len(trajectory) > 1 and trajectory[-2]==self.droid_pos:
                        trajectory.pop(-1)
                    else:
                        trajectory.append(self.droid_pos)

                    if out == 1:
                        self.canvas.set(requested_pos,'.')
                    elif out == 2:
                        self.canvas.set(requested_pos,'*')
                        leak_distance = len(trajectory)-1


            if self.computer.halted:
                break

            fps = 30
            if explore:
                fps = 120
            self.clock.tick(fps)

        print("Distance from start to leak:",leak_distance)

        fill = True
        minutes=0
        if fill:
            while self.canvas.count_tile('.') > 0:
                self.draw(False)
                current_oxygen_pts = []
                for y in range(self.canvas.height):
                    for x in range(self.canvas.width):
                        if self.canvas.get([x,y]) == '*':
                            current_oxygen_pts.append([x,y])
                for op in current_oxygen_pts:
                    # spread oxygen
                    surrounding_pts = [[op[0]-1,op[1]],
                                       [op[0]+1,op[1]],
                                       [op[0],op[1]-1],
                                       [op[0],op[1]+1]]

                    for p in surrounding_pts:
                        pt = self.canvas.get(p)
                        if pt == '.':
                            self.canvas.set(p,'*')

                minutes += 1
                self.clock.tick(30)

            print("Filling all locations with oxygen took {} minuets.".format(minutes))

        pygame.quit()

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = open(sys.argv[1]).read()

state = list(map(int,prog.split(',')))

game = RepairDroidGame(state)

game.run()
