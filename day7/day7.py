
import itertools
import sys

class IntcodeComputer:
    def __init__(self,state):
        self.state = list(state)
        self.pc = 0
        self.halted = False

    def execute(self, input_queue, output_queue):

        if self.halted:
            raise Exception("Cannot execute computer, already halted")

        while True:

            opcode = self.state[self.pc] % 100
            opmode = self.state[self.pc] // 100

            # print("pc: {}, opcode: {}, opmode: {}".format(pc,opcode,opmode))

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

                in1 = self.state[self.pc+1]
                in2 = self.state[self.pc+2]
                outaddr = self.state[self.pc+3]

                opmode1 = opmode % 10
                opmode2 = (opmode//10) % 10

                arg1 = in1 if opmode1==1 else self.state[in1]
                arg2 = in2 if opmode2==1 else self.state[in2]

                self.state[outaddr] = operation(arg1,arg2)

                self.pc += 4
            elif opcode == 3:
                # read input
                outaddr = self.state[self.pc+1]

                if len(input_queue) == 0:
                    # waiting for input...
                    break

                # have enough input
                self.state[outaddr] = input_queue.pop(0)

                self.pc += 2

            elif opcode == 4:
                # write output
                in1 = self.state[self.pc+1]
                opmode1 = opmode % 10
                arg1 = in1 if opmode1==1 else self.state[in1]

                output_queue.append(arg1)
                self.pc += 2

            elif opcode in [5,6]:
                if opcode == 5:
                    # jump-if-true
                    cond = lambda a: a != 0
                elif opcode == 6:
                    # jump-if-false
                    cond = lambda a: a == 0

                in1 = self.state[self.pc+1]
                in2 = self.state[self.pc+2]

                opmode1 = opmode % 10
                opmode2 = (opmode//10) % 10

                arg1 = in1 if opmode1==1 else self.state[in1]
                arg2 = in2 if opmode2==1 else self.state[in2]

                if cond(arg1):
                    self.pc = arg2
                else:
                    self.pc += 3

            else:
                raise Exception('invalid opcode {} at {}'.format(opcode, self.pc))

def get_output(state, phase_settings):

    signal = 0

    for i,s in enumerate(phase_settings):
        comp = IntcodeComputer(state)

        input_pipe = [s,signal]
        output_pipe = []
        comp.execute(input_pipe, output_pipe)

        signal = output_pipe[0]

    return signal

def get_output_feedback(state, phase_settings):

    computers = [IntcodeComputer(state) for i in range(5)]

    pipes = [[phase_settings[i]] for i in range(5)]

    # add initial input
    pipes[0].append(0)

    done = False

    while not done:
        for i in range(5):
            computers[i].execute(pipes[i],pipes[(i+1)%5])
        halted = [c.halted for c in computers]
        if any(halted):
            if not all(halted):
                raise Exception("Not all computers halted at the same time: {}".format(halted))
            done = True

    # print("final state of pipes:",pipes)
    # get output
    return pipes[0][0]


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

prog = open(sys.argv[1]).read()

state = list(map(int,prog.split(',')))

## part 1
# phase_settings_values = [0,1,2,3,4]

## part 2
phase_settings_values = [5,6,7,8,9]

max_phase_settings = None
max_output = -1

for ps in itertools.permutations(phase_settings_values):
    ## part 1
    # o = get_output(state,ps)

    ## part 2
    o = get_output_feedback(state,ps)

    if o > max_output:
        max_output = o
        max_phase_settings = ps

print(max_phase_settings,"->",max_output)
