__author__ = 'philipp ebensberger'

import ast
import inspect
import Image

import sejits_ctree

from asp import tree_grammar
from specializer.dsl.dsl_specification import dsl

from specializer.utils.ast_visualizer import pformat_ast
from specializer.utils.dsl_ast_transformer import DslAstTransformer
from specializer.fpga.fpga_ast_optimizer import FpgaAstOptimizer
from specializer.dsl.dsl_specification import dsl

 
class ZYNQ_Specializer(object):
    """ docstring for ZYNQ_Specializer """
    def __init__(self, args, func):
        """ docstring for __init__ """
        # parse dsl and add dsl classes to dsl_classes dictionary
        self.dsl_classes = dict()
        tree_grammar.parse(dsl, self.dsl_classes, checker=None)
        # TODO: remove ALL decorators! -> multiple decorators etc.
        func_src = "\n".join(inspect.getsource(func).splitlines()[1:])
        self.func_ast = ast.parse(func_src.lstrip())
        self.func_args = args

    # ======================================================================= #
    #   HELPER METHODS                                                        #
    # ======================================================================= #
    def run(self):
        """ docstring for run """
        ast_transformer = DslAstTransformer(self.func_ast, self.func_args, self.dsl_classes)
        trans_ast = ast_transformer.run()
        ast.__dict__.update(self.dsl_classes)
        sejits_ctree.browser_show_ast(trans_ast, file_name="transformed_dsl_ast.png")
        # DEBUG
        print "\nKERNEL TRANSFORMED\n"
        #pformat_ast(trans_ast)
        print "#"*80,"\n\n"
        # !DEBUG
        
        ast_optimizer = FpgaAstOptimizer(trans_ast, self.dsl_classes)
        opt_ast = ast_optimizer.run()
        sejits_ctree.browser_show_ast(opt_ast, file_name="optimized_dataFlow.png")

        return None
