"""
Support for Python ast nodes in the 'ast' module.
"""

import ast

# ---------------------------------------------------------------------------
# dot generator

from sejits_ctree.dotgen import DotGenLabeller


class PyDotLabeller(DotGenLabeller):  # pragma: no cover
    """
    Manages generation of DOT.
    """

    def visit_arg(self, node):
        s = "name: %s" % node.arg
        if node.annotation and not isinstance(node.annotation, ast.AST):
            s += "\nannotation: %s" % self._qualified_name(node.annotation)
        return s

    def visit_KernelModule(self, node):
        return "id: %s" % node.id

    def visit_InImageObj(self, node):
        return "id: %s" % node.id

    def visit_OutImageObj(self, node):
        return "id: %s" % node.id

    def visit_Constant(self, node):
        return "id: %s\nvalue: %s" % (node.id, node.value)

    def visit_Int(self, node):
        if node.id is not None:
            return "id: %s\nn: %s" % (node.id, node.n)
        else:
            return "n: %s" % (node.n)

    def visit_Float(self, node):
        if node.id is not None:
            return "id: %s\nn: %s" % (node.id, node.n)
        else:
            return "n: %s" % (node.n)

    def visit_Index(self, node):
        return "n: %s" % node.n

    def visit_Identifier(self, node):
        return "name: %s" % node.name

    def visit_FunctionDef(self, node):
        return "name: %s" % node.name

    def visit_Num(self, node):
        return "n: %s" % node.n

    def visit_Name(self, node):
        return "id: %s" % node.id

    def visit_Attribute(self, node):
        return "attr: %s" % node.attr

    def visit_Str(self, node):
        return "str: %s" % node.s
