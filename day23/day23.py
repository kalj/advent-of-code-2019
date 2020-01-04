#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)day23.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys

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


class NicComputer:
    def __init__(self,prog,input_pipe,output_pipe):
        self.cpu = IntcodeComputer(prog)
        self.i = input_pipe
        self.o = output_pipe

    def execute(self):
        self.cpu.execute(self.i,self.o)

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = [int(c) for c in open(sys.argv[1]).read().split(',')]

ncomputers = 50
computers = [NicComputer(prog,[i,-1],[]) for i in range(ncomputers)]

nat_mem = []
last_nat_y = None
iter=0
while True:
    bus = []
    for comp in computers:
        comp.execute()
        while len(comp.o) > 0:
            dest = comp.o.pop(0)
            X = comp.o.pop(0)
            Y = comp.o.pop(0)
            bus.append((dest,X,Y))

    print("Messages iteration",iter)
    for dest,x,y in bus:
        print(dest,x,y)
        if dest < ncomputers:
            computers[dest].i.append(x)
            computers[dest].i.append(y)
        if dest == 255:
            print("Y value sent to 255:",y)
            nat_mem = [x,y]

    if sum(len(comp.i) for comp in computers)==0:
        print("Execution stalled, NAT sending message to computer 0:",nat_mem)
        if last_nat_y != None and last_nat_y == nat_mem[1]:
            print("Same Y sent twice in a row from NAT:",last_nat_y)
            break
        computers[0].i.append(nat_mem[0])
        computers[0].i.append(nat_mem[1])
        last_nat_y = nat_mem[1]

    for comp in computers:
        if len(comp.i) == 0:
            comp.i.append(-1)

    iter += 1
    # if iter > 20:
    #     break
