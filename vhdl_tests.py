"""Test Module for vhdl-sejits."""
import os
import ctypes
import logging
import glob
import traceback

from skimage import data
from scipy import ndimage
import numpy as np

from src.vhdl_ctree.types import get_ctype
from src.vhdl_ctree.nodes import Project
from src.vhdl_ctree.c.nodes import FunctionDecl, CFile
from src.vhdl_ctree.transformations import PyBasicConversions
from src.vhdl_ctree.jit import LazySpecializedFunction
from src.vhdl_ctree.jit import ConcreteSpecializedFunction
from src.jit_synth import VhdlLazySpecializedFunction

from src.transformations import VhdlIRTransformer, VhdlBaseTransformer
from src.dsl import DSLTransformer
from src.nodes import VhdlFile, VhdlProject
from src.dsl import get_dsl_type, gen_dsl_wrapper
from src import TransformationError

#
logging.basicConfig(level=10)
#

VHDL = True
img_path = os.path.dirname(__file__) + "/images/"

orig_tree = "origin_tree.png"
pre_dsl_trans_tree = "pre-dsl-transform_tree.png"
post_dsl_trans_tree = "post-dsl-transform_tree.png"
pretrans_tree = "pre-transform_tree.png"
posttrans_tree = "post-transform_tree.png"


class BasicTranslator(VhdlLazySpecializedFunction):

    def args_to_subconfig(self, args):
        if not VHDL:
            if len(args) > 1:
                return {'arg_type': [type(get_ctype(arg)) for arg in args]}
            elif len(args) == 1:
                return {'arg_type': type(get_ctype(args[0]))}
            else:
                raise IOError()
        else:
            return {'arg_type': get_dsl_type(args, 32)}

    def transform(self, tree, program_config):
        if not VHDL:
            tree = DSLTransformer(backend="C").visit(tree)
            tree = PyBasicConversions().visit(tree)
            #
            fib_fn = tree.find(FunctionDecl, name="apply")
            arg_type = program_config.args_subconfig['arg_type']
            fib_fn.return_type = arg_type()
            fib_fn.params[0].type = arg_type()

            lifted_functions = DSLTransformer.lifted_functions()
            c_translator = CFile("generated", [lifted_functions, tree])
            return [c_translator]
        else:
            tree = DSLTransformer(backend="VHDL").visit(tree)
            tree = PyBasicConversions().visit(tree)
            l_funcs = DSLTransformer.lifted_functions()
            tree = VhdlBaseTransformer(program_config.args_subconfig['arg_type'], l_funcs).visit(tree)
            # Generate accelerator file
            accel_file = VhdlFile("generated", body=[tree])

            # Generate wrapper file
            wrapper_file = gen_dsl_wrapper(program_config.args_subconfig['arg_type'],
                                           axi_stream_width=32,
                                           file2wrap=accel_file)

            # Add pregenerated vhdl files
            hw_file_path = os.path.dirname(__file__) + "/src/hw/"
            prebuilt_files = []
            for fn in glob.glob(hw_file_path + "*"):
                fname = os.path.basename(os.path.splitext(fn)[0])
                prebuilt_files.append(VhdlFile.from_prebuilt(name=fname, path=fn))
            #
            return [wrapper_file, accel_file] + prebuilt_files

    def finalize(self, transform_result, program_config):
        if not VHDL:
            proj = Project(transform_result)

            arg_config, tuner_config = program_config
            arg_type = arg_config['arg_type']
            entry_type = ctypes.CFUNCTYPE(arg_type, arg_type)

            return BasicFunction("apply", proj, entry_type)
        else:
            proj = VhdlProject(transform_result, gen_wrapper=False)
            return BasicFunction("apply", proj, None)


class BasicFunction(ConcreteSpecializedFunction):
    def __init__(self, entry_name, project_node, entry_typesig):
        self._ll_function = self._compile(entry_name, project_node, entry_typesig)

    def __call__(self, *args, **kwargs):
        return self._ll_function(*args, **kwargs)


def specialize(func):
    # generated lazy specialized function
    return BasicTranslator.from_function(func)

import time


def bb_convolve(mask, divisor, width, height, img):
    k = np.array([[mask[0],mask[1],mask[2]],[mask[3],mask[4],mask[5]],[mask[6],mask[7],mask[8]]])
    k = k.astype(np.float)
    k = k/divisor
    st = time.time()
    res = ndimage.convolve(img, k, mode='constant', cval=0.0)
    et = time.time()
    print "took {}sec".format(et-st)
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

# def test_func(a):
#     filtMASK_Gauss = (1, 2, 1, 2, 4, 2, 1, 2, 1)  # Gauss
#     # filtMASK_Sobel_y = (-1, 0, 1, -2, 0, 2, -1, 0, 1)  # Sobel_y
#     #
#     c = 255 - a
#     #
#     return bb_convolve(filtMASK_Gauss, 16, 315, 300, 8, 8, bb_convolve(filtMASK_Gauss, 16, 315, 300, 8, 8, c))

# def test_func(img):
#     filtMASK_Gauss = (1, 2, 1, 2, 4, 2, 1, 2, 1)  # Gauss
#     # filtMASK_Sobel_y = (-1, 0, 1, -2, 0, 2, -1, 0, 1)  # Sobel_y
#     #
#     r = bb_split(img, 0)
#     g = bb_split(img, 1)
#     b = bb_split(img, 2)
#     #
#     p_r = bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, r))
#     p_g = bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, g))
#     p_b = bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, b))
#     #
#     p_img = bb_merge(p_r, p_g, p_b)
#     return p_img

# def test_func(img):
#     filtMASK_Gauss = (1, 2, 1, 2, 4, 2, 1, 2, 1)  # Gauss
#     # filtMASK_Sobel_y = (-1, 0, 1, -2, 0, 2, -1, 0, 1)  # Sobel_y
#     #
#     a = img * 12
#     return bb_convolve(filtMASK_Gauss, 16, 640, 480, 8, 8, a)

# from skimage import io
@specialize
def test_func(img):
    a = bb_convolve((-1, 0, 1, -2, 0, 2, -1, 0, 1), 16, 640, 480, img)
    b = bb_sub(img, a)
    c = bb_convolve((1, 2, 1, 2, 4, 2, 1, 2, 1), 16, 640, 480, b)
    return bb_add(img, c)

# @specialize
# def test_func(img):
#     return bb_add(img, 3)

# @specialize
# def test_func(img):
#     a = bb_add(img, 3)
#     return bb_add(img, a)


# transformed_func = BasicTranslator.from_function(test_func)

image = data.camera()

# print image, image.shape

# res = test_func(image)

# print res

# io.imshow(res)
# io.show()

print test_func(image)
print test_func(image)
print test_func(image)
