# edited by zjt
from bmp_stegano import bmp_stegano
from skimage import data, io
import sys
sys.path.append("D:\计算机\WORKS\信息隐藏技术\datahide_lab")
from rs_analysis import *

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

stegano = bmp_stegano(img, data_byte)
rs = rs_analysis(img)
rs.rs_analysis(stegano)
