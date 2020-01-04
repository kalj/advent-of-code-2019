import sys

def trace(path):
    coords = [(0,0)]
    for p in path:
        direction = p[0]
        length = int(p[1:])

        if direction == 'R':
            op = lambda c: (c[0]+1,c[1])
        elif direction == 'L':
            op = lambda c: (c[0]-1,c[1])
        elif direction == 'U':
            op = lambda c: (c[0],c[1]+1)
        elif direction == 'D':
            op = lambda c: (c[0],c[1]-1)
        else:
            raise Exception('Invalid direction')

        for i in range(length):
            coords.append(op(coords[-1]))
    return coords

def get_segments(path):
    segments = []
    coord = (0,0)
    for p in path:
        direction = p[0]
        length = int(p[1:])

        if direction == 'R':
            newcoord = (coord[0]+length,coord[1])
        elif direction == 'L':
            newcoord = (coord[0]-length,coord[1])
        elif direction == 'U':
            newcoord = (coord[0],coord[1]+length)
        elif direction == 'D':
            newcoord = (coord[0],coord[1]-length)
        else:
            raise Exception('Invalid direction')

        segments.append((coord,newcoord))
        coord = newcoord

    return segments

def plot_coords(coords):

    xmin = min(c[0] for c in coords)
    xmax = max(c[0] for c in coords)
    ymin = min(c[1] for c in coords)
    ymax = max(c[1] for c in coords)

    for y in reversed(range(ymin,ymax+1)):
        row = ' '*(xmax-xmin)
        rowcoords = [c[0] for c in coords if c[1] == y]
        for x in rowcoords:
            if x==0 and y==0:
                marker = 'O'
            else:
                marker = '*'
            idx = x-xmin
            row = row[0:idx]+marker+row[idx+1:]

        print(row)

def trace_segment(segment):
    coords = [segment[0]]

    diff = (segment[1][0]-segment[0][0],segment[1][1]-segment[0][1])
    if diff[0] == 0:
        # vertical
        length=abs(diff[1])
        sign = int(diff[1]/length)
        coords = [(segment[0][0],segment[0][1]+sign*i) for i in range(length+1)]
    else:
        # horizontal
        length=abs(diff[0])
        sign = int(diff[0]/length)
        coords = [(segment[0][0]+sign*i,segment[0][1]) for i in range(length+1)]
    return coords

def intersect(s1,s2):
    xmin1 = min(s1[0][0],s1[1][0])
    xmax1 = max(s1[0][0],s1[1][0])
    ymin1 = min(s1[0][1],s1[1][1])
    ymax1 = max(s1[0][1],s1[1][1])

    xmin2 = min(s2[0][0],s2[1][0])
    xmax2 = max(s2[0][0],s2[1][0])
    ymin2 = min(s2[0][1],s2[1][1])
    ymax2 = max(s2[0][1],s2[1][1])

    if xmax2 >= xmin1 and xmin2 <= xmax2 and \
       ymax2 >= ymin1 and ymin2 <= ymax2:
        path1 = trace_segment(s1)
        path2 = trace_segment(s2)
        intersections = []
        for c in path1:
            if c in path2:
                intersections.append(c)
        return intersections
    return None

def find_intersections(segments1,segments2):
    intersections = []
    for i,s1 in enumerate(segments1):
        print("Intersecting with segment {} ({})...".format(i,s1))
        for s2 in segments2:
            intersection = intersect(s1,s2)
            if intersection:
                intersections.extend(intersection)
                print("intersections:",intersections)
    return intersections

def dist(c):
    return abs(c[0])+abs(c[1])

infile = sys.argv[1]

paths = [l.split(',') for l in open(infile).read().splitlines()]
print('read paths')

segments = [get_segments(p) for p in paths]
print('segments extracted')
print("nsegments: {}, {}".format(len(segments[0]),len(segments[1])))

intersections = find_intersections(segments[0],segments[1])
print('intersections found')
intersections = filter(lambda i: i[0] != 0 and i[1] != 0,intersections)

closest = sorted(intersections,key=dist)


print(closest[0], "->", dist(closest[0]))
