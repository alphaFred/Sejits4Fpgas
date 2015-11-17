__author__ = 'philipp ebensberger'

import ast
import inspect

from specializer.utils.ast_visualizer import pformat_ast
from specializer.utils.dsl_ast_transformer import DslAstTransformer


class ZYNQ_Specializer(object):
    """ docstring for ZYNQ_Specializer """
    def __init__(self, args, func):
        """ docstring for __init__ """
        # TODO: remove ALL decorators! -> multiple decorators etc.
        func_src = "\n".join(inspect.getsource(func).splitlines()[1:])
        self.func_ast = ast.parse(func_src.lstrip())
        self.func_args = args

    # ======================================================================= #
    #   HELPER METHODS                                                        #
    # ======================================================================= #
    def run(self):
        """ docstring for run """
        ast_transformer = DslAstTransformer(self.func_ast, self.func_args)
        # DEBUG
        print "\nKERNEL TRANSFORMED\n"
        ret = ast_transformer.run()
        pformat_ast(ret)
        print "#"*80,"\n\n"
        # !DEBUG
        return ret
