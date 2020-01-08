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


def compute_distances(labels, mapp):

    distances = {}
    for lbl in labels:
        startpos = mapp.get_tile_locations(lbl)[0]

        mapp_cpy = Map(mapp)
        mapp_cpy.set(startpos,'*')
        wavefronts = [(startpos,set())]
        nsteps = 1

        while len(wavefronts) > 0:

            wavefronts_new = []
            for wpos,doors_passed in wavefronts:

                sur = get_surrounding_positions(wpos,mapp_cpy.height,mapp_cpy.width)
                for pt in sur:
                    t = mapp_cpy.get(pt)

                    if t in lowercase_alpha:
                        # we found a key!
                        if t > lbl:
                            distances[lbl+t] = (nsteps,doors_passed)
                    if t != '*' and t!= '#':

                        if t in uppercase_alpha:
                            doors_passed = set(doors_passed)
                            doors_passed.add(t)

                        mapp_cpy.set(pt,'*')
                        # line = mapp[pt[0]]
                        # mapp[pt[0]] = line[0:pt[1]]+'@'+line[pt[1]+1:]
                        wavefronts_new.append((pt,doors_passed))

            wavefronts = wavefronts_new
            nsteps += 1


    return distances

def key_str(start,tgtset):
    return start+':'+''.join(sorted(tgtset))

def get_optimal_path(paths, tgtset, start, acquired_keys, distances):
    key = key_str(start,tgtset)

    # print("get_optimal_path for {} ({})".format(key,acquired_keys))

    if not key in paths:
        # print("key WAS NOT in paths")

        if len(tgtset) == 1:
            for tgt in tgtset:
                # print("tgtset has len 1 ({})".format(tgt))
                pair = ''.join(sorted([start,tgt]))
                distance,required_doors = distances[pair]
                required_keys = {d.lower() for d in required_doors}
                path = start+tgt
                if not required_keys.issubset(acquired_keys):
                    # print("do not have enough keys: {} vs {}".format(required_keys,acquired_keys))
                    distance = None
            # print("Found distance={} and path={}".format(distance,path))

        else:

            distance = None
            path = None

            for tgt in tgtset:
                # print("trying tgt {} in tgtset {}".format(tgt,tgtset))

                pair = ''.join(sorted([start,tgt]))
                self_distance, required_doors = distances[pair]
                required_keys = {d.lower() for d in required_doors}

                if not required_keys.issubset(acquired_keys):
                    # print("do not have enough keys: {} vs {}".format(required_keys,acquired_keys))
                    continue
                new_acquired_keys = set(acquired_keys)
                new_acquired_keys.add(tgt)

                rest = tgtset.difference({tgt})

                d,p = get_optimal_path(paths,rest, tgt, new_acquired_keys, distances)

                if not d or not p:
                    # print("optimal path for tgt {} has null distance ({}) or path ({})".format(tgt,d,p))
                    continue

                dd = d+self_distance
                pp = start+p
                if distance == None or dd < distance:
                    distance = dd
                    path = pp


        paths[key] = [distance,path]
    # else:
        # print("key WAS in paths")


    return paths[key]

def get_shortest_path_smart(mapp, pos):

    keyset = {k for k in lowercase_alpha if mapp.get_tile_locations(k)}

    locations=sorted(list(keyset)+['@'])
    distances = compute_distances(locations,mapp)
    print("distances computed")

    # for k in distances:
        # print(k,distances[k][0], ''.join(sorted(distances[k][1])))

    optimal_paths = {}

    dist,path = get_optimal_path(optimal_paths,keyset, '@',set(), distances)
    return path, dist

    # return path[1:],dist


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

the_input = open(sys.argv[1]).read().splitlines()

mapp = Map(the_input)

mapp.print()

initial_pos = mapp.get_tile_locations('@')[0]
print("Pos:",initial_pos)

path,dist = get_shortest_path_smart(mapp,initial_pos)

print()
print("Shortest path:",path)
print("Distance:     ",dist)
