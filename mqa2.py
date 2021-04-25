import rs
import numpy as np
from skimage import data, io
import bmp_stegano
import matplotlib.pyplot as plt
import matplotlib
# image = np.array([[139,144,149,153,155,155,155,155],
#                     [144,151,153,156,159,156,156,156],
#                     [150,155,160,163,158,156,156,156],
#                     [159,161,162,160,160,159,159,159],
#                     [159,160,161,162,162,155,155,155],
#                     [161,161,161,161,160,157,157,157],
#                     [162,162,161,163,162,157,157,157],
#                     [162,162,161,161,163,158,158,158]], dtype=int)
# image = np.array([[52,55,61,66,70,61,64,73],
#                     [63,59,55,90,109,85,69,72],
#                     [62,59,68,113,144,104,66,73],
#                     [63,58,71,122,154,106,70,69],
#                     [67,61,68,104,126,88,68,70],
#                     [79,65,60,70,77,68,58,75],
#                     [85,71,64,59,55,61,65,83],
#                     [87,79,69,68,65,76,78,94]], dtype=int)
# image = np.array([[52,55,61,66,70,61,64,73],
#                     [63,59,55,90,109,85,69,72],
#                     [62,59,68,113,144,104,66,73],
#                     [63,58,71,122,154,106,70,69],
#                     [67,61,68,104,126,88,68,70],
#                     [79,65,60,70,77,68,58,75],
#                     [85,71,64,59,55,61,65,83],
#                     [87,79,69,68,65,76,78,94],
#                     [79,65,60,70,77,68,58,75]], dtype=int)
# image = io.imread('~/datahide/lab2/a.bmp')
# image = data.colorwheel()
img = io.imread("lena512.bmp")
data = None
with open("data_stegano.txt", "rb") as f:
    data = f.read()
data_byte = []
for item in data:
    n = item
    tmp = []
    for i in range(0, 8):
        tmp.append(n%2)
        n //= 2
    tmp.reverse()
    data_byte += tmp

stegano = bmp_stegano.bmp_stegano(img, data_byte)
index, perc = stegano.lsb_stegano(25)
img2 = io.imread('lsb_data/lsb_perc{}.bmp'.format(perc))
stegano.extract_info(img2, index, perc)


x = []
rm_p = []
sm_p = []
r_m_p = []
s_m_p = []
rr = rs.rs(img)
x.append(0)
rm_p.append(rr.rm / rr.block_count)
sm_p.append(rr.sm / rr.block_count)
r_m_p.append(rr.r_m / rr.block_count)
s_m_p.append(rr.s_m / rr.block_count)
print(rr.block_count, rr.rm / rr.block_count, rr.sm / rr.block_count, rr.r_m / rr.block_count, rr.s_m / rr.block_count)

for i in range(1, 30):
    index, perc = stegano.lsb_stegano(i)
    img2 = io.imread('lsb_data/lsb_perc{}.bmp'.format(perc))
    rr = rs.rs(img2)
    x.append(i)
    rm_p.append(rr.rm / rr.block_count)
    sm_p.append(rr.sm / rr.block_count)
    r_m_p.append(rr.r_m / rr.block_count)
    s_m_p.append(rr.s_m / rr.block_count)
    print(rr.block_count, rr.rm / rr.block_count, rr.sm / rr.block_count, rr.r_m / rr.block_count, rr.s_m / rr.block_count)

print(x, rm_p, sm_p, r_m_p, s_m_p)
plt.figure()
plt.plot(x, rm_p, label='R+')
plt.plot(x, sm_p, label='S+')
plt.plot(x, r_m_p, label='R-')
plt.plot(x, s_m_p, label='S-')
plt.xlabel("隐写率")
plt.legend()
plt.show()

# rr = rs.rs(img)
# # print(rr.origin_image.shape)
# # print(rr.origin_image)
# # print(rr.image.shape)
# # print(rr.image[:,:,0])
# # print(rr.zigzag_data)
# # print(rr.correlation_data)
# print(rr.block_count, rr.rm / rr.block_count, rr.sm / rr.block_count, rr.r_m / rr.block_count, rr.s_m / rr.block_count)
# rr = rs.rs(img2)
# print(rr.block_count, rr.rm / rr.block_count, rr.sm / rr.block_count, rr.r_m / rr.block_count, rr.s_m / rr.block_count)

