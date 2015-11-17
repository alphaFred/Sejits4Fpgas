__author__ = 'philipp ebensberger'

import inspect
import ast
import types

import asp.tree_grammar as tree_grammar
from specializer.utils.ast_visualizer import pformat_ast
from specializer.dsl.dsl_specification import dsl
from specializer.utils.dsl_ast_transformer import DslAstData
from specializer.utils.dsl_ast_transformer import DslAstTransformer


class Zynq_Specializer(object):
    def __init__(self, args, func):
        # TODO: remove ALL decorators! -> multiple decorators etc.
        func_src = "\n".join(inspect.getsource(func).splitlines()[1:])
        func_ast = ast.parse(func_src.lstrip())
        # pack ast-data
        self.func_ast_data = DslAstData(ast = func_ast,
                                        args = args)

    # ======================================================================= #
    #   HELPER METHODS                                                        #
    # ======================================================================= #
    def run(self):
        ast_transformer = DslAstTransformer(self.func_ast_data)
        # DEBUG
        print "\nKERNEL TRANSFORMED\n"
        ret = ast_transformer.run()
        pformat_ast(ret)
        print "#"*80,"\n\n"
        # !DEBUG
        return ret
