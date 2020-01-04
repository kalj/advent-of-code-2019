#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day17.py
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
    def __init__(self,bytelst):
        self.canvas = [line for line in bytes(bytelst).decode().splitlines() if len(line) > 0]
        self.height = len(self.canvas)
        self.width = len(self.canvas[0])

    def print(self):
        for line in self.canvas:
            print(line)

    def get_intersections(self):

        intersections = []
        for i in range(self.height):
            for j in range(self.width):

                if i > 0 and i < (self.height-1) and j>0 and j<(self.width-1) and \
                self.canvas[i][j] == '#' and \
                self.canvas[i+1][j] == '#' and self.canvas[i-1][j] == '#' and \
                self.canvas[i][j+1] == '#' and self.canvas[i][j-1] == '#':

                    intersections.append([i,j])
                    # print("Intersection at [{}, {}]".format(i,j))
                    # canvas[i][j] = 'O'
                    # print("Len before modification:",len(canvas[i]))
                    self.canvas[i] = self.canvas[i][:j] + 'O' + self.canvas[i][(j+1):]
                    # print("Len after modification:",len(canvas[i]))

        return intersections

def get_movement_logic(canvas):

    initpos = None
    for i in range(canvas.height):
        for j in range(canvas.width):
            if canvas.canvas[i][j] == '^':
                initpos= [j,i]
                break

    print("Initial position is",initpos)

    dirs = '^>v<' # instead simply use 0...3

    def get_dirvec(d):
        apa = [[0,-1],
               [1,0],
               [0,1],
               [-1,0]]
        return apa[d]

    def axpy(a,x,y):
        return [a*x[0]+y[0],
                a*x[1]+y[1]]

    def is_valid_scaffold(pt):
        return (pt[0] >= 0 and pt[0] < canvas.width) and (pt[1] >= 0 and pt[1] < canvas.height) and canvas.canvas[pt[1]][pt[0]] == '#'

    commands = []
    pos = initpos

    direction = 0

    nodir = False
    while not nodir:

        nodir = True
        for inc in [-1,1]:
            dr = (direction+inc)%4
            dirvec = get_dirvec(dr)
            neighbor_pos = axpy(1,dirvec,pos)

            if is_valid_scaffold(neighbor_pos):
                nodir = False

                # bingo!
                newdir = dr
                commands.append('L' if inc == -1 else 'R')

                nsteps = 0
                while is_valid_scaffold(axpy(nsteps+1,dirvec,pos)):
                    nsteps += 1

                # print("Next move:", str(nsteps), dirs[dr])
                commands.append(str(nsteps))
                pos = axpy(nsteps,dirvec,pos)

                direction = newdir
                break

    return commands

def match_sublist(keylist,lst):
    length = len(keylist)
    matches = []
    i=0
    while i < len(lst):
        if lst[i:(length+i)]==keylist:
            matches.append(i)
            i += length
        else:
            i += 1
    return matches

def find_matching_sublists(commands):
    matches = []

    for start in range(0,len(commands),2):
        for length in range(2,len(commands)-start,2):

            keylist = commands[start:start+length]

            if 'A' in keylist or 'B' in keylist or 'C' in keylist:
                continue
            if len(','.join(keylist)) > 20:
                continue
            if [m for m in matches if m[0]==keylist]:
                continue
            m = match_sublist(keylist,commands)
            if len(m) > 1:
                reduction = len(m)*len(keylist) - len(m)
                matches.append([keylist, m, reduction])

    matches.sort(key=lambda m:m[2]*1000+(100-m[1][0]))

    # print("Matches:")
    # print("{:>8s} {:>8s} {:>8s}   {:<20s} {:<20s}".format("nmatches","length", "reduct.", "matches", "string"))
    # for m in matches:
    #     print("{:8d} {:8d} {:8d}   {:<20s} {}".format(len(m[1]), len(m[0]), m[2], '  '.join(str(i) for i in m[1]), m[0]))

    return matches

def replace_sublist_matches(lst, sublist_length, start_indices, new_symbol):
    # adjust start indices
    start_indices = [idx-i*(sublist_length-1) for i,idx in enumerate(start_indices)]

    for start in start_indices:
        lst = lst[0:start]+[new_symbol]+lst[(start+sublist_length):]
    return lst

def compress_commands(commands_in):

    commands = list(commands_in)
    compressed = []

    matches_a = find_matching_sublists(commands)

    # find match for A
    for ma in reversed(matches_a):

        A = ma[0]
        # print("Replacing A:", ma)

        commands_a = replace_sublist_matches(commands,len(ma[0]),ma[1],'A')

        # find match for B
        matches_b = find_matching_sublists(commands_a)
        for mb in reversed(matches_b):
            B = mb[0]
            # print("Replacing B:", mb)

            commands_b = replace_sublist_matches(commands_a,len(mb[0]),mb[1],'B')

            # find match for C
            matches_c = find_matching_sublists(commands_b)
            for mc in reversed(matches_c):
                C = mc[0]
                # print("Replacing C:", mc)

                commands_c = replace_sublist_matches(commands_b,len(mc[0]),mc[1],'C')
                if all([c in ['A','B','C'] for c in commands_c]):
                    # we have replaced all. yay.
                    compressed.append([commands_c,A,B,C])

    return compressed

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = [int(c) for c in open(sys.argv[1]).read().split(',')]

## Part 1

computer = IntcodeComputer(prog)

input_pipe = []
output_pipe = []
computer.execute(input_pipe,output_pipe)

if not computer.halted:
    raise Exception("Excpeted a halt")

canvas = Canvas(output_pipe)

canvas.print()

intersections = canvas.get_intersections()

print()
print("======= Canvas with intersections marked =======")

canvas.print()

alignment_parameter = sum(i*j for i,j in intersections)
print("Alignment parameter:",alignment_parameter)


## Part 2

prog[0] = 2

print()

canvas = Canvas(output_pipe)

commands = get_movement_logic(canvas)

print(",".join(commands))

compressed = compress_commands(commands)

for main,a,b,c in compressed:
    print("=== Running with movement logic: ===")
    mainstr = ",".join(main)
    print("Main: {:20s} \t len: {:5d}".format(mainstr,len(mainstr)))
    astr = ",".join(a)
    print("A:    {:20s} \t len: {:5d}".format(astr,len(astr)))
    bstr = ",".join(b)
    print("B:    {:20s} \t len: {:5d}".format(bstr,len(bstr)))
    cstr = ",".join(c)
    print("C:    {:20s} \t len: {:5d}".format(cstr,len(cstr)))

    computer_pt2 = IntcodeComputer(prog)

    movement_logic = \
        mainstr+"\n"+\
        astr+"\n"+\
        bstr+"\n"+\
        cstr+"\n"+\
        "n\n"

    input_pipe = []
    input_pipe = list(movement_logic.encode())

    output_pipe = []
    computer_pt2.execute(input_pipe,output_pipe)

    dust_report = output_pipe.pop(-1)

    # print("Output:",bytes(output_pipe))

    print("Amount of dust collected:",dust_report)
    canvas = Canvas(output_pipe)

    canvas.print()

    print("Halted:",computer_pt2.halted)
