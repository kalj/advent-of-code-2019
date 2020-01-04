
import sys

def execute(state,input_data):

    input_data  = list(input_data)
    output_data = []
    pc = 0

    while True:

        opcode = state[pc] % 100
        opmode = state[pc] // 100

        # print("pc: {}, opcode: {}, opmode: {}".format(pc,opcode,opmode))

        if opcode == 99:
            # halt
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

            in1 = state[pc+1]
            in2 = state[pc+2]
            outaddr = state[pc+3]

            opmode1 = opmode % 10
            opmode2 = (opmode//10) % 10

            arg1 = in1 if opmode1==1 else state[in1]
            arg2 = in2 if opmode2==1 else state[in2]

            state[outaddr] = operation(arg1,arg2)

            pc += 4
        elif opcode == 3:
            # read input
            outaddr = state[pc+1]

            state[outaddr] = input_data.pop(0)

            pc += 2

        elif opcode == 4:
            # write output
            in1 = state[pc+1]
            opmode1 = opmode % 10
            arg1 = in1 if opmode1==1 else state[in1]

            output_data.append(arg1)
            pc += 2

        elif opcode in [5,6]:
            if opcode == 5:
                # jump-if-true
                cond = lambda a: a != 0
            elif opcode == 6:
                # jump-if-false
                cond = lambda a: a == 0

            in1 = state[pc+1]
            in2 = state[pc+2]

            opmode1 = opmode % 10
            opmode2 = (opmode//10) % 10

            arg1 = in1 if opmode1==1 else state[in1]
            arg2 = in2 if opmode2==1 else state[in2]

            if cond(arg1):
                pc = arg2
            else:
                pc += 3

        else:
            raise Exception('invalid opcode {} at {}'.format(opcode, pc))

    return output_data

## part 1
# if len(sys.argv) != 2:
#     print("Insufficient arguments!")
#     sys.exit(1)

# prog = open(sys.argv[1]).read()
# input_data = [1]

## part 2
if len(sys.argv) != 3:
    print("Insufficient arguments!")
    sys.exit(1)

prog = open(sys.argv[1]).read()
input_data = [int(sys.argv[2])]

state = list(map(int,prog.split(',')))

# print("Initial state: {}".format(state))

output_data = execute(state,input_data)

print()
print("Final state: {}".format(state))
print("Output: {}".format(output_data))
