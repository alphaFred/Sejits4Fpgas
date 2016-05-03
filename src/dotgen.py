""" DOT generator for VHDL constructs. """

import ast
from .vhdl_ctree.util import enumerate_flatten
from .vhdl_ctree.dotgen import DotGenLabeller


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

    @staticmethod
    def label(node):
        """
        A string to provide useful information for visualization,
        debugging, etc.
        """
        return r"%s\n%s" % (type(node).__name__, node.label())

    # TODO: change formation to visitor pattern
    @staticmethod
    def format(node):
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

    @staticmethod
    def visit_Component(node):
        """ Add Component information to dot node. """
        return node.name

    @staticmethod
    def visit_Port(node):
        """ Add Port information to dot node. """
        return node.direction

    @staticmethod
    def visit_Signal(node):
        """ Add Signal information to dot node. """
        return node.name + " : " + str(node.vhdl_type)

    @staticmethod
    def visit_Generic(node):
        """ Add Generic information to dot node. """
        return node.value.__class__.__name__

    @staticmethod
    def visit_Constant(node):
        """ Add Constant information to dot node. """
        return str(node.value) + " : " + str(node.vhdl_type)

    @staticmethod
    def visit_VhdlBinaryOp(node):
        op_decode = {0: "Add", 1: "Sub", 2: "Mul"}
        return op_decode[node.op] + "\n" + "d=" + str(node.d) + " | " + "dprev=" + str(node.dprev)

    @staticmethod
    def visit_VhdlComponent(node):
        return node.name + "\n" + "d=" + str(node.d) + " | " + "dprev=" + str(node.dprev)

    @staticmethod
    def visit_VhdlReturn(node):
        return "dprev=" + str(node.dprev)

    @staticmethod
    def visit_VhdlConstant(node):
        return str(node.value)

    @staticmethod
    def visit_VhdlDReg(node):
        return "d=" + str(node.d)

    @staticmethod
    def visit_VhdlSink(node):
        return node.name

    @staticmethod
    def visit_VhdlSource(node):
        return node.name
