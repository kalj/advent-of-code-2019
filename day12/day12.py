#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day12.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import parse
import numpy as np

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

inlines = open(sys.argv[1]).read().splitlines()

ic = []
for line in inlines:
    p = parse.parse("<x={}, y={}, z={}>",line)
    ic.append(list(map(int,p.fixed)))


zeros = np.zeros((len(ic),3))
state = np.concatenate((ic,zeros),axis=1)

initial_state = state.copy()

nmoons = len(ic)

nsteps=1000
steps = 0
print("After {} steps:".format(steps))
print(state)

while True:
    # apply gravity to velocity
    for i in range(nmoons):
        for j in range(nmoons):
            if i != j:
                state[i,3:] += (state[j,0:3] > state[i,0:3]).astype(int) - (state[j,0:3] < state[i,0:3]).astype(int)

    # apply velocity to position
    for i in range(nmoons):
        state[i,0:3] += state[i,3:]

    steps+=1

    ## part 1
    # if steps < nsteps:
    #     break

    if steps % 10000 == 0:
        print("Steps:",steps)

    ## part 2
    if np.all(state == initial_state):
        break

print("After {} steps:".format(steps))
print(state)
print("Energy:")
totsum = 0
for i in range(nmoons):
    pot = sum(abs(state[i,0:3]))
    kin = sum(abs(state[i,3:]))
    tot = pot * kin
    print("pot: {:5g}, kin: {:5g}, tot: {:5g}".format(pot,kin,tot))
    totsum += tot
print("Sum of total energy: {:g}".format(totsum))
