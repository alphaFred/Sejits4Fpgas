"""
Cilk nodes supported by ctree.
"""

from sejits_ctree.nodes import CtreeNode


class CilkNode(CtreeNode):
    """Base class for all Cilk nodes supported by sejits_ctree."""

    def codegen(self, indent=0):
        from sejits_ctree.cilk.codegen import CilkCodeGen

        return CilkCodeGen(indent).visit(self)

    def _to_dot(self, _):
        from sejits_ctree.cilk.dotgen import CilkDotLabeller

        return CilkDotLabeller().visit(self)
