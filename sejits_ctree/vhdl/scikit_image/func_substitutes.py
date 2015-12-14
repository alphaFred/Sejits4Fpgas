""" Contains FunctionTransformers for scikit-image functions """

import time
from skimage.data import camera
from ast import NodeTransformer


class BaseFunctionalTransformer(NodeTransformer):

    """ Base class for FunctionTransformers. """

    def __init__(self):
        """ Initialize super class. """
        super(BaseFunctionalTransformer, self).__init__()

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
        in_args = [camera(), 2]
        component_call = self.get_def(node, in_args)
        return component_call

    def _get_args(self, node):
        """ Extract arguments from node. """
        raise NotImplementedError("Implement BaseFunctionalTransformer._get_args first!")

    @property
    def func_name(self):
        """ String representing function name. """
        raise NotImplementedError("Class %s should override func_name()"
                                  % type(self))

    def get_def(self, inner_function_name, params):
        """ Return Python AST representaton of function. """
        raise NotImplementedError("Class %s should override get_def()"
                                  % type(self))


class assert_nD_Substituter(BaseFunctionalTransformer):
    func_name = "assert_nD"

    def get_def(self, func, in_args):
        """ Assert if arguments are correct. """
        import numpy as np
        #
        array = in_args[0]
        ndim = in_args[1]
        arg_name = "image"
        #
        array = np.asanyarray(array)
        msg = "The parameter `%s` must be a %s-dimensional array"
        if isinstance(ndim, int):
            ndim = [ndim]
        if array.ndim not in ndim:
            raise ValueError(msg % (arg_name, '-or-'.join([str(n)
                                    for n in ndim])))
        return None
