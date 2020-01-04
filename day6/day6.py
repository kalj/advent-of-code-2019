#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day6.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import graphviz

if len(sys.argv) < 2:
    print("too few arguments")
    sys.exit(1)
inputfile = sys.argv[1]
out_gv='out.gv'

data = open(inputfile).read().splitlines()
data = [l for l in data if l.strip()]

edges = [l.split(')') for l in data]

nodes = list(set([n for e in edges for n in e ]))

def count_orbits(root,nparents=0):
    children = [e[1] for e in edges if e[0]==root]
    return nparents+sum([count_orbits(c,nparents+1) for c in children])

norbits = count_orbits('COM')

print("norbits:",norbits)


# dot = graphviz.Digraph()

# for n in nodes:
#     dot.node(n)

# dot.edges(edges)

# dot.render(out_gv)


## Part 2

def make_chain(obj):
    chain=[obj]
    while True:
        parents = [e[0] for e in edges if e[1] == obj]
        if len(parents) > 1:
            raise Exception("{} has multiple parents: {}".format(obj,', '.join(parents)))
        elif len(parents) < 1:
            break

        parent=parents[0]

        chain.insert(0,parent)
        obj = parent

    return chain

you_chain = make_chain("YOU")
san_chain = make_chain("SAN")
print("YOU chain:")
print(" -> ".join(you_chain))
print("SAN chain:")
print(" -> ".join(san_chain))

ncommon=0
while you_chain[ncommon] == san_chain[ncommon]:
    ncommon+=1


you_subchain = you_chain[ncommon-1:]
san_subchain = san_chain[ncommon-1:]
print("Last common parent is",you_subchain[0])

# print("List of transfers:")
# for i in reversed(range(1,len(you_subchain)-1)):
#     print("{}: {} -> {}".format(i,you_subchain[i],you_subchain[i-1]))

# for i in range(len(san_subchain)-2):
#     print("{}: {} -> {}".format(i,san_subchain[i],san_subchain[i+1]))

ntransfers = len(you_subchain[:-2]) + len(san_subchain[:-2])
print("Number of transfers:",ntransfers)
