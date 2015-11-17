"""
SIMD vector nodes supported by ctree.
"""

from sejits_ctree.nodes import CtreeNode


class SimdNode(CtreeNode):
    """Base class for all SIMD nodes supported by sejits_ctree."""

    def codegen(self, indent=0):
        from sejits_ctree.sse.codegen import SimdCodeGen

        return SimdCodeGen(indent).visit(self)

    def label(self):
        from sejits_ctree.sse.dotgen import SimdDotLabeller

        return SimdDotLabeller().visit(self)
