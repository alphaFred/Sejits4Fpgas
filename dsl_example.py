__author__ = 'philipp ebensberger'

import Image

from sejits import Specialize


# Example 1: Apply Minimum-Filter
"""
out_image = in_images.filter(MinFilter(size=5))
"""
"""
out_image = in_images.filter(MinFilter(size=3))
"""

# Example 2: Apply point operation
"""
out_image = in_images.point(lambda i: i * 2.2)
"""
"""
out_image = in_images.point(lambda i: i + 25)
"""

# Example 3: Combine filter and point operation
"""
temp1 = in_images.filter(MinFilter(size=5))
out_image = temp1.point(lambda i: i * 2.2)
"""

# DummyFilter(size=types.IntType, bla=types.FloatType, blub)

@Specialize("fpga")
def dec_kernel(in_image=Image.new("RGB", (512, 512), "white"),
               out_image=Image.new("RGB", (512, 512), "white"),
               in_arg=(3,12,4)):
    temp1 = in_image.filter(DummyFilter(in_arg[0], blub=in_arg[1], bla=3.4)).point(lambda i: i + in_arg[2])
    temp2 = temp1.filter(MinFilter(3))
    out_image = temp2
    return out_image

in_image = Image.open("./images/Lena.png")
out_image = Image.new("RGB", (512, 512), "white")

in_image2 = Image.open("./images/Lena.png")
out_image2 = Image.new("RGB", (512, 512), "white")

print "first line"
dec_kernel(in_image,out_image,25)


"""
class FIA_Example(FIA_Kernel_Core):
    def kernel(self):
        out_image = in_images.point(lambda i: i + 25)

in_image = Image.open("./images/Lena.png")
out_image = Image.new("RGB", (512, 512), "white")

# in_image.show()

fia_example = FIA_Example(in_images=[in_image], out_image=[out_image])

# available targets: python, fpga
img = fia_example.run(target="fpga")
if img is not None:
    # img.show() uses ImageMagic
    # install under ubuntu via: sudo apt-get install imagemagick --fix-missing 
    img.show()
"""
