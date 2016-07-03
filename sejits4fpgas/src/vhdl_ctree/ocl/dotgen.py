"""
DOT generation for OpenCL.
"""

from ..dotgen import DotGenLabeller


class OclDotLabeller(DotGenLabeller):
    """
    Visitor to generator DOT.
    """
    def visit_OclFile(self, node):
        return node.get_filename()
