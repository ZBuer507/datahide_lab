import cv2
import numpy as np
from PIL import Image
from dahuffman import HuffmanCodec
from matplotlib import pyplot as plt
import copy
import sys
sys.path.append("D:\计算机\WORKS\信息隐藏技术\datahide_lab")
from jpeg24depth import *

SHOW = True

class jpeg_stegano:
    zig_data = None
    data = None
    zig_data_ste = None
    length = 0

    def __init__(self, zig_data, data):
        self.zig_data = zig_data
        self.data = data
        self.f3_stegano()

    def f3_stegano(self):
        self.zig_data_ste = []
        flag = False
        pos_data = 0
        for item in self.zig_data:
            pos_zig = 0
            block = copy.deepcopy(item)
            while pos_zig < 64 and pos_data < len(self.data) and not flag:
                if self.data[pos_data] == 1 or self.data[pos_data] == -1:
                    if block[pos_zig] == 0:
                        pass
                    elif block[pos_zig] % 2 == 1:
                        pos_data += 1
                    else:
                        block[pos_zig] = int((abs(block[pos_zig]) - 1) * (abs(block[pos_zig]) / block[pos_zig]))
                        pos_data += 1
                else:
                    if block[pos_zig] == 0:
                        pass
                    elif block[pos_zig] == 1 or block[pos_zig] == -1:
                        block[pos_zig] = 0
                    elif block[pos_zig] % 2 == 0:
                        pos_data += 1
                    else:
                        block[pos_zig] = int((abs(block[pos_zig]) - 1) * (abs(block[pos_zig]) / block[pos_zig]))
                        pos_data += 1
                pos_zig += 1
            self.zig_data_ste.append(block)
            if pos_data == len(self.data) and not flag:
                flag = True
        self.length = pos_data
        #print(pos_data)

    def compress_pic(self):
        sequence = tuple([tuple(line) for line in self.zig_data_ste])
        codec = HuffmanCodec.from_data(sequence)
        encoded = codec.encode(sequence)
        return codec, encoded

    def decompress_pic(self, codec, compress_pic):
        decoded = codec.decode(compress_pic)
        decoded_blocks = [line for line in decoded]
        return decoded_blocks

    def extrct_info(self, decoded_blocks, secret_shape):
        bin_seq = []
        for i in range(len(decoded_blocks)):
            block = decoded_blocks[i]
            length = len(block)
            for m in range(length):
                if block[m]:
                    bin_seq.append(str(abs(block[m])%2))
                    if len(bin_seq) == self.length:
                        bin_seq = np.split(np.array(bin_seq), len(bin_seq)//8)
                        img_arr = np.array([int(''.join(item), 2) for item in bin_seq], dtype=np.uint8).reshape(secret_shape)
                        Image.fromarray(img_arr).save('extract_img.jpg')
                        return

    def stegano_compress(self):
        codec, encoded = self.compress_pic()
        # print('size of compressed pic is %.2fkB' % (len(encoded) / 1024))
        return codec, encoded

    def decompress_reverse(self, codec, encoded, secret_shape):
        decoded_blocks = self.decompress_pic(codec, encoded)
        self.extrct_info(decoded_blocks, secret_shape)
        self.reverse_process(decoded_blocks)

    def reverse_process(self, stegano_blocks):
        iquant_blocks = [np.array(line).reshape([8,8]) * np.array([np.array(l) for l in jpeg_24bit_depth.Qy]) for line in stegano_blocks]
        idct_blocks = []
        stack_arr = []
        #Image.fromarray(stack_arr).save('reversed_img.jpg')

    def display_result(self, original_path, stegano_path, secret_path, extract_path):
        plt.subplot(2,2,1)
        plt.imshow(cv2.cvtColor(cv2.imread(original_path), cv2.COLOR_BGR2RGB))
        plt.title('original')
        plt.axis('off')
        '''
        plt.subplot(2, 2, 2)
        plt.imshow(cv2.cvtColor(cv2.imread(stegano_path), cv2.COLOR_BGR2RGB))
        plt.title('stegano')
        plt.axis('off')
        '''
        plt.subplot(2, 2, 3)
        plt.imshow(cv2.cvtColor(cv2.imread(secret_path), cv2.COLOR_BGR2RGB))
        plt.title('secret')
        plt.axis('off')

        plt.subplot(2, 2, 4)
        plt.imshow(cv2.cvtColor(cv2.imread(extract_path), cv2.COLOR_BGR2RGB))
        plt.title('extracted')
        plt.axis('off')

        plt.savefig('compare_result.jpg')
        if SHOW: plt.show()
