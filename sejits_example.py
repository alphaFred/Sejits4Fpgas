""" Example of Ctree Specializer/Transformer and Visitor. """

import numpy as np
import time
import ast
import ctree
import inspect
import textwrap
import sejits_ctree
from skimage.filters import scharr, prewitt
# from skimage.filters import sobel_v, sobel_h, scharr_h, scharr_v
from sejits_ctree.vhdl.scikit_image.transformations import VhdlTransformer
from sejits_ctree.vhdl.codegen import VhdlCodeGen
from sejits_ctree.transformations import PyBasicConversions


def test_func(img):
    """ return skimage.filters.sobel(img) """
    edge_scharr = scharr(img)
    edge_prewitt = prewitt(img)

    diff_scharr_prewitt = edge_scharr - edge_prewitt
    res = diff_scharr_prewitt + edge_scharr
    return res

t1 = time.time()
# tree = sejits_ctree.get_ast(test_func)
tree = VhdlTransformer().visit(sejits_ctree.get_ast(test_func))
t2 = time.time()
print "VhdlTransformer execution time: %s sec" % str(t2 - t1)

code = VhdlCodeGen().run(tree)
#
with open("test_code.vhdl", 'w') as f:
    f.write(code)
#
sejits_ctree.browser_show_ast(tree, file_name="test_graph.png")
