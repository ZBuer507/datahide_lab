import matplotlib.pyplot as plt 
from skimage import data, io
import numpy as np

class jpeg:
    
    block_size = None
    trans_array = None

    image = None
    origin_height = None
    origin_width = None
    
    height = None
    width = None

    dct_image = None

    def alpha(self, u):
        if u == 0:
            return 2**-0.5
        else:
            return 1

    def magic(self, u):
        return self.trans_array[u]

    def block(self, target_img, count):
        return target_img


    def __init__(self):
        # init block_size
        self.block_size = 8
        
        # init trans_array
        self.trans_array = {}
        for u in range(block_size):
            array = np.zeros((block_size, 1))
            for i in range(block_size):
                array[i, 0] = np.cos((2 * i + 1) * u * np.pi / 16)
            self.trans_array[u] = array
        
        # init image
        self.image = data.coins()
        self.origin_height = self.image.shape[0]
        self.origin_width = self.image.shape[1]

        # padding image
        if origin_height % block_size != 0:
            self.image = np.vstack(
                (self.image, self.image[0 : block_size - origin_height % block_size, :])
            )
        if origin_width % block_size != 0:
            self.image = np.hstack(
                (self.image, self.image[:, 0 : block_size - origin_width % block_size])
            )
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]

        # dct trans
        self.dct_image = np.zeros((height, width))
        for uu in range(width):
            for vv in range(height):
                u = uu % block_size
                v = vv % block_size
                image_block = block(image, uu, vv) - 128
                self.dct_image[vv, uu] = alpha(u) * alpha(v) * magic(v).T @ image_block @ magic(u) / 4

block_size = 8

trans_array = {} # u : array(u)
A = np.zeros((block_size, block_size))
for i in range(block_size):
    for j in range(block_size):
        A[i, j] = np.cos((2 * i + 1) * j * np.pi / 16)

for u in range(block_size):
    array = np.zeros((block_size, 1))
    for i in range(block_size):
        array[i, 0] = np.cos((2 * i + 1) * u * np.pi / 16)
    trans_array[u] = array
# print(trans_array)

def alpha(u):
    if u == 0:
        return 2**-0.5
    else:
        return 1

def magic(u):
    return trans_array[u]

def block(target_img, uu, vv):
    return target_img[vv - vv % block_size:vv - vv % block_size + block_size, uu - uu % block_size: uu - uu % block_size + block_size]


# image = data.coins()
image = np.array([[52,55,61,66,70,61,64,73],
                    [63,59,55,90,109,85,69,72],
                    [62,59,68,113,144,104,66,73],
                    [63,58,71,122,154,106,70,69],
                    [67,61,68,104,126,88,68,70],
                    [79,65,60,70,77,68,58,75],
                    [85,71,64,59,55,61,65,83],
                    [87,79,69,68,65,76,78,94]], dtype=float)

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

# def block(target_img, num):
#     top = num * block_size // block_per_line
#     left = num * block_size % block_per_line
#     return target_img[top : top + block_size, left : left + block_size]

dct_image = np.zeros((height, width))
for uu in range(width):
    for vv in range(height):
        u = uu % block_size
        v = vv % block_size
        image_block = block(image, uu, vv) - 128
        #dct_image[vv, uu] = alpha(u) * alpha(v) * magic(v).T @ image_block @ magic(u) / 4
        dct_image[vv, uu] = magic(v).T @ image_block @ magic(u)
print(dct_image)

Q = [[16,11,10,16,24,40,51,61],
[12,12,14,19,26,58,60,55],
[14,13,16,24,40,57,69,56],
[14,17,22,29,51,87,80,62],
[18,22,37,56,68,109,103,77],
[24,35,55,64,81,104,113,92],
[49,64,78,87,103,121,120,101],
[72,92,95,98,112,100,103,99]]
dct_image_after_quantization = np.zeros((height, width))
for uu in range(width):
    for vv in range(height):
        # dct_image_after_quantization[vv - vv % block_size:vv - vv % block_size + block_size, uu - uu % block_size: uu - uu % block_size + block_size] = 
        pass


# dct_image = np.zeros((height, width))
# for i in range(width // block_size):
#     for j in range(height // block_size):
#         for uu in range(block_size * i, block_size * (i + 1)):
#             for vv in range(block_size * j, block_size * (j + 1)):
#                 u = uu - block_size * i
#                 v = vv - block_size * j
#                 magic_sum = 0
#                 for xx in range(block_size * i, block_size * (i + 1)):
#                     for yy in range(block_size * j, block_size * (j + 1)):
#                         x = xx - block_size * i
#                         y = yy - block_size * j
#                         magic_sum += (image[yy, xx] - 128) * np.cos((2 * x + 1) * u * np.pi / 16) * np.cos((2 * y + 1) * v * np.pi / 16)
#                 dct_image[vv, uu] = alpha(u) * alpha(v) * magic_sum / 4
# print(dct_image)

# block_list = []
# for i in range(width // block_size):
#     for j in range(height // block_size):
#         block_list.append(
#             image[
#                 block_size * i : block_size * (i + 1),
#                 block_size * j : block_size * (j + 1)
#                 ]
#             )
# print(block_list)
# for block in block_list:
#     for u in range(block_size):
#         for v in range(block_size):
#             magic_sum = 0
#             for x in range(block_size * i, block_size * (i + 1)):
#                 for y in range(block_size * j, block_size * (j + 1)):
#                     magic_sum += (image[y, x]) * np.cos((2 * x + 1) * u * np.pi / 16) * np.cos((2 * y + 1) * v * np.pi / 16)
#             image[v, u] = (1 / 4) * alpha(u) * alpha(v) * magic_sum
# print(block_list)  
# ... or any other NumPy array!
# plt.imshow(image, cmap='gray')
# plt.show()