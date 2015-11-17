"""
C preprocessor nodes supported by ctree.
"""

from sejits_ctree.nodes import CtreeNode


class CppNode(CtreeNode):
    """Base class for all C Preprocessor nodes in sejits_ctree."""

    def codegen(self, indent=0):
        from sejits_ctree.cpp.codegen import CppCodeGen

        return CppCodeGen(indent).visit(self)

    def label(self):
        from sejits_ctree.cpp.dotgen import CppDotLabeller

        return CppDotLabeller().visit(self)

    def _requires_semicolon(self):
        return False


class CppInclude(CppNode):
    """Represents #include <foo.h>."""

    def __init__(self, target="", angled_brackets=True):
        self.target = target
        self.angled_brackets = angled_brackets


class CppComment(CppNode):
    """Represents // foo"""

    def __init__(self, text=""):
        self.text = text


class CppDefine(CppNode):
    _fields = ['name', 'params', 'body']

    def __init__(self, name=None, params=None, body=None):
        self.name = name
        self.params = params
        self.body = body
        super(CppDefine, self).__init__()
