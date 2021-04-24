# edited by zjt
from skimage import data, io
from PIL import Image
import copy
import numpy as np
import sys
sys.path.append("D:\计算机\WORKS\信息隐藏技术\datahide_lab")

class bmp_stegano:
    img = None
    data = None
    length = None
    x = None
    y = None

    def __init__(self, img, data):
        self.img = img
        self.length = len(img) * len(img[0])
        self.x = len(img)
        self.y = len(img[0])
        self.data = data

    def lsb_stegano(self, perc):
        index = self.length*perc//100
        img_stegano = np.ndarray([self.x, self.y])
        flag = True
        node = 0
        l = 0
        for line in self.img:
            for i in range(0, self.x):
                if flag:
                    if line[i]%2 == 0:
                        if self.data[node] == 0: img_stegano[l][i] = line[i]
                        else: img_stegano[l][i] = line[i] + 1
                    else:
                        if self.data[node] == 0: img_stegano[l][i] = line[i] - 1
                        else: img_stegano[l][i] = line[i]
                    node += 1
                else:
                    img_stegano[l][i] = line[i]
                
                if flag and node == index:
                    flag = False
            l += 1
        img_stegano.reshape([self.x, self.y])
        Image.fromarray(np.array(img_stegano, dtype=np.uint8)).save('lsb_data/lsb_perc{}.bmp'.format(perc))
        return index, perc

    def extract_info(self, img, index, perc):
        data = []
        #print(img[0])
        for i in range(0, index):
            data.append(img[i//self.x][i%self.x])
        b = index//8
        with open('lsb_data/lsb_perc{}_data.txt'.format(perc), "wb") as f:
            for i in range(0, b):
                tmp = data[i*8 : i*8+8]
                t = 0
                n = 7
                for j in tmp:
                    t += (j%2) * 2**n
                    n -= 1
                f.write(bytes([t]))
        