import numpy as np
from scipy import ndimage


def bb_convolve(mask, divisor, width, height, img):
    k = np.array([[mask[0],mask[1],mask[2]],[mask[3],mask[4],mask[5]],[mask[6],mask[7],mask[8]]])
    k = k.astype(np.float)
    k = k/divisor
    res = ndimage.convolve(img, k, mode='constant', cval=0.0)
    return res

def bb_split(i, n):
    return n[i]


def bb_merge(n_3, n_2, n_1, n_0):
    return [n_3, n_2, n_1, n_0]


def bb_add(x, y):
    return x + y


def bb_sub(x, y):
    return x - y


def bb_mul(x, y):
    return x * y


def bb_limitTo(valid, x):
    return x
