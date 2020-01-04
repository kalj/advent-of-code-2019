
import sys

def execute(state):

    pc = 0

    while True:
        opcode = state[pc]

        if opcode == 99:
            break
        if opcode == 1:
            operation = lambda a,b: a+b
        elif opcode == 2:
            operation = lambda a,b: a*b
        else:
            raise Exception('invalid opcode {} at {}'.format(opcode, pc))

        in1addr = state[pc+1]
        in2addr = state[pc+2]
        outaddr = state[pc+3]

        state[outaddr] = operation(state[in1addr],state[in2addr])

        pc += 4

def prepare_state(state,noun,verb):
    state[1] = noun
    state[2] = verb

def compute_output(initial_state,noun,verb):
    state = list(initial_state)
    prepare_state(state,noun,verb)
    execute(state)
    return state[0]

def look_for_output(initial_state,desired_output):
    for noun in range(0,100):
        for verb in range(0,100):
            output = compute_output(state,noun,verb)
            print("Testing nount={}, verb={}...".format(noun,verb))
            if output == desired_output:
                return noun,verb
    raise Exception("No pairs noun,verb gave the desired output {}".format(desired_output))


if len(sys.argv) != 2:
    print("need input!")
    sys.exit(1)

data = open(sys.argv[1]).read()

state = list(map(int,data.split(',')))

## Part 1
# print("-- Initial state --")
# print(state)
# prepare_state(state,12,2)
# print("-- Prepared state --")
# print(state)
# execute(state)
# print("-- Final state --")
# print(state)

## Part 2
desired_output = 19690720

noun,verb = look_for_output(state,desired_output)

print()
print("Found input (noun={}, verb={}) yielding output {}".format(noun,verb,desired_output))
