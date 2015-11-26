""" docstring for dsl_example module. """
__author__ = 'philipp ebensberger'

import Image

from sejits import Specialize
from ImageFilter import MinFilter, MaxFilter


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
"""inspect.getmembers(sys.modules[__name__])
out_image = in_images.point(lambda i: i + 25)
"""

# Example 3: Combine filter and point operation
"""
temp1 = in_images.filter(MinFilter(size=5))
out_image = temp1.point(lambda i: i * 2.2)
"""

# DummyFilter(size=types.IntType, bla=types.FloatType, blub)

"""
    temp1 = in_image.filter(MaxFilter(size=5))

    temp2_1 = temp1.point(lambda i: i * 2.4)
    temp2_2 = temp1.point(lambda i: i + 4)
    temp2_3 = temp1.filter(MinFilter(size=3))

    temp3_1 = temp2_1.filter(MaxFilter(size=3))
    temp3_2 = temp2_2 + temp2_3

    temp4 = temp3_2 + temp1
    temp5 = (temp3_1 - temp3_2) + temp4
    out_image = temp5 + in_image
    return out_image
"""


@Specialize("fpga")
def dec_kernel(in_image=[Image.new("RGB", (512, 512), "white"),
                         Image.new("RGB", (512, 512), "white")],
               out_image=Image.new("RGB", (512, 512), "white")):
    conv_img_1 = in_image[0].filter(MinFilter(size=3))
    conv_img_2 = in_image[1].filter(MinFilter(size=3))
    tmp1 = conv_img_1.point(lambda i: i * 0.5)
    tmp2 = conv_img_2.point(lambda i: i * 0.5)
    out_image = tmp1 + tmp2
    return out_image

in_image = Image.open("./images/Lena.png")
out_image = Image.new("RGB", (512, 512), "white")

in_image2 = Image.open("./images/Lena.png")
out_image2 = Image.new("RGB", (512, 512), "white")

print "-" * 80
ret_image = dec_kernel(in_image, out_image)
ret_image.save("./images/landscape_transformed.jpg")

