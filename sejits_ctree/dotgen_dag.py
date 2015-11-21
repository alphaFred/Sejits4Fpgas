import ast

from sejits_ctree.visitors import NodeVisitor
from sejits_ctree.util import enumerate_flatten


def dag_label_for_py_ast_nodes(self):
    from sejits_ctree.py.dotgen import PyDotLabeller
    return PyDotLabeller().visit(self)

def dag_to_dot_outer_for_py_ast_nodes(self):
    return "digraph mytree {\n%s\n%s}" % (str.join("\n",
                                                   ['rankdir="LR"',
                                                    'splines=line',
                                                    'splines=true',
                                                    'node []']),
                                          self._to_dot())

def dag_to_dot_inner_for_py_ast_nodes(self):
    from sejits_ctree.dotgen_dag import DagDotGenVisitor
    return DagDotGenVisitor().visit(self)

"""
Bind to_dot_for_py_ast_nodes to all classes that derive from ast.AST. Ideally
we'd be able to bind one method to ast.AST, but it's a built-in type so we
can't.
"""
for entry in ast.__dict__.values():
    try:
        if issubclass(entry, ast.AST):
            entry.label = dag_label_for_py_ast_nodes
            entry.to_dot = dag_to_dot_outer_for_py_ast_nodes
            entry._to_dot = dag_to_dot_inner_for_py_ast_nodes
    except TypeError:
        pass


class DotGenLabeller(NodeVisitor):
    def generic_visit(self, node):
        return ""


class DagDotGenVisitor(NodeVisitor):

    """
    Generates a representation of the AST in the DOT graph language.

    See http://en.wikipedia.org/wiki/DOT_(graph_description_language)
    """

    def __init__(self):
        """ docstring for __init__. """
        self.dag_objs = set()

    @staticmethod
    def _qualified_name(obj):
        """ Return object name with leading module. """
        return "%s.%s" % (obj.__module__, obj.__name__)

    def label(self, node):
        """ Return string for visualization, debugging, etc. """
        return r"%s\n%s" % (type(node).__name__[3:], node.label())

    # TODO: change formation to visitor pattern
    def format(self, node):
        """ docstring for format. """
        formats = {"DagImageFilter": ', style=filled, fillcolor="#00EB5E"',
                   "DagImagePointOp": ', style=filled, fillcolor="#C2FF66"',
                   "DagInImage": ', style=filled, fillcolor="#FFF066"',
                   "DagOutImage": ', style=filled, fillcolor="#FFA366"'
                   }
        return formats.get(type(node).__name__, "")

    def generic_visit(self, node):
        """ docstring for generic_visit. """
        # label this node
        out_string = 'n%s [label="%s" %s];\n' % (id(node),
                                                 self.label(node),
                                                 self.format(node))
        # edges to children
        try:
            for next_node in node.next:
                if hash((id(node), id(next_node))) not in self.dag_objs:
                    out_string += 'n{} -> n{} [label="{} -> {}"];\n'.format(
                        id(node), id(next_node),
                        getattr(node, "prod", "").__class__.__name__,
                        getattr(next_node, "cons", "").__class__.__name__)
                    #
                    self.dag_objs.add(hash((id(node), id(next_node))))
                out_string += self.visit(next_node)
        except AttributeError:
            pass
        return out_string
