#edited by mqa and zjt
import numpy as np
import matplotlib.pyplot as plt
import random
import sys
sys.path.append("D:\计算机\WORKS\信息隐藏技术\datahide_lab")
from bmp_stegano import *

class rs_analysis:
    block_size = None
    zig = None

    origin_image = None
    origin_height = None
    origin_width = None

    level = None
    height = None
    width = None

    image = None

    block_line_per_level = None
    block_per_line = None
    block_per_level = None
    block_count = None

    zigzag_data = None
    correlation_data = None

    rm = None
    sm = None
    r_m = None
    s_m = None

    #edited by mqa
    def __init__(self, img):
        self.const()
        self.origin_image = np.array(img, dtype=int)
        self.padding()
        self.block_line_per_level = self.height // self.block_size
        self.block_per_line = self.width // self.block_size
        self.block_per_level = self.block_line_per_level * self.block_per_line
        self.block_count = self.block_per_level * self.level
        self.zigzag()
        self.f()
        self.statistics()
    
    #edited by mqa
    def const(self):
        self.block_size = 8

        self.zig = []
        for sum in range(2 * (self.block_size - 1) + 1):
            rg = min(sum, self.block_size - 1)
            if sum % 2 == 0:
                for i in range(sum - rg, rg + 1):
                    self.zig.append((sum - i, i))
            else:
                for i in range(sum - rg, rg + 1):
                    self.zig.append((i, sum - i))
    
    #edited by mqa
    def padding(self):
        self.origin_height = self.origin_image.shape[0]
        self.origin_width = self.origin_image.shape[1]
        if len(self.origin_image.shape) == 2:
            self.level = 1
        else:
            self.level = self.origin_image.shape[2]
        
        if self.level == 1:
            self.image = np.expand_dims(self.origin_image, axis=2)
        else:
            self.image = np.array(self.origin_image, dtype=int)

        if self.origin_height % self.block_size != 0:
            self.image = np.concatenate(
                (self.image, self.image[0 : self.block_size - self.origin_height % self.block_size, :]), axis=0
                )
        if self.origin_width % self.block_size != 0:
            self.image = np.concatenate(
                (self.image, self.image[:, 0 : self.block_size - self.origin_width % self.block_size]), axis=1
                )
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]
    
    #edited by mqa
    def block(self, num):
        lev = num // self.block_per_level
        top = ((num % self.block_per_level) // self.block_per_line) * self.block_size
        left = ((num % self.block_per_level) % self.block_per_line) * self.block_size
        return lev, top, left

    #edited by mqa
    def zigzag(self):
        self.zigzag_data = {'pre':[[self.image[self.zig[j][0] + self.block(i)[1], self.zig[j][1] + self.block(i)[2], self.block(i)[0]] for j in range(self.block_size * self.block_size)] for i in range(self.block_count)]}
        self.zigzag_data['pos'] = [[block[i] + ((-1) ** (block[i] % 2)) * random.randint(0, 1) for i in range(len(block))] for block in self.zigzag_data['pre']]
        self.zigzag_data['neg'] = [[block[i] - ((-1) ** (block[i] % 2)) * random.randint(0, 1) for i in range(len(block))] for block in self.zigzag_data['pre']]

    #edited by mqa
    def f(self):
        def cal(lst):
            tmp = 0
            for i in range(1, len(lst)):
                tmp += np.abs(lst[i] - lst[i - 1])
            return tmp 
        
        tp = ('pre', 'pos', 'neg')
        self.correlation_data = {key:[cal(block) for block in self.zigzag_data[key]] for key in tp}

    #edited by mqa
    def statistics(self):
        self.rm = 0
        self.sm = 0
        for i in range(len(self.correlation_data['pos'])):
            self.rm += int(self.correlation_data['pos'][i] > self.correlation_data['pre'][i])
            self.sm += int(self.correlation_data['pos'][i] < self.correlation_data['pre'][i])
        
        self.r_m = 0
        self.s_m = 0
        for i in range(len(self.correlation_data['neg'])):
            self.r_m += int(self.correlation_data['neg'][i] > self.correlation_data['pre'][i])
            self.s_m += int(self.correlation_data['neg'][i] < self.correlation_data['pre'][i])

    #edited by mqa and zjt
    def rs_analysis(self, stegano):
        x = []
        rm_p = []
        sm_p = []
        r_m_p = []
        s_m_p = []
        result = []
        x.append(0)
        rm_p.append(self.rm / self.block_count)
        sm_p.append(self.sm / self.block_count)
        r_m_p.append(self.r_m / self.block_count)
        s_m_p.append(self.s_m / self.block_count)
        print("0%", self.block_count, self.rm / self.block_count, self.sm / self.block_count, self.r_m / self.block_count, self.s_m / self.block_count)
        result.append("{} {} {} {} {} {}\n".format(0 , self.block_count, self.rm / self.block_count, self.sm / self.block_count, self.r_m / self.block_count, self.s_m / self.block_count))

        for i in range(1, 101, 3):
            index, perc = stegano.lsb_stegano(i)
            img2 = io.imread('lsb_data/lsb_perc{}.bmp'.format(perc))
            stegano.extract_info(img2, index, perc)
            rs = rs_analysis(img2)
            x.append(i)
            rm_p.append(rs.rm / rs.block_count)
            sm_p.append(rs.sm / rs.block_count)
            r_m_p.append(rs.r_m / rs.block_count)
            s_m_p.append(rs.s_m / rs.block_count)
            print("{}%".format(i), self.block_count, rs.rm / rs.block_count, rs.sm / rs.block_count, rs.r_m / rs.block_count, rs.s_m / rs.block_count)
            result.append("{} {} {} {} {} {}\n".format(i , self.block_count, self.rm / self.block_count, self.sm / self.block_count, self.r_m / self.block_count, self.s_m / self.block_count))

        with open("rs_result.txt", "w") as f:
            for line in result:
                f.write(line)

        plt.figure()
        plt.plot(x, rm_p, label='R+')
        plt.plot(x, sm_p, label='S+')
        plt.plot(x, r_m_p, label='R-')
        plt.plot(x, s_m_p, label='S-')
        plt.xlabel("Steganography Rate")
        plt.legend()
        plt.savefig('rs_result.jpg')
        plt.show()
