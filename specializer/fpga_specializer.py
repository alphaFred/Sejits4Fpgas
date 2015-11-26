""" docstring for module fpga_specializer. """
__author__ = 'philipp ebensberger'

import ast
import inspect
import sejits_ctree
import copy

from asp import tree_grammar
from specializer.dsl.dsl_specification import dsl
from specializer.utils.dsl_ast_transformer import DslAstTransformer
from specializer.fpga.fpga_ast_optimizer import FpgaDagCreator
from specializer.fpga.fpga_codegen import FpgaCodeGen


class ZynqSpecializer(object):

    """ docstring for ZYNQ_Specializer. """

    def __init__(self, args, func):
        """ docstring for __init__. """
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
        """ docstring for run. """
        ast_transformer = DslAstTransformer(self.func_ast,
                                            self.func_args,
                                            self.dsl_classes)
        dag_creator = FpgaDagCreator()
        #
        ast.__dict__.update(self.dsl_classes)
        ast.__dict__.update(dag_creator.getDagDict())

        # transform ast and save result
        trans_ast = ast_transformer.run()
        _trans_ast = copy.deepcopy(trans_ast)
        # optimize ast and create dag
        dag_graph = dag_creator.run(trans_ast)
        #
        # Codegen
        fpga_codegenerator = FpgaCodeGen()
        fpga_codegenerator.run(dag_graph)
        #
        # create output images
        sejits_ctree.browser_show_ast(_trans_ast,
                                      file_name="transformed_graph.png")
        print "generated: transformed_dsl_ast.png"
        sejits_ctree.browser_show_dag(dag_graph,
                                      file_name="dag_graph.png")
        print "generated: dag_graph.png"
        return None
