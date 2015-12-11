""" Example of Ctree Specializer/Transformer and Visitor. """

import sejits_ctree
from skimage.filters import scharr, prewitt, sobel
# from skimage.filters import sobel_v, sobel_h, scharr_h, scharr_v
from sejits_ctree.vhdl.scikit_image.transformations import VhdlBasicTransformer
from sejits_ctree.vhdl.codegen import VhdlCodeGen
# from sejits_ctree.transformations import PyBasicConversions


def test_func(img):
    """ return skimage.filters.sobel(img) """
    return sobel(img)

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
trees = VhdlBasicTransformer().run(sejits_ctree.get_ast(test_func))
for idx, tree in enumerate(trees.files):
    code = VhdlCodeGen().run(tree)
    with open("test_code.vhdl", 'a') as f:
        f.write(code)
        f.write("\n" + "-" * 80 + "\n")
    name = "test_graph_" + str(idx) + ".png"
    sejits_ctree.browser_show_ast(tree, file_name=name)
