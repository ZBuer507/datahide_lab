import jpeg2
from skimage import data, io

img = io.imread("a.bmp")
print(img[:,:,0].shape)

# jpg = jpeg2.jpeg(data.coins())