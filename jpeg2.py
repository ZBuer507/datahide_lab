import numpy as np

class jpeg:
    
    block_size = None
    
    alpha = None
    A = None
    Q = None
    zig = None

    image = None
    origin_height = None
    origin_width = None


    height = None
    width = None
    block_line_count = None
    block_per_line = None
    block_count = None

    dct_image = None

    def __init__(self, img):
        self.const()
        self.image = img
        
        self.padding()
        
        self.block_line_count = self.height // self.block_size
        self.block_per_line = self.width // self.block_size
        self.block_count = self.block_line_count * self.block_per_line

        self.dct()
        self.quantization()
        

    def const(self):
        self.block_size = 8

        self.A = np.zeros((self.block_size, self.block_size))
        for i in range(self.block_size):
            for j in range(self.block_size):
                self.A[i, j] = np.cos((2 * i + 1) * j * np.pi / 16)

        self.alpha = np.ones((self.block_size, self.block_size), dtype=float)
        self.alpha[0] = 2**-0.5
        self.alpha[:,0] = 2**-0.5
        self.alpha[0, 0] = 0.5

        self.Q =[[16,11,10,16,24,40,51,61],
            [12,12,14,19,26,58,60,55],
            [14,13,16,24,40,57,69,56],
            [14,17,22,29,51,87,80,62],
            [18,22,37,56,68,109,103,77],
            [24,35,55,64,81,104,113,92],
            [49,64,78,87,103,121,120,101],
            [72,92,95,98,112,100,103,99]]

        self.zig = []
        sum = 0
        while sum <= 2 * (self.block_size - 1):
            rg = min(sum, self.block_size - 1)
            if sum % 2 == 0:
                for i in range(sum - rg, rg + 1):
                    self.zig.append((sum - i, i))
            else:
                for i in range(sum - rg, rg + 1):
                    self.zig.append((i, sum - i))
            sum += 1

    def padding(self):
        self.origin_height = self.image.shape[0]
        self.origin_width = self.image.shape[1]
        if self.origin_height % self.block_size != 0:
            self.image = np.vstack(
                (self.image, self.image[0 : self.block_size - self.origin_height % self.block_size, :])
                )
        if self.origin_width % self.block_size != 0:
            self.image = np.hstack(
                (self.image, self.image[:, 0 : self.block_size - self.origin_width % self.block_size])
                )
        self.height = self.image.shape[0]
        self.width = self.image.shape[1]

    def block(self, num):
        top = num // self.block_per_line * self.block_size
        left = num % self.block_per_line * self.block_size
        return top, left

    def dct(self):
        self.dct_image = np.zeros((self.height, self.width))
        for i in range(self.block_count):
            top, left = self.block(i)
            self.dct_image[top:top+self.block_size, left:left+self.block_size] = self.alpha * (self.A.T @ (self.image[top:top+self.block_size, left:left+self.block_size] - 128) @ self.A) / 4

    def quantization(self):
        self.dct_image_after_quantization = np.zeros((self.height, self.width), dtype = int)
        for i in range(self.block_count):
            top, left = self.block(i)
            self.dct_image_after_quantization[top:top+self.block_size, left:left+self.block_size] = np.round(self.dct_image[top:top+self.block_size, left:left+self.block_size] / self.Q)