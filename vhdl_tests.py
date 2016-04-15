"""Test Module for vhdl-sejits."""
import os
import ctypes
import logging
import glob
#
from skimage import data
#
from ctree.types import get_ctype
from ctree.nodes import Project
from ctree.c.nodes import FunctionDecl, CFile
from ctree.transformations import PyBasicConversions
from ctree.jit import LazySpecializedFunction
#
from src.transformations import VhdlIRTransformer, VhdlBaseTransformer
from src.dsl import DSLTransformer
from src.nodes import VhdlFile, VhdlProject
from src.dsl import get_dsl_type, DSLWrapper
#
from ctree.jit import ConcreteSpecializedFunction
#
logging.basicConfig(level=40)
#

VHDL = True
img_path = os.getcwd() + "/images/"

orig_tree = "origin_tree.png"
pretrans_tree = "pre-transform_tree.png"
posttrans_tree = "post-transform_tree.png"


class BasicTranslator(LazySpecializedFunction):

    def args_to_subconfig(self, args):
        if not VHDL:
            if len(args) > 1:
                return {'arg_type': [type(get_ctype(arg)) for arg in args]}
            elif len(args) == 1:
                return {'arg_type': type(get_ctype(args[0]))}
            else:
                raise IOError()
        else:
            return {'arg_type': get_dsl_type(args)}


    def transform(self, tree, program_config):
        from ctree.visual.dot_manager import DotManager
        DotManager().dot_ast_to_file(tree, file_name=img_path + orig_tree)
        #
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
            # =================================================================
            DotManager().dot_ast_to_file(tree,
                                         file_name=img_path + pretrans_tree)
            # =================================================================
            #
            l_funcs = DSLTransformer.lifted_functions()
            tree = VhdlBaseTransformer(program_config.args_subconfig['arg_type'], l_funcs).visit(tree)
            # tree = VhdlIRTransformer(program_config.args_subconfig['arg_type'], l_funcs).visit(tree)

            # =================================================================
            DotManager().dot_ast_to_file(tree,
                                         file_name=img_path + posttrans_tree)
            # =================================================================
            accel_file = VhdlFile("generated", body=[tree])
            wrapper_file = DSLWrapper(program_config.args_subconfig['arg_type']).generate_wrapper(file2wrap=accel_file)

            # add pregenerated vhdl files
            hw_file_path = "./src/hw/"
            prebuilt_files = []
            for fn in glob.glob(hw_file_path + "*"):
                fname = fn.lstrip(hw_file_path).rstrip(".vhd").lower()
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
        if not VHDL:
            self._c_function = self._compile(entry_name, project_node, entry_typesig)
        else:
            self.vhdl_function = self._compile(entry_name, project_node, entry_typesig)

    def __call__(self, *args, **kwargs):
        if not VHDL:
            return self._c_function(*args, **kwargs)
        else:
            for i in args:
                print id(i)
            return self.vhdl_function()


def bb_convolve(n):
    return n * 2

def bb_split(n, i):
    return n[i]

def bb_merge(n_0, n_1, n_2):
    return [n_2, n_1, n_0]

# def test_func(a):
#     filtMASK_Gauss = (1, 2, 1, 2, 4, 2, 1, 2, 1)  # Gauss
#     filtMASK_Sobel_y = (-1, 0, 1, -2, 0, 2, -1, 0, 1)  # Sobel_y
#     #
#     a_1 = a * -1 + 255
#     b_1 = a * 2 + 15
#     c = a_1 + b_1
#     #
#     return bb_convolve(filtMASK_Sobel_y, 1, 640, 480, 8, 8, c)

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

def test_func(a):
    return 255 - a

transformed_func = BasicTranslator.from_function(test_func)
print type(transformed_func)

image = data.coins()

print transformed_func(image)
