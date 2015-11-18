import ast

from sejits_ctree.visitors import NodeVisitor
from sejits_ctree.util import enumerate_flatten


def label_for_py_ast_nodes(self):
    from sejits_ctree.py.dotgen import PyDotLabeller

    return PyDotLabeller().visit(self)

def to_dot_outer_for_py_ast_nodes(self):
    return "digraph mytree {\n%s}" % self._to_dot()

def to_dot_inner_for_py_ast_nodes(self):
    from sejits_ctree.dotgen import DotGenVisitor

    return DotGenVisitor().visit(self)

"""
Bind to_dot_for_py_ast_nodes to all classes that derive from ast.AST. Ideally
we'd be able to bind one method to ast.AST, but it's a built-in type so we
can't.
"""
for entry in ast.__dict__.values():
    try:
        if issubclass(entry, ast.AST):
            entry.label   = label_for_py_ast_nodes
            entry.to_dot  = to_dot_outer_for_py_ast_nodes
            entry._to_dot = to_dot_inner_for_py_ast_nodes
    except TypeError:
        pass


class DotGenLabeller(NodeVisitor):
    def generic_visit(self, node):
        return ""


class DotGenVisitor(NodeVisitor):
    """
    Generates a representation of the AST in the DOT graph language.
    See http://en.wikipedia.org/wiki/DOT_(graph_description_language)
    """
    @staticmethod
    def _qualified_name(obj):
        """
        return object name with leading module
        """
        return "%s.%s" % (obj.__module__, obj.__name__)

    def label(self, node):
        """
        A string to provide useful information for visualization, debugging, etc.
        """
        return r"%s\n%s" % (type(node).__name__, node.label())

    # TODO: change formation to visitor pattern
    def format(self, node):
        formats = {"ImageFilter": ', style=filled, fillcolor="#00EB5E"',
                   "ImagePointOp":', style=filled, fillcolor="#C2FF66"',
                   "TempAssign":  ', style=filled, fillcolor="#66C2FF"',
                   "OutAssign":   ', style=filled, fillcolor="#6675FF"',
                   "InImageObj":  ', style=filled, fillcolor="#FFF066"',
                   "OutImageObj": ', style=filled, fillcolor="#FFA366"'
                   }
        return formats.get(type(node).__name__, "")

    def generic_visit(self, node):

        # label this node
        out_string = 'n%s [label="%s" %s];\n' % (id(node), self.label(node), self.format(node))

        # edges to children
        for fieldname, fieldvalue in ast.iter_fields(node):
            for index, child in enumerate_flatten(fieldvalue):
                if isinstance(child, ast.AST):
                    suffix = "".join(["[%d]" % i for i in index])
                    out_string += 'n{} -> n{} [label="{}{}"];\n'.format(
                        id(node), id(child), fieldname, suffix)
                    out_string += self.visit(child)
        return out_string
