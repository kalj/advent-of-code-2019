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

                    doors_passed_cpy = set(doors_passed)
                    t = mapp_cpy.get(pt)

                    if t in lowercase_alpha:
                        # we found a key!
                        if t > lbl:
                            distances[lbl+t] = (nsteps,doors_passed_cpy)

                    if t != '*' and t!= '#':

                        if t in uppercase_alpha:
                            doors_passed_cpy.add(t)

                        mapp_cpy.set(pt,'*')
                        wavefronts_new.append((pt,doors_passed_cpy))

            wavefronts = wavefronts_new
            nsteps += 1

    return distances

class SuperMap:
    def __init__(self,arg):
        if type(arg) == SuperMap:
            self.submaps = [Map(sm) for sm in arg.submaps]
            self.height = arg.height
            self.width = arg.width
        else:
            lines = arg
            self.height = len(lines)
            self.width = len(lines[0])

            splitrow = self.height//2
            splitcol = self.width//2
            sublines = [
                [l[0:1+splitcol] for l in lines[0:1+splitrow]],
                [l[splitcol:] for l in lines[0:1+splitrow]],
                [l[0:1+splitcol] for l in lines[splitrow:]],
                [l[splitcol:] for l in lines[splitrow:]]
                ]
            self.submaps = [Map(sl) for sl in sublines]

    def print(self):
        # compact = False
        compact = True

        for o in [0,2]:
            if compact:
                istart = 0 if o==0 else 1
            else:
                istart = 0
            for l1,l2 in zip(self.submaps[o].teh_map[istart:],self.submaps[o+1].teh_map[istart:]):
                if compact:
                    print("{}{}".format(''.join(l1[:-1]),''.join(l2)))
                else:
                    print("{} {}".format(''.join(l1),''.join(l2)))

            if not compact and o==0:
                print()

def key_str(starts,tgtsets):
    return '{}:{}'.format(''.join(starts),''.join(sorted(set.union(*tgtsets))))

def get_optimal_path(paths, tgtsets, starts, acquired_keys, distances):
    key = key_str(starts,tgtsets)

    if not key in paths:

        distance = None
        path = None
        for mi in range(4):
            for tgt in tgtsets[mi]:

                pair = ''.join(sorted([starts[mi],tgt]))
                self_distance, required_doors = distances[mi][pair]
                required_keys = {d.lower() for d in required_doors}

                if not required_keys.issubset(acquired_keys):
                    continue

                new_acquired_keys = set(acquired_keys)
                new_acquired_keys.add(tgt)

                new_starts = list(starts)
                new_starts[mi] = tgt

                new_tgtsets = [set(s) for s in tgtsets]
                new_tgtsets[mi] = new_tgtsets[mi].difference({tgt})

                if sum(len(s) for s in new_tgtsets) == 0:
                    d = 0
                    p = ''
                else:
                    d,p = get_optimal_path(paths, new_tgtsets, new_starts, new_acquired_keys, distances)

                dd = d+self_distance
                pp = tgt+p
                if distance == None or dd < distance:
                    distance = dd
                    path = pp

        if distance == None:
            raise Exception("Didn't find any path for key={} - distance was None".format(key))

        paths[key] = [distance,path]

    return paths[key]

def get_shortest_path(mapp: SuperMap):

    keysets = []
    distances = []
    for i,sm in enumerate(mapp.submaps):
        ks = {k for k in lowercase_alpha if sm.get_tile_locations(k)}

        locations=sorted(list(ks)+['@'])
        dists = compute_distances(locations,sm)
        # print("distances computed for map {}:".format(i))
        # for k,v in dists.items():
        #     dist,doors = v
        #     print(k,dist, ''.join(sorted(doors)))

        distances.append(dists)
        keysets.append(ks)

    optimal_paths = {}
    starts = ['@','@','@','@']

    dist,path = get_optimal_path(optimal_paths, keysets, starts, set(), distances)
    return path, dist

if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

the_input = open(sys.argv[1]).read().splitlines()

mapp = SuperMap(the_input)

# mapp.print()

path,dist = get_shortest_path(mapp)

print()
print("Shortest path:",path)
print("Distance:     ",dist)
