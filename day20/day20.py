#!/usr/bin/env python3

import sys

uppercase_alpha = bytes(list(range(ord('A'),ord('Z')+1))).decode()
lowercase_alpha = bytes(list(range(ord('a'),ord('z')+1))).decode()

def get_surrounding_positions(pos, height, width):

    valid_pos = []
    for dim in [0,1]:
        for o in [-1,1]:
            newpos = [pos[0],pos[1]]
            newpos[dim] += o
            if newpos[0] >= 0 and newpos[0] < height and newpos[1] >= 0 and newpos[1] < width:
                valid_pos.append(newpos)
    return valid_pos


class Map:
    def __init__(self,arg):
        if type(arg) == Map:
            self.teh_map = [list(line) for line in arg.teh_map]
            self.height = arg.height
            self.width = arg.width
        else:
            teh_map = arg
            self.height = len(teh_map)
            self.width = 0
            for l in teh_map:
                self.width = max(self.width,len(l))

            self.teh_map = [list(line)+[' ']*(self.width-len(line)) for line in teh_map]


    def print(self):
        for l in self.teh_map:
            print(''.join(l))

    def get(self,pt):
        return self.teh_map[pt[0]][pt[1]]

    def set(self,pt,t):
        self.teh_map[pt[0]][pt[1]] = t

    def get_tile_locations(self,t):
        return [[i,j] for i in range(self.height) for j in range(self.width) if self.get([i,j])==t]

def get_labels(mapp):
    labels = {}

    for i in range(1,mapp.height-1):
        for j in range(1,mapp.width-1):

            this_tile = mapp.get([i,j])
            sur = [(mapp.get(p),p) for p in get_surrounding_positions([i,j],mapp.height,mapp.width)]


            # print('this tile:',this_tile,"sur:",sur)

            sur_dot   = [s for s in sur if s[0]=='.']
            sur_space = [s for s in sur if s[0]==' ']
            sur_alpha = [s for s in sur if s[0] in uppercase_alpha]


            # print("sur_dot:",sur_dot)
            # print("sur_space:",sur_space)
            # print("sur_alpha:",sur_alpha)

            if this_tile in uppercase_alpha and len(sur_dot) == 1 and len(sur_alpha) == 1:
                other_tile = sur_alpha[0]

                if other_tile[1][0] < i or other_tile[1][1] < j: # label on top or left edge -> current tile second
                    label_name = other_tile[0]+this_tile
                else:
                    label_name = this_tile+other_tile[0]

                if label_name in labels:
                    labels[label_name].append(sur_dot[0][1])
                else:
                    labels[label_name] = [sur_dot[0][1]]

    return labels

def find_shortest_path_len(mapp_in):

    mapp = Map(mapp_in)

    labels = get_labels(mapp)

    startpos = labels['AA'][0]
    target =   labels['ZZ'][0]
    portals = {k:v for k,v in labels.items() if len(v)==2}

    # for n in portals:
    #     print(n,portals[n])

    mapp.set(startpos,'@')
    wavefronts = [startpos]
    nsteps = 0

    target_found = False
    while not target_found and len(wavefronts) > 0:

        wavefronts_new = []
        for wpos in wavefronts:

            sur = get_surrounding_positions(wpos,mapp.height,mapp.width)
            match_portals = [v for v in portals.values() if wpos in v]
            if len(match_portals) > 1:
                raise Exception("Unexpectedly matched more than one portal: {}".format(match_portals))
            if len(match_portals) == 1:
                portal = match_portals[0]
                # print("point {} matched portal {}".format(wpos,portal))
                newsur = portal[0] if portal[1]==wpos else portal[1]
                # print("adding new neighbor",newsur)
                sur.append(newsur)

            for pt in sur:

                t = mapp.get(pt)

                if t == '#' or t=='@' or t in uppercase_alpha:
                    continue

                if t == '.':
                    mapp.set(pt,'@')
                    # line = mapp[pt[0]]
                    # mapp[pt[0]] = line[0:pt[1]]+'@'+line[pt[1]+1:]
                    if pt == target:
                        target_found = True
                        break

                    wavefronts_new.append(pt)

        wavefronts = wavefronts_new
        nsteps += 1
        print("=== After {} steps ===".format(nsteps))
        mapp.print()

    if not target_found:
        raise Exception("Failed finding path to target!")
    return nsteps

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

the_input = open(sys.argv[1]).read().splitlines()

mapp = Map(the_input)

mapp.print()

nsteps = find_shortest_path_len(mapp)

print("Reached target in {} steps".format(nsteps))
