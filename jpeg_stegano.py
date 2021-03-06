# edited by zjt
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
    process = None
    zig_data = None
    data = None
    zig_data_ste = None
    length = 0

    def __init__(self, zig_data, data, process):
        self.zig_data = zig_data
        self.data = data
        self.process = process
        self.f3_stegano()

    def compress_pic(self):
        sequence = tuple([tuple(line) for line in self.zig_data_ste])
        codec = HuffmanCodec.from_data(sequence)
        encoded = codec.encode(sequence)
        return codec, encoded

    def compress_pic_before(self):
        sequence = tuple([tuple(line) for line in self.zig_data])
        codec = HuffmanCodec.from_data(sequence)
        encoded = codec.encode(sequence)
        return codec, encoded

    def stegano_compress(self):
        codec, encoded = self.compress_pic()
        return codec, encoded

    def decompress_reverse(self, codec, encoded, secret_shape):
        decoded_blocks = self.decompress_pic(codec, encoded)
        self.extract_info(decoded_blocks, secret_shape)
        self.reverse_process(decoded_blocks)

    def f3_stegano(self):
        self.zig_data_ste = []
        flag = False
        pos_data = 0
        for item in self.zig_data:
            pos_zig = 0
            block = copy.deepcopy(item)
            while pos_zig < 64 and pos_data < len(self.data) and not flag:
                if self.data[pos_data] == 1:
                    if block[pos_zig] == 0:
                        pass
                    elif block[pos_zig] % 2 == 1:
                        pos_data += 1
                    else:
                        block[pos_zig] = (abs(block[pos_zig]) - 1) * (abs(block[pos_zig]) // block[pos_zig])
                        pos_data += 1
                else:
                    if block[pos_zig] == 0:
                        pass
                    elif block[pos_zig] == 1 or block[pos_zig] == -1:
                        block[pos_zig] = 0
                    elif block[pos_zig] % 2 == 0:
                        pos_data += 1
                    else:
                        block[pos_zig] = (abs(block[pos_zig]) - 1) * (abs(block[pos_zig]) // block[pos_zig])
                        pos_data += 1
                pos_zig += 1
            self.zig_data_ste.append(block)
            if pos_data == len(self.data) and not flag:
                flag = True
        self.length = pos_data
        print(self.length)

    def extract_info(self, decoded_blocks, secret_shape):
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
                        Image.fromarray(img_arr).save('f3_data/extract_img.jpg')
                        return

    def process_after(self, secret_shape):
        codec, encoded = self.compress_pic()
        stegano_blocks = codec.decode(encoded)
        self.extract_info(stegano_blocks, secret_shape)
        zig_data = [list(line) for line in stegano_blocks]
        dzz_data = self.process.dezigzag(zig_data)
        dequantization_data = self.process.dequantization(dzz_data)
        idct_data = self.process.idct(dequantization_data)
        stack_arr = []
        for i in range(self.process.width):
            stack_arr += [[None]*self.process.height]
        i = 0
        for item in idct_data:
            j = 0
            x = (i%self.process.block_per_line)*8
            y = (i//self.process.block_per_line)*8
            while j <= 63:
                stack_arr[y + j%8][x + j//8] = item[j%8][j//8]
                j += 1
            i += 1
        Image.fromarray(np.array([np.array(line) for line in stack_arr], dtype=np.uint8)).save('f3_data/after.bmp')

    def process_before(self):
        codec, encoded = self.compress_pic_before()
        decoded = codec.decode(encoded)
        stegano_blocks = [line for line in decoded]
        zig_data = [list(line) for line in stegano_blocks]
        dzz_data = self.process.dezigzag(zig_data)
        dequantization_data = self.process.dequantization(dzz_data)
        idct_data = self.process.idct(dequantization_data)
        stack_arr = []
        for i in range(self.process.width):
            stack_arr += [[None]*self.process.height]
        i = 0
        for item in idct_data:
            j = 0
            x = (i%self.process.block_per_line)*8
            y = (i//self.process.block_per_line)*8
            while j <= 63:
                stack_arr[y + j%8][x + j//8] = item[j%8][j//8]
                j += 1
            i += 1
        Image.fromarray(np.array([np.array(line) for line in stack_arr], dtype=np.uint8)).save('f3_data/before.bmp')

    def display_result(self, original_path, stegano_path, secret_path, extract_path):
        plt.subplot(2,2,1)
        plt.imshow(cv2.cvtColor(cv2.imread(original_path), cv2.COLOR_BGR2RGB))
        plt.title('before')
        plt.axis('off')
        
        plt.subplot(2, 2, 2)
        plt.imshow(cv2.cvtColor(cv2.imread(stegano_path), cv2.COLOR_BGR2RGB))
        plt.title('after')
        plt.axis('off')
        
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
