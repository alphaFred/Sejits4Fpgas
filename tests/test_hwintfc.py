import context
import ctypes as c
import numpy as np
import numpy.ctypeslib as ctl

from pkg_resources import resource_filename
from sejits4fpgas.src.config import config


def hw_intfc():
    hw_intfc_filepath = "/home/linaro/libHwIntfc.so" 
    #

    libHwIntfc = c.cdll.LoadLibrary(hw_intfc_filepath)
    libHwIntfc.process_single.argtypes = [ctl.ndpointer(np.uint8, ndim=1, flags='C'), c.c_uint]

    return libHwIntfc.process_single

def send_data(hw_intfc, data):
    hw_intfc(data, np.uint(len(data)))
    return data

if __name__ == "__main__":
    hw_intfc = hw_intfc()
    #
    res = send_data(hw_intfc, np.array([1, 2, 3, 4], dtype=np.uint8))
    #
    print(res)
