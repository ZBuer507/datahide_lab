#import jpeg2
from skimage import data, io

img = io.imread("example-256-256.bmp")
print(img[:,:,0].shape)

# jpg = jpeg2.jpeg(data.coins())