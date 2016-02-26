""" Example of Ctree Specializer/Transformer and Visitor. """

import logging

from skimage.filters import sobel, sobel_h, sobel_v
import sejits_ctree
import sejits_ctree.frontend

#
import ctypes
import numpy as np

import sejits_ctree.vhdl
from skimage.data import camera
#
from sejits_ctree.vhdl.nodes import Signal, VhdlProject
from sejits_ctree.vhdl.transformations import VhdlTransformer
from sejits_ctree.vhdl.transformations import VhdlKeywordTransformer

from sejits_ctree.vhdl.jit_synth import LazySpecializedFunction
from sejits_ctree.vhdl.jit_synth import ConcreteSpecializedFunction

from sejits_ctree.vhdl.nodes import VhdlType
from sejits_ctree.vhdl.basic_blocks import convolve

def fib(n):
    a = n * n
    b = a + 5
    return (n * 2) + (1/a)

def sejits_test(img):
    """ return sobel filtered image. """
    MASK = (1, 2, 1, 0, 0, 0, -1, -2, -1)
    DIV = 4
    WIDTH = 8
    #
    a = 5
    b = 1
    #
    ret = (a * convolve(img, MASK, DIV, WIDTH)) + b
    #
    return ret

"""
    HSOBEL_WEIGHTS = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
    out = np.sqrt(convolve(img, HSOBEL_WEIGHTS) ** 2 + filter_sobel_v(img) ** 2)
    out2 = out / np.sqrt(out)
    return out2
"""


# =========================================================================== #
# LAZY / CONCRETE SPECIALIZED FUNCTION
# =========================================================================== #

class BasicVhdlTrans(LazySpecializedFunction):

    def args_to_subconfig(self, args):
        arg = args[0]
        arg_type = np.ctypeslib.ndpointer(arg.dtype, arg.ndim, arg.shape)
        return {'arg_type': arg_type}

    def transform(self, tree, program_config):
        # TODO: convert arg_type to vhdl_type (OPTIONALLY)
        # arg_type = program_config.args_subconfig['arg_type']
        img_type = Signal(name="img",
                          vhdl_type=VhdlType.VhdlStdLogicVector(size=8,
                                                                default="0"))

        libraries = ["work.the_filter_package.all"]
        name_dict = {"img": img_type}

        #
        sejits_ctree.browser_show_ast(tree, file_name="basic_ast.png")
        tree = VhdlKeywordTransformer().visit(tree)
        tree = VhdlTransformer(name_dict, libs=libraries).visit(tree)
        #
        sejits_ctree.browser_show_ast(tree, file_name="trans_ast.png")
        #
        return [tree]

    def finalize(self, transform_result, program_config):
        proj = VhdlProject(files=transform_result,
                           synthesis_dir="./")
        #
        arg_config, tuner_config = program_config
        arg_type = arg_config['arg_type']
        entry_type = ctypes.CFUNCTYPE(arg_type._dtype_.type, arg_type)
        #
        return BasicFunction("dummy_func", proj, entry_type)


class BasicFunction(ConcreteSpecializedFunction):
    def __init__(self, entry_name, project_node, entry_typesig):
        self.module = project_node.codegen(indent=4)
        self.jit_callable = self.module.get_callable("bla", None)
        # self.module.cleanup()

    def __call__(self, *args, **kwargs):
        return self.jit_callable()

# =========================================================================== #
#
# =========================================================================== #


def main():
    """
    # get raw ast of test function
    raw_ast = sejits_ctree.frontend.get_ast(sejits_test)

    sejits_ctree.browser_show_ast(raw_ast, file_name="basic_ast.png")

    name_dict = {"img": Signal(name="img", vhdl_type="nd_array")}

    # generate Vhdl Basic Transformer
    vhdl_transformer = VhdlTransformer(name_dict)

    # Tranform python source code
    master_file = vhdl_transformer.visit(raw_ast)
    sejits_ctree.browser_show_ast(master_file, file_name="trans_ast.png")
    # Collect all generated Vhdl files
    vhdl_files = [master_file] + vhdl_transformer.vhdl_files

    # Generate Vhdl Project
    vhdlproject = VhdlProject(vhdl_files, "./")
    vhdlproject.codegen(indent=1)

    """
    vhdl_trans = BasicVhdlTrans.from_function(sejits_test)
    img = camera()
    vhdl_trans(img)


if __name__ == "__main__":
    main()
