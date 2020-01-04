#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)day25.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import cmd

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

class Room:
    def __init__(self,doors):
        self.doors = doors

    def get_str_part(self,segm):
        if segm == 0:
            if 'north' in self.doors:
                return '. .'
            else:
                return '.-.'
        elif segm == 1:
            if 'west' in self.doors:
                return ' '
            else:
                return '|'
        elif segm == 2:
            if 'east' in self.doors:
                return ' '
            else:
                return '|'
        elif segm == 3:
            if 'south' in self.doors:
                return '. .'
            else:
                return '.-.'
        else:
            raise Exception('Invalid segment id')

movements = {'north':[-1,0],'south':[1,0],'west':[0,-1],'east':[0,1]}

class Map:

    def __init__(self):
        self.pos = [0,0]
        self.rooms = [[]]
        self.width=0
        self.height=1

    def parse_output(self, output, command):

        if "== Pressure-Sensitive Floor ==" in output:
            # this is a fake room
            return

        if command in movements.keys():
            movefail = False
            for line in output:
                if line == "You can't go that way.":
                    movefail = True

            if movefail:
                return

            movement = movements[command]

            newpos = [self.pos[0]+movement[0],
                      self.pos[1]+movement[1]]

            self.pos = newpos

        if self.pos[0] == -1:
            self.height += 1
            self.pos[0] = 0
            self.rooms.insert(0,[None]*self.width)

        elif self.pos[1] == -1:
            self.width += 1
            self.pos[1] = 0
            for row in self.rooms:
                row.insert(0,None)

        elif self.pos[0] == self.height:
            self.height += 1
            self.rooms.append([None]*self.width)

        elif self.pos[1] == self.width:
            self.width += 1
            for row in self.rooms:
                row.append(None)

        if self.rooms[self.pos[0]][self.pos[1]] == None:

            do_door_parse = False
            doors = []
            for line in output:
                if do_door_parse:
                    if line == '':
                        do_door_parse = False
                    else:
                        door = line[2:]
                        doors.append(door)

                elif line == 'Doors here lead:':
                    do_door_parse = True

            if len(doors) == 0:
                raise Exception('Rooms cannot have no doors! Parsed output: {}'.format(output))

            self.rooms[self.pos[0]][self.pos[1]] = Room(doors)

    def print(self):

        for i,row in enumerate(self.rooms):


            print(' '.join([room.get_str_part(0) if room else '   ' for room in row]))
            midrow=[]
            for j in range(self.width):
                if row[j] == None:
                    midrow.append('   ')
                else:
                    mid = row[j].get_str_part(1)
                    mid += 'x' if self.pos == [i,j] else ' '
                    mid += row[j].get_str_part(2)
                    midrow.append(mid)
            print(' '.join(midrow))
            print(' '.join([room.get_str_part(3) if room else '   ' for room in row]))


class Game:
    def __init__(self,prog):
        self.prog = list(prog)
        self.restart()

    def restart(self):
        self.computer = IntcodeComputer(prog)
        self.mapp = Map()

    def iteration(self,command):

        if command:
            input_pipe = list(command.encode())+[10]
        else:
            input_pipe = []

        output_pipe = []

        # print("Executing with input", bytes(input_pipe))

        self.computer.execute(input_pipe,output_pipe)

        ut = bytes(output_pipe).decode()
        print(ut)

        self.mapp.parse_output(ut.splitlines(),command)

        self.mapp.print()

        return self.computer.halted


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = [int(c) for c in open(sys.argv[1]).read().split(',')]

game = Game(prog)

game.iteration('')

class MyCmd(cmd.Cmd):
    def do_exit(self, inp):
        print("Exiting...")
        return True

    def do_EOF(self,inp):
        print("Exiting...")
        return True

    def do_north(self,inp):
        return game.iteration('north')

    def do_south(self,inp):
        return game.iteration('south')

    def do_west(self,inp):
        return game.iteration('west')

    def do_east(self,inp):
        return game.iteration('east')

    def do_take(self,inp):
        return game.iteration('take '+inp)

    def do_drop(self,inp):
        return game.iteration('drop '+inp)

    def do_inv(self,inp):
        return game.iteration('inv')

    def do_restart(self,inp):
        game.restart()
        game.iteration('')


MyCmd().cmdloop()
