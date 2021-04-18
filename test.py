from skimage import data, io
import sys
sys.path.append("D:\计算机\WORKS\信息隐藏技术\datahide_lab")
from jpeg24depth import *
from jpeg_stegano import *

secret_shape = (10, 10)
Image.open('example-256-256.bmp').convert('L').resize(secret_shape, Image.ANTIALIAS).save('secret_grey.jpg')
img = io.imread("lena512.bmp")
img2 = io.imread("secret_grey.jpg")
process = jpeg_24bit_depth(img)
data = []
data0 = img2.flatten()
for num in data0:
    l = []
    n = num
    for i in range(0, 8):
        l.append(n%2)
        n = int(n/2)
    l.reverse()
    data += l
stegano = jpeg_stegano(process.zig_data, data)

codec, encoded = stegano.stegano_compress()
stegano.decompress_reverse(codec, encoded, secret_shape)
stegano.display_result('lena512.bmp', 'reversed_img.jpg', 'secret_grey.jpg', 'extract_img.jpg')