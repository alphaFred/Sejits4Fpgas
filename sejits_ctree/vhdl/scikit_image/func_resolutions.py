""" Contains FunctionResolutions for scikit-image functions """

import sejits_ctree
from sejits_ctree.visitors import NodeTransformer


class BaseFunctionalResolver(NodeTransformer):

    """ Base class for FunctionTransformers. """

    def __init__(self):
        """ Initialize super class. """
        super(BaseFunctionalResolver, self).__init__()

    def visit_Call(self, node):
        """ Check if called function has to be transformed. """
        self.generic_visit(node)
        if getattr(node.func, "id", None) == self.func_name:
            return self.convert(node)
        else:
            return node

    def convert(self, node):
        """ Convert passed node. """
        # in_args = self._get_args(node)
        in_args = None
        component_call = self.get_def(node, in_args)
        return component_call

    def _get_args(self, node):
        """ Extract arguments from node. """
        raise NotImplementedError("Implement BaseFunctionalResolver._get_args first!")

    @property
    def func_name(self):
        """ String representing function name. """
        raise NotImplementedError("Class %s should override func_name()"
                                  % type(self))

    def get_def(self, inner_function_name, params):
        """ Return Python AST representaton of function. """
        raise NotImplementedError("Class %s should override get_def()"
                                  % type(self))


class sobel_Resolver(BaseFunctionalResolver):

    """ Resolve sobel source code and return AST. """

    func_name = "sobel"

    def get_def(self, func, in_args):
        from skimage.filters import sobel
        return sejits_ctree.get_ast(sobel)
