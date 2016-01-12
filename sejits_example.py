""" Example of Ctree Specializer/Transformer and Visitor. """

import logging

from skimage.filters import sobel

import sejits_ctree
import sejits_ctree.frontend

#
import ctypes
import numpy as np
from skimage.data import camera
#
from sejits_ctree.vhdl.nodes import Signal, VhdlProject
from sejits_ctree.vhdl.transformations import VhdlTransformer
from sejits_ctree.vhdl.transformations import UserTransformers

from sejits_ctree.vhdl.jit_synth import LazySpecializedFunction
from sejits_ctree.vhdl.jit_synth import ConcreteSpecializedFunction


log = logging.getLogger(__name__)


def filter_sobel(img):
    """ return sobel filtered image. """
    return sobel(img)


def sejits_test(img):
    """ return sobel filtered image. """
    filtered_image = filter_sobel(img)
    return filtered_image


# =========================================================================== #
# LAZY / CONCRETE SPECIALIZED FUNCTION
# =========================================================================== #

class BasicVhdlTrans(LazySpecializedFunction):

    def args_to_subconfig(self, args):
        arg = args[0]
        arg_type = np.ctypeslib.ndpointer(arg.dtype, arg.ndim, arg.shape)
        return {'arg_type': arg_type}

    def transform(self, tree, program_config):
        arg_type = program_config.args_subconfig['arg_type']
        #
        name_dict = {"img": Signal(name="img", vhdl_type="nd_array")}
        # tree = UserTransformers().visit(tree)
        #
        basic_transformer = VhdlTransformer(name_dict)
        tree = basic_transformer.visit(tree)
        trees = [tree] + basic_transformer.vhdl_files
        #
        sejits_ctree.browser_show_ast(trees[0], file_name="trans_ast.png")
        #
        return trees

    def finalize(self, transform_result, program_config):
        proj = VhdlProject(files=transform_result,
                           synthesis_dir="./")
        #
        proj.codegen(1)
        #
        arg_config, tuner_config = program_config
        arg_type = arg_config['arg_type']
        entry_type = ctypes.CFUNCTYPE(arg_type._dtype_.type, arg_type)

        return BasicFunction("dummy_func", proj, entry_type)


class BasicFunction(ConcreteSpecializedFunction):
    def __init__(self, entry_name, project_node, entry_typesig):
        pass

    def __call__(self, *args, **kwargs):
        return "bla"

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
