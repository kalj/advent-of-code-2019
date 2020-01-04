
import sys

if len(sys.argv) != 4:
    print("Insufficient arguments!")
    sys.exit(1)

image_data = list(map(int,open(sys.argv[1]).read()))
width=int(sys.argv[2])
height=int(sys.argv[3])

layer_size = width*height
nlayers = int(len(image_data)/layer_size)

layers = []
for l in range(nlayers):
    offset = l*layer_size
    layers.append(image_data[offset:offset+layer_size])

def count_digit(layer,digit):
    return len([d for d in layer if d==digit])

nzeroes = [count_digit(layer,0) for layer in layers]

# for i,layer in enumerate(layers):
#     print()
#     print("-- Layer",i,"--", "#zeroes:",zeroes[i])
#     for row in layer:
#         print(''.join(map(str,row)))

zl = nzeroes.index(min(nzeroes))

print(zl)

n1s = count_digit(layers[zl],1)
n2s = count_digit(layers[zl],2)

print("nones*ntwos = {}*{} = {}".format(n1s,n2s,n1s*n2s))

image = [2]*layer_size

for layer in layers:
    image = [dl if di==2 else di for di,dl in zip(image,layer)]


for i in range(height):
    row = image[i*width:(i+1)*width]
    line = [' ' if d==0 else 'o' for d in row]
    print(' '.join(line))
