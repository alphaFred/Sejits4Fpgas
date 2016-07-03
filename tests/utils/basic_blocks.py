def bb_convolve(mask, divisor, width, height, img):
    return img * 2

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