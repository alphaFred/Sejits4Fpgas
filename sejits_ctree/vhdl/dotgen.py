""" DOT generator for VHDL constructs. """
__author__ = 'philipp ebensberger'

from sejits_ctree.dotgen import DotGenLabeller
from sejits_ctree.types import codegen_type


class VhdlDotGenLabeller(DotGenLabeller):

    """ Manages generation of DOT. """

    def visit_SymbolRef(self, node):
        """ docstring dummy. """
        s = r""
        if node._global:
            s += r"__global "
        if node._local:
            s += r"__local "
        if node._const:
            s += r"__const "
        if node.type is not None:
            s += r"%s " % codegen_type(node.type)
        s += r"%s" % node.name
        return s

    def visit_VhdlFile(self, node):
        return node.name

    def visit_Constant(self, node):
        return str(node.type)
