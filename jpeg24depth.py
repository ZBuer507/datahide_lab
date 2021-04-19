import numpy as np

class jpeg_24bit_depth:

    block_size = None

    alpha = None
    A = None
    Qy = [[16,11,10,16,24,40,51,61],
        [12,12,14,19,26,58,60,55],
        [14,13,16,24,40,57,69,56],
        [14,17,22,29,51,87,80,62],
        [18,22,37,56,68,109,103,77],
        [24,35,55,64,81,104,113,92],
        [49,64,78,87,103,121,120,101],
        [72,92,95,98,112,100,103,99]]
    Qc = [[17,18,24,47,99,99,99,99],
        [18,21,26,66,99,99,99,99],
        [24,26,56,99,99,99,99,99],
        [47,66,99,99,99,99,99,99],
        [99,99,99,99,99,99,99,99],
        [99,99,99,99,99,99,99,99],
        [99,99,99,99,99,99,99,99],
        [99,99,99,99,99,99,99,99]]
    zig = None

    origin_image = None
    origin_height = None
    origin_width = None

    level = None
    height = None
    width = None

    image = None # after color space trans

    block_line_per_level = None
    block_per_line = None
    block_per_level = None
    block_count = None

    dct_image = None
    dct_image_after_quantization = None
    zig_data = None

    def __init__(self, img):
        self.const()
        self.origin_image = img

        self.padding()
        self.color_space_trans()

        self.block_line_per_level = self.height // self.block_size
        self.block_per_line = self.width // self.block_size
        self.block_per_level = self.block_line_per_level * self.block_per_line
        self.block_count = self.block_per_level * self.level

        self.dct()
        self.quantization()
        self.zigzag()

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
        self.origin_height = self.origin_image.shape[0]
        self.origin_width = self.origin_image.shape[1]
        if len(self.origin_image.shape) == 2:
            self.level = 1
        else:
            self.level = self.origin_image.shape[2]
        
        if self.origin_height % self.block_size != 0:
            self.origin_image = np.concatenate(
                (self.origin_image, self.origin_image[0 : self.block_size - self.origin_height % self.block_size, :]), axis=0
                )
        if self.origin_width % self.block_size != 0:
            self.origin_image = np.concatenate(
                (self.origin_image, self.origin_image[:, 0 : self.block_size - self.origin_width % self.block_size]), axis=1
                )
        self.height = self.origin_image.shape[0]
        self.width = self.origin_image.shape[1]
    
    def color_space_trans(self):
        if self.level == 1:
            self.image = np.zeros((self.height, self.width, self.level), dtype=int)
            self.image[:,:,0] = self.origin_image
            return
        if self.level != 3:
            print('error.')
            exit(0)
        self.image = np.zeros((self.height, self.width, self.level))
        r = self.origin_image[:,:,0]
        g = self.origin_image[:,:,1]
        b = self.origin_image[:,:,2]
        self.image[:,:,0] = 0.299 * r + 0.587 * g + 0.114 * b
        self.image[:,:,1] = -0.1687 * r - 0.3313 * g + 0.5 * b
        self.image[:,:,2] = 0.5 * r - 0.4187 * g + 0.0813 * b
    
    def block(self, num):
        lev = num // self.block_per_level
        top = ((num % self.block_per_level) // self.block_per_line) * self.block_size
        left = ((num % self.block_per_level) % self.block_per_line) * self.block_size
        return lev, top, left
    
    def dct(self):
        self.dct_image = np.zeros((self.height, self.width, self.level))
        for i in range(self.block_count):
            lev, top, left = self.block(i)
            self.dct_image[top:top+self.block_size, left:left+self.block_size, lev] = self.alpha * (self.A.T @ (self.image[top:top+self.block_size, left:left+self.block_size, lev] - 128) @ self.A) / 4
        
    def quantization(self):
        self.dct_image_after_quantization = np.zeros(
            (self.height, self.width, self.level),
            dtype = int
            )
        for i in range(self.block_count):
            lev, top, left = self.block(i)
            Q = None
            if lev == 0:
                Q = self.Qy
            else:
                Q = self.Qc
            self.dct_image_after_quantization[top:top+self.block_size,
                                                left:left+self.block_size,
                                                lev] = \
            np.round(self.dct_image[top:top+self.block_size,
                                        left:left+self.block_size,
                                        lev] / Q)

    def zigzag(self):
        self.zig_data = []
        for i in range(self.block_count):
            lev, top, left = self.block(i)
            tmp = []
            #print(self.block_size)
            for j in range(self.block_size * self.block_size):
                row, col = self.zig[j]
                tmp.append(self.dct_image_after_quantization[row + top, col + left, lev])
            self.zig_data.append(tmp)

    def dezigzag(self, zig_data):
        dzz_data = []
        for item in zig_data:
            tmp = np.zeros((self.block_size, self.block_size))
            for index in range(0,len(item) - 1):
                i , j = self.zig[index]
                tmp[i, j] = item[index]
            dzz_data.append(tmp)
        return dzz_data

    def dequantization(self, dzz_data):
        dequantization_data = []
        for item in dzz_data :
            tmp = np.zeros((self.block_size, self.block_size))
            tmp = np.multiply(item , self.Qy)
            dequantization_data.append(tmp)
        return dequantization_data

    def idct(self, dequantization_data):
        idct_data = []
        for item in dequantization_data :
            tmp = np.zeros((self.block_size, self.block_size))
            tmp = np.linalg.inv((self.A.T)) @ (4 * item / self.alpha) @ np.linalg.inv(self.A) + 128
            idct_data.append(np.round(tmp))
        return idct_data