#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @(#)day10.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys
import numpy as np
from operator import itemgetter

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

lines = open(sys.argv[1]).read().splitlines()

mapp = []
for i,l in enumerate(lines):
    for j,c in enumerate(l):
       if c == '#':
           mapp.append(np.array([j,i]))

def my_angle(d):
    raw_angle = np.arctan2(d[1],d[0])
    angle  = (np.pi/2+raw_angle)%(np.pi*2)
    return angle


def get_visible(coord, mapp):

    direction_bins = {}
    for tgt in mapp:
        if np.array_equal(tgt,coord):
            continue
        diff = tgt-coord
        x = diff[0]
        y = diff[1]
        n = np.gcd(x,y)

        distance = np.linalg.norm(diff)
        direction = tuple(diff/n)

        # print("{:10s} {:10d} {:10g} {:20s}".format(str(tgt),n,distance,str(direction)))

        if not direction in direction_bins:
            direction_bins[direction] = []

        direction_bins[direction].append((distance,tgt))

    angle_bins = { my_angle(d):sorted(v) for d,v in direction_bins.items() }

    # for angle in angle_bins:
        # print("{:15s} {}".format(str(angle),angle_bins[angle]))

    return angle_bins


visible = [(coord,get_visible(coord,mapp)) for coord in mapp]

nmax = 0
imax = -1
for i,v in enumerate(visible):
    coord = v[0]
    entries = v[1]
    n_entries = len(v[1])
    if n_entries > nmax:
        nmax = n_entries
        imax = i

refcoord,angle_bins = visible[imax]
print(refcoord,len(angle_bins))

angles = sorted(angle_bins.keys())

# for a,bin in sorted(angle_bins.items()):
#     print("{:14.6g} {}".format(a, bin))

pts = []
done = False
while not done:
    done = True
    for a in angles:
        current_bin = angle_bins[a]
        if len(current_bin) > 0:
            next_entry = current_bin.pop(0)
            pts.append(next_entry[1])

        if len(current_bin) > 0:
            done = False


# for i,pt in enumerate(pts):
#     print(i,pt)

print("Point 200:",pts[199])

# for a,bin in sorted(angle_bins.items()):
#     print("{:14.6g} {}".format(a, bin))


# import matplotlib.pyplot as plt

# ptarr = np.array(pts)
# plt.plot(ptarr[:,0], -ptarr[:,1],'o-')
# plt.plot(refcoord[0],-refcoord[1],'x')
# arrows = ptarr[1:,:]-ptarr[:-1,:]
# plt.quiver(ptarr[:-1,0],-ptarr[:-1,1],arrows[:,0],-arrows[:,1])
# plt.show()


# pts = []

# for a,bin in sorted(angle_bins.items()):
#     print("{:14.6g} {}".format(a, bin))

#     for c,dist in bin:
#         # pts.append(c)
#         pts.append(np.array([refcoord[0]+dist*np.sin(a),refcoord[1]-dist*np.cos(a)]))

# import matplotlib.pyplot as plt

# x = np.array(pts)[:,0]
# y = np.array(pts)[:,1]
# plt.plot(x, -y,'o')
# plt.plot(refcoord[0],-refcoord[1],'x')
# plt.show()
