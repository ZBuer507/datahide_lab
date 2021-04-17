import matplotlib.pyplot as plt 
from skimage import data, io
import numpy as np

# prepare const
block_size = 8

A = np.zeros((block_size, block_size))
for i in range(block_size):
    for j in range(block_size):
        A[i, j] = np.cos((2 * i + 1) * j * np.pi / 16)

alpha = np.ones((block_size, block_size), dtype=float)
alpha[0] = 2**-0.5
alpha[:,0] = 2**-0.5
alpha[0, 0] = 0.5

Q =[[16,11,10,16,24,40,51,61],
    [12,12,14,19,26,58,60,55],
    [14,13,16,24,40,57,69,56],
    [14,17,22,29,51,87,80,62],
    [18,22,37,56,68,109,103,77],
    [24,35,55,64,81,104,113,92],
    [49,64,78,87,103,121,120,101],
    [72,92,95,98,112,100,103,99]]

zig = []
sum = 0
while sum <= 2 * (block_size - 1):
    rg = min(sum, block_size - 1)
    if sum % 2 == 0:
        for i in range(sum - rg, rg + 1):
            zig.append((sum - i, i))
    else:
        for i in range(sum - rg, rg + 1):
            zig.append((i, sum - i))
    sum += 1

# func
def block(num):
    top = num // block_per_line * block_size
    left = num % block_per_line * block_size
    return top, left

# 读取图片
image = data.coins()
image = np.array([[52,55,61,66,70,61,64,73],
                    [63,59,55,90,109,85,69,72],
                    [62,59,68,113,144,104,66,73],
                    [63,58,71,122,154,106,70,69],
                    [67,61,68,104,126,88,68,70],
                    [79,65,60,70,77,68,58,75],
                    [85,71,64,59,55,61,65,83],
                    [87,79,69,68,65,76,78,94]], dtype=float)

# 八像素对齐(使用滚筒式)
origin_height = image.shape[0]
origin_width = image.shape[1]
if origin_height % block_size != 0:
    image = np.vstack(
        (image, image[0 : block_size - origin_height % block_size, :])
        )
if origin_width % block_size != 0:
    image = np.hstack(
        (image, image[:, 0 : block_size - origin_width % block_size])
        )
height = image.shape[0]
width = image.shape[1]


block_line_count = height // block_size
block_per_line = width // block_size
block_count = block_line_count * block_per_line

print(height, width, block_line_count, block_per_line, block_count)

# dct变换
dct_image = np.zeros((height, width))
for i in range(block_count):
    top, left = block(i)
    print(top, left)
    dct_image[top:top+block_size, left:left+block_size] = alpha * (A.T @ (image[top:top+block_size, left:left+block_size] - 128) @ A) / 4
print(dct_image)

# 量化
dct_image_after_quantization = np.zeros((height, width), dtype = int)
for i in range(block_count):
    top, left = block(i)
    dct_image_after_quantization[top:top+block_size, left:left+block_size] = np.round(dct_image[top:top+block_size, left:left+block_size] / Q)
print(dct_image_after_quantization)

f = open('test.txt', 'w')
print(np.round(dct_image, 2))
for i in range(height):
    for j in range(width):
        f.write('{:3} '.format(dct_image_after_quantization[i, j]))
    f.write('\n')

# z字形排序
data = []
for i in range(block_count):
    top, left = block(i)
    data.append([])
    for j in range(block_size * block_size):
        row, col = zig[j]
        data[i].append(dct_image_after_quantization[row + top, col + left])
print(data)

# 游程长度编码
rle = []
for block in data:
    tmp = []
    count = 0
    for b in block:
        if b == 0:
            count += 1
        else:
            while count >= 16:
                tmp.append((15, 0))
                count -= 16
            tmp.append((count, b))
            count = 0
    if count > 0:
        tmp.append('EOB')
    rle.append(tmp)
print(rle)

#rle = [[(0,35), (0,7), (3,-6), (0,-2), (2,-9), (15,0), (2,8), 'EOB']]

# bit 编码(todo)
def code(num):
    size = int(np.floor(np.log2(np.abs(num))) + 1)
    c = '{{:0>{}}}'.format(size)
    if num >= 0:
        c = c.format(bin(num)[2:])
    else:
        c = c.format(bin(num + 2**size - 1)[2:])
    return size, c

bit = []
for block in rle:
    tmp = []
    for b in block:
        if b == 'EOB':
            tmp.append('EOB')
            continue
        count = b[0]
        num = b[1]
        print(count, num)
        if num == 0:
            tmp.append((count * 16 + num, '-'))
        else:
            size, c = code(num)
            tmp.append((count * 16 + size, c))
    bit.append(tmp)
print(bit)
        