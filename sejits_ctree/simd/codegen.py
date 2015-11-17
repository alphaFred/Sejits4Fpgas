"""
Code generation for SIMD.
"""

from sejits_ctree.codegen import CodeGenVisitor


class SimdCodeGen(CodeGenVisitor):
    """
    Visitor to generate SIMD code.
    """
    def visit_m256d(self, node):
        return "__m256d"
