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
            self.teh_map = [list(line) for line in teh_map]
            self.height = len(teh_map)
            self.width = len(teh_map[0])

    def print(self):
        for l in self.teh_map:
            print(''.join(l))

    def get(self,pt):
        return self.teh_map[pt[0]][pt[1]]

    def set(self,pt,t):
        self.teh_map[pt[0]][pt[1]] = t

    def get_tile_locations(self,t):
        return [[i,j] for i in range(self.height) for j in range(self.width) if self.get([i,j])==t]

    def get_accessible_keys(self,pos):

        mapp = Map(self)
        found_keys = []
        wavefronts = [pos]
        nsteps = 1

        while len(wavefronts) > 0:

            wavefronts_new = []
            for wpos in wavefronts:

                sur = get_surrounding_positions(wpos,self.height,self.width)
                for pt in sur:
                    t = mapp.get(pt)

                    if t == '#' or t in uppercase_alpha:
                        continue
                    if t in lowercase_alpha:
                        # we found a key!
                        found_keys.append([t,pt,nsteps])
                    if t == '.':
                        mapp.set(pt,'@')
                        # line = mapp[pt[0]]
                        # mapp[pt[0]] = line[0:pt[1]]+'@'+line[pt[1]+1:]
                        wavefronts_new.append(pt)

            wavefronts = wavefronts_new
            nsteps += 1

        return found_keys


def get_shortest_path_bruteforce(mapp, pos):

    accessible_keys = mapp.get_accessible_keys(pos)

    paths = []

    for ak in accessible_keys:

        key, kpos, kdist = ak
        mapp_copy = Map(mapp)

        # move position and remove key
        mapp_copy.set(pos,'.')
        mapp_copy.set(kpos,'@')
        # remove door/block
        door_locations = mapp_copy.get_tile_locations(key.upper())
        for dl in door_locations:
            mapp_copy.set(dl,'.')

        keys,dist = get_shortest_path_bruteforce(mapp_copy,kpos)
        paths.append([[key]+keys,dist+kdist])

    if len(paths) == 0:
        return [[],0]

    paths.sort(key=lambda p: p[1])

    return paths[0]



def compute_distances(labels, mapp):

    distances = {}
    for lbl in labels:
        startpos = mapp.get_tile_locations(lbl)[0]

        mapp_cpy = Map(mapp)
        mapp_cpy.set(startpos,'*')
        wavefronts = [startpos]
        nsteps = 1

        while len(wavefronts) > 0:

            wavefronts_new = []
            for wpos in wavefronts:

                sur = get_surrounding_positions(wpos,mapp_cpy.height,mapp_cpy.width)
                for pt in sur:
                    t = mapp_cpy.get(pt)

                    if t in lowercase_alpha:
                        # we found a key!
                        if t > lbl:
                            distances[lbl+t] = nsteps
                    if t != '*' and t!= '#':
                        mapp_cpy.set(pt,'*')
                        # line = mapp[pt[0]]
                        # mapp[pt[0]] = line[0:pt[1]]+'@'+line[pt[1]+1:]
                        wavefronts_new.append(pt)

            wavefronts = wavefronts_new
            nsteps += 1


    return distances

def key_str(start,tgtset):
    return start+':'+''.join(sorted(tgtset))

def get_optimal_path(dst, start, tgtset, distances):
    key = key_str(start,tgtset)

    if not key in dst:

        if len(tgtset) == 1:
            for tgt in tgtset:
                pair = ''.join(sorted([start,tgt]))
                distance = distances[pair]
                path = start+tgt

        else:

            distance = 2**63-1
            path = None

            for tgt in tgtset:
                pair = ''.join(sorted([start,tgt]))
                self_distance = distances[pair]

                rest = tgtset.difference({tgt})

                d,p = get_optimal_path(dst,tgt,rest,distances)

                dd = d+self_distance
                pp = start+p
                if dd < distance:
                    distance = dd
                    path = pp

        dst[key] = [distance,path]

    return dst[key]

def get_shortest_path_smart(mapp, pos):

    keyset = {k for k in lowercase_alpha if mapp.get_tile_locations(k)}

    locations=sorted(list(keyset)+['@'])
    distances = compute_distances(locations,mapp)
    print("distances computed")

    # for k in distances:
    #     print(k,distances[k])

    optimal_paths = {}

    dist,path = get_optimal_path(optimal_paths,'@',keyset, distances)

    return path[1:],dist


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

the_input = open(sys.argv[1]).read().splitlines()

mapp = Map(the_input)

mapp.print()

initial_pos = mapp.get_tile_locations('@')[0]
print("Pos:",initial_pos)

# path,dist = get_shortest_path_bruteforce(mapp,initial_pos)

# print()
# print("Shortest path:",''.join(path))
# print("Distance:     ",dist)

path,dist = get_shortest_path_smart(mapp,initial_pos)

print()
print("Shortest path:",path)
print("Distance:     ",dist)
