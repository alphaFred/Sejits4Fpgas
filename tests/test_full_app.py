import context
import logging

from skimage import data

from tests.utils.basic_blocks import *
from pkg_resources import resource_filename

from sejits4fpgas.src.dsl import DSLTransformer
from sejits4fpgas.src.dsl import get_dsl_type
from sejits4fpgas.src.dsl import gen_dsl_wrapper
from sejits4fpgas.src.config import config
from sejits4fpgas.src.nodes import VhdlFile
from sejits4fpgas.src.nodes import VhdlProject
from sejits4fpgas.src.utils import get_basic_blocks
from sejits4fpgas.src.transformations import VhdlBaseTransformer
from sejits4fpgas.src.jit_synth import VhdlLazySpecializedFunction
from sejits4fpgas.src.vhdl_ctree.jit import ConcreteSpecializedFunction
from sejits4fpgas.src.vhdl_ctree.transformations import PyBasicConversions

#
logging.basicConfig(filename=resource_filename("sejits4fpgas",
                                               config.get("Paths", "logging_path") + "test_full_app.log"),
                    level=logging.INFO)
#


def specialize(func):
    # generated lazy specialized function
    return TestLazyTranslator.from_function(func)


class TestLazyTranslator(VhdlLazySpecializedFunction):

    def args_to_subconfig(selfself, args):
        return {'arg_type': get_dsl_type(args, 32)}

    def transform(self, tree, program_config):
        tree = DSLTransformer(backend="VHDL").visit(tree)
        tree = PyBasicConversions().visit(tree)
        l_funcs = DSLTransformer.lifted_functions()
        tree = VhdlBaseTransformer(program_config.args_subconfig['arg_type'], l_funcs).visit(tree)
        accel_file = VhdlFile("generated", body=[tree])
        # Generate wrapper file
        wrapper_file = gen_dsl_wrapper(program_config.args_subconfig['arg_type'],
                                       axi_stream_width=32,
                                       file2wrap=accel_file)
        # Add pregenerated vhdl files
        prebuilt_files = get_basic_blocks()
        #
        return [wrapper_file, accel_file] + prebuilt_files

    def finalize(selfself, transform_result, program_config):
        proj = VhdlProject(transform_result, gen_wrapper=False)
        return TestFunction("apply", proj, None)


class TestFunction(ConcreteSpecializedFunction):
    def __init__(self, entry_name, project_node, entry_typesig):
        self._ll_function = self._compile(entry_name, project_node, entry_typesig)

    def __call__(self, *args, **kwargs):
        return self._ll_function(*args, **kwargs)


def bb_convolve(mask, divisor, width, height, img):
    k = np.array([[mask[0],mask[1],mask[2]],[mask[3],mask[4],mask[5]],[mask[6],mask[7],mask[8]]])
    k = k.astype(np.float)
    k = k/divisor
    return ndimage.convolve(img, k, mode='constant', cval=0.0)

test_img = []


def test_bb_add():
    @specialize
    def test_func(a):
        return bb_add(a, 10)

    img = data.camera()
    test_func(img)


def test_bb_sub():
    @specialize
    def test_func(a):
        return bb_sub(a, 10)

    img = data.camera()
    test_func(img)

def test_bb_mul():
    @specialize
    def test_func(a):
        return bb_mul(a, 2)

    img = data.camera()
    test_func(img)


def test_bb_limitTo():
    @specialize
    def test_func(a):
        return bb_limitTo(42, a)

    img = data.camera()
    test_func(img)

"""
def test_func(a):
    return bb_convolve((1, 2, 1, 2, 4, 2, 1, 2, 1), 16, 512, 512, a)

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
# @specialize
# def test_func(img):
#     a = bb_convolve((0, 0, 0, 0, 1, 0, 0, 0, 0), 1, 640, 480, img)
#     b = bb_sub(img, a)
#     c = bb_convolve((0, 0, 0, 0, 1, 0, 0, 0, 0), 1, 640, 480, b)
#     return bb_add(img, c)

# @specialize
# def test_func(img):
#     return bb_convolve((1, 2, 1, 2, 4, 2, 1, 2, 1), 16, 640, 480, bb_mul(img, 2))

# @specialize
# def test_func(img):
#     a = bb_sub(255, img)
#     return bb_add(img, a)

"""