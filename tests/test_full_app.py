import context

from skimage import data
from scipy import ndimage
import numpy as np

from sejits4fpgas.src.dsl import DSLTransformer
from sejits4fpgas.src.dsl import get_dsl_type
from sejits4fpgas.src.dsl import gen_dsl_wrapper
from sejits4fpgas.src.nodes import VhdlFile
from sejits4fpgas.src.nodes import VhdlProject
from sejits4fpgas.src.utils import get_basic_blocks
from sejits4fpgas.src.transformations import VhdlBaseTransformer
from sejits4fpgas.src.jit_synth import VhdlLazySpecializedFunction
from sejits4fpgas.src.vhdl_ctree.jit import ConcreteSpecializedFunction
from sejits4fpgas.src.vhdl_ctree.transformations import PyBasicConversions



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

