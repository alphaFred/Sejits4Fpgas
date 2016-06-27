import os
import sys
import glob
import time
import pytest
import skimage

import numpy as np

sys.path.append("..")

from vhdl_sejits.src.vhdl_ctree.jit import LazySpecializedFunction
from vhdl_sejits.src.vhdl_ctree.jit import ConcreteSpecializedFunction
from vhdl_sejits.src.vhdl_ctree.transformations import PyBasicConversions

from vhdl_sejits.src.transformations import VhdlBaseTransformer
from vhdl_sejits.src.dsl import DSLTransformer
from vhdl_sejits.src.nodes import VhdlFile
from vhdl_sejits.src.nodes import VhdlProject
from vhdl_sejits.src.dsl import get_dsl_type
from vhdl_sejits.src.dsl import gen_dsl_wrapper
from vhdl_sejits.src.utils import TransformationError
from basic_blocks import *



class VhdlBasicTranslator(LazySpecializedFunction):

    def args_to_subconfig(self, args):
        return {'arg_type': get_dsl_type(args, 32)}

    def transform(self, tree, program_config):
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
            fname = fn.lstrip(hw_file_path).rstrip(".vhd").lower()
            prebuilt_files.append(VhdlFile.from_prebuilt(name=fname, path=fn))
        return [wrapper_file, accel_file] + prebuilt_files

    def finalize(self, transform_result, program_config):
        proj = VhdlProject(transform_result, gen_wrapper=False)
        return VhdlBasicFunction("apply", proj, None)


class VhdlBasicFunction(ConcreteSpecializedFunction):
    def __init__(self, entry_name, project_node, entry_typesig):
        self.vhdl_function = self._compile(entry_name, project_node, entry_typesig)

    def __call__(self, *args, **kwargs):
        for i in args:
            print id(i)
        return self.vhdl_function()


def test_init():
    def test_func(img):
        return img
    #
    lsf_inst = VhdlBasicTranslator.from_function(test_func)
    #
    try:
        lsf_inst(5)
    except TransformationError as e:
        assert e.msg == "All input parameter must be of type np.ndarray"
    #
    try:
        lsf_inst([5, 123, 14])
    except TransformationError as e:
        assert e.msg == "All input parameter must be of type np.ndarray"


def test_sys_0():
    def test_func(a):
        return bb_convolve((1, 2, 1, 2, 4, 2, 1, 2, 1), 16, 512, 512, a)
    #
    assert True

def test_sy_1():
    def test_func(a):
        c = bb_sub(a, 125)
        return bb_add(c, a)
    #
    st = time.time()

    et = time.time()
    #
    assert True
