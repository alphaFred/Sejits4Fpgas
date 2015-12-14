""" Example of Ctree Specializer/Transformer and Visitor. """

import sejits_ctree
from skimage.filters import scharr, prewitt, sobel
# from skimage.filters import sobel_v, sobel_h, scharr_h, scharr_v
from sejits_ctree.vhdl.scikit_image.transformations import VhdlKeywordTransformer
from sejits_ctree.vhdl.scikit_image.transformations import VhdlBasicTransformer
from sejits_ctree.vhdl.scikit_image.transformations import FuncResolver
from sejits_ctree.vhdl.scikit_image.transformations import FuncSubstituter
from sejits_ctree.vhdl.codegen import VhdlCodeGen
# from sejits_ctree.transformations import PyBasicConversions
from sejits_ctree.types import get_ctype
from sejits_ctree.jit import LazySpecializedFunction
from sejits_ctree.jit import ConcreteSpecializedFunction

def test_func(img):
    """ return skimage.filters.sobel(img) """
    out = sobel(img)
    return out


class BasicVhdlTrans(LazySpecializedFunction):

    """ docstring dummy. """

    def args_to_subconfig(self, args):
        return {'arg_type': type(get_ctype(args[0]))}

    def transform(self, tree, program_config):
        vdhl_tree_proj = VhdlBasicTransformer().run(tree)
        #
        for idx, vhdl_file in enumerate(vdhl_tree_proj.files):
            code = VhdlCodeGen().run(vhdl_file)
            with open("test_code.vhdl", 'a') as f:
                f.write(code)
                f.write("\n" + "-" * 80 + "\n")
            name = "test_graph_" + str(idx) + ".png"
            sejits_ctree.browser_show_ast(tree, file_name=name)
        #
        return vdhl_tree_proj

    def finalize(self, transform_result, program_config):
        return BasicVhdlFunc()

class BasicVhdlFunc(ConcreteSpecializedFunction):
    pass


"""
t1 = time.time()
# tree = sejits_ctree.get_ast(test_func)
tree = VhdlTransformer().visit(sejits_ctree.get_ast(test_func))
t2 = time.time()
print "VhdlTransformer execution time: %s sec" % str(t2 - t1)

code = VhdlCodeGen().run(tree)
#
with open("test_code.vhdl", 'w') as f:
    f.write(code)
"""
funcres_tree = FuncResolver().visit(sejits_ctree.get_ast(test_func))
functrans_tree = FuncSubstituter().visit(funcres_tree)
keytrans_tree = VhdlKeywordTransformer().visit(functrans_tree)
trees = VhdlBasicTransformer().run(keytrans_tree)
for idx, tree in enumerate(trees.files):
    code = VhdlCodeGen().run(tree)
    if idx == 0:
        with open("test_code.vhdl", 'w') as f:
            f.write(code)
            f.write("\n" + "-" * 80 + "\n")
    else:
        with open("test_code.vhdl", 'a') as f:
            f.write(code)
            f.write("\n" + "-" * 80 + "\n")
    name = "test_graph_" + str(idx) + ".png"
    sejits_ctree.browser_show_ast(tree, file_name=name)
