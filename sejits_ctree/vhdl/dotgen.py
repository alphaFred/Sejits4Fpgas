""" DOT generator for VHDL constructs. """
__author__ = 'philipp ebensberger'

import ast
from ctree.util import enumerate_flatten
from ctree.dotgen import DotGenLabeller


class VhdlDotGenVisitor(ast.NodeVisitor):
    """
    Generates a representation of the AST in the DOT graph language.
    See http://en.wikipedia.org/wiki/DOT_(graph_description_language)
    """

    visited_nodes = set()

    @staticmethod
    def _qualified_name(obj):
        """ Return object name with leading module """
        return "%s.%s" % (obj.__module__, obj.__name__)

    def label(self, node):
        """
        A string to provide useful information for visualization,
        debugging, etc.
        """
        return r"%s\n%s" % (type(node).__name__, node.label())

    # TODO: change formation to visitor pattern
    def format(self, node):
        """ Format Dot nodes. """
        formats = {"VhdlModule": ', style=filled, fillcolor="#00EB5E"',
                   "VhdlBinaryOp": ', style=filled, fillcolor="#C2FF66"',
                   "VhdlComponent": ', style=filled, fillcolor="#C2FF66"',
                   "VhdlReturn": ', style=filled, fillcolor="#C2FF66"',
                   "VhdlDReg": ', style=filled, shape=rect, fillcolor="#99CCFF"',
                   "VhdlSource": ', style=filled, fillcolor="#FFF066"',
                   "VhdlSink": ', style=filled, fillcolor="#FFF066"',
                   "VhdlConstant": ', style=filled, fillcolor="#FFF066"'
                   }
        return formats.get(type(node).__name__, "")

    def generic_visit(self, node):
        # label this node
        out_string = 'n%s [label="%s" %s];\n' % (id(node),
                                                 self.label(node),
                                                 self.format(node))
        # edges to children
        for fieldname, fieldvalue in ast.iter_fields(node):
            for index, child in enumerate_flatten(fieldvalue):
                if isinstance(child, ast.AST):
                    suffix = "".join(["[%d]" % i for i in index])
                    out_string += 'n{} -> n{} [label="{}{}"];\n'.format(
                        id(node), id(child), fieldname, suffix)
                    if hash(child) not in self.visited_nodes:
                        self.visited_nodes.add(hash(child))
                        out_string += self.visit(child)
                    else:
                        ""
        return out_string


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
        return node.name + " : " + str(node.vhdl_type)

    def visit_Generic(self, node):
        """ Add Generic information to dot node. """
        return node.value.__class__.__name__

    def visit_Constant(self, node):
        """ Add Constant information to dot node. """
        return str(node.value) + " : " + str(node.vhdl_type)

    def visit_VhdlBinaryOp(self, node):
        op_decode = {0: "Add", 1 : "Sub", 2: "Mul"}
        return op_decode[node.op] + "\n" + "d=" + str(node.d) + " | " + "dprev=" + str(node.dprev)

    def visit_VhdlComponent(self, node):
        return node.name + "\n" + "d=" + str(node.d) + " | " + "dprev=" + str(node.dprev)

    def visit_VhdlReturn(self, node):
        return "dprev=" + str(node.dprev)

    def visit_VhdlConstant(self, node):
        return node.value

    def visit_VhdlDReg(self, node):
        return "d=" + str(node.d)

    def visit_VhdlSink(self, node):
        return node.name

    def visit_VhdlSource(self, node):
        return node.name
