""" DOT generator for VHDL constructs. """
__author__ = 'philipp ebensberger'

from sejits_ctree.dotgen import DotGenLabeller


class VhdlDotGenLabeller(DotGenLabeller):

    """ Manages generation of DOT. """

    def visit_Component(self, node):
        """ Add Component information to dot node. """
        return node.name

    def visit_Port(self, node):
        """ Add Port information to dot node. """
        return node.direction

    def visit_Signal(self, node):
        """ Add Signal information to dot node. """
        return node.name + " : " + node.vhdl_type

    def visit_Generic(self, node):
        """ Add Generic information to dot node. """
        return node.value.__class__.__name__

    def visit_Constant(self, node):
        """ Add Constant information to dot node. """
        return str(node.value) + " : " + node.vhdl_type
