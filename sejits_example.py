""" Example of Ctree Specializer/Transformer and Visitor. """

import sejits_ctree
import time
from skimage.filters import scharr, prewitt, sobel
from skimage.data import camera
# from skimage.filters import sobel_v, sobel_h, scharr_h, scharr_v
from sejits_ctree.vhdl.scikit_image.transformations import VhdlKeywordTransformer
from sejits_ctree.vhdl.scikit_image.transformations import VhdlBasicTransformer
from sejits_ctree.vhdl.scikit_image.transformations import FuncResolver
from sejits_ctree.vhdl.scikit_image.transformations import FuncSubstituter
from sejits_ctree.vhdl.codegen import VhdlCodeGen
# from sejits_ctree.transformations import PyBasicConversions
from sejits_ctree.types import get_ctype
from sejits_ctree.vhdl.jit_synth import LazySpecializedFunction
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
        t1 = time.time()
        funcres_tree = FuncResolver().visit(sejits_ctree.get_ast(test_func))
        t2 = time.time()
        _t1 = "FuncResolver execution time: %s sec" % str(t2 - t1)

        t1 = time.time()
        functrans_tree = FuncSubstituter().visit(funcres_tree)
        t2 = time.time()
        _t2 = "FuncSubstituter execution time: %s sec" % str(t2 - t1)

        t1 = time.time()
        keytrans_tree = VhdlKeywordTransformer().visit(functrans_tree)
        t2 = time.time()
        _t3 = "VhdlKeywordTransformer execution time: %s sec" % str(t2 - t1)

        t1 = time.time()
        trees = VhdlBasicTransformer().run(keytrans_tree)
        t2 = time.time()
        _t4 = "VhdlBasicTransformer execution time: %s sec" % str(t2 - t1)
        #
        print """
>> generate debug output:
\t\t{0}\n\t\t{1}\n\t\t{2}\n\t\t{3}""".format(_t1, _t2, _t3, _t4)
        #
        # generate debug output
        self.generate_debug_output(trees)
        #
        return None

    def generate_debug_output(self, vhdl_proj):
        for idx, tree in enumerate(vhdl_proj.files):
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

    def finalize(self, transform_result, program_config):
        return BasicVhdlFunc()

class BasicVhdlFunc(ConcreteSpecializedFunction):
    def __init__(self):
        super(BasicVhdlFunc, self).__init__()

    def __call__(self, *args, **kwargs):
        print "Call of ConcreteSpecializedFunction"


def main():
    vhdl_trans = BasicVhdlTrans.from_function(test_func)
    img = camera()
    vhdl_trans(img)

if __name__ == "__main__":
    main()
