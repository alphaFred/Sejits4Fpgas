""" DAG nodes for VHDL constructs. """
__author__ = 'philipp ebensberger'

import logging
# set up module-level logger
log = logging.getLogger(__name__)

from sejits_ctree.types import get_ctype
from sejits_ctree.nodes import VhdlTreeNode, File


std_libs = ["library ieee", "use ieee.std_logic_1164.all"]


class VhdlNode(VhdlTreeNode):

    """Base class for all VHDL nodes in sejits_ctree."""

    def codegen(self, indent=0):
        """
        Generate Vhdl code of node.

        Args:
            indent: number of spaces per indentation level (Default = 0)

        Returns:
            string with source code of node
        """
        # from sejits_ctree.vhdl.codegen import VhdlCodeGen
        # return VhdlCodeGen(indent).visit(self)
        pass

    def label(self):
        """ Return node label for dot file. """
        from sejits_ctree.vhdl.dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)


class VhdlFile(VhdlNode, File):

    """Represents a .vhd file."""

    _ext = "vhd"

    def __init__(self,
                 name="generated",
                 libs=None,
                 body=None,
                 config_target='vhdl',
                 path=None):
        """ docstring dummy. """
        VhdlNode.__init__(self)
        # body = entity, archs
        File.__init__(self, name, body, path)
        #
        self.libs = std_libs + libs if libs else std_libs
        #
        self.config_target = config_target

    def synthesise(self, program_text):
        """ docstring dummy. """
        pass


# =============================================================================#
# NODES
# =============================================================================#

class Op:
    class _Op(VhdlNode):
        def __str__(self):
            return self._vhdl_str

    class Add(_Op):
        _vhdl_str = "add"

    class Mul(_Op):
        _vhdl_str = "mul"

    class Div(_Op):
        _vhdl_str = "div"

    class Sub(_Op):
        _vhdl_str = "sub"

    class Pow(_Op):
        _vhdl_str = "pow"



class Statement(VhdlNode):
    """ docstring dummy."""
    pass


class Expression(VhdlNode):
    """ docstring dummy. """


class Literal(Expression):
    """ docstring dummy. """
    pass


class Return(Statement):
    """ docstring dummy. """
    _fields = ['value']

    def __init__(self, value=None):
        self.value = value
        super(Return, self).__init__()


class Constant(Literal):
    """ docstring dummy. """
    _fields = ['value', 'type']

    def __init__(self, value=None, type=None):
        self.value = value
        if type is None:
            self.type = get_ctype(self.value)
        else:
            self.type = type
        super(Constant, self).__init__()

class BinaryOp(Expression):
    """Cite me."""
    _fields = ['left', 'op', 'right']

    def __init__(self, left=None, op=None, right=None):
        self.left = left
        self.op = op
        self.right = right
        super(BinaryOp, self).__init__()

class String(Literal):
    """Cite me."""

    def __init__(self, *values):
        self.values = values
        super(String, self).__init__()


class Return(Statement):
    """ docstring dummy. """
    _fields = ['value']

    def __init__(self, value=None):
        self.value = value
        super(Return, self).__init__()


class SymbolRef(Literal):
    """ docstring dummy. """
    _next_id = 0
    _fields = ['name', 'type']

    def __init__(self, name=None, sym_type=None, _global=False,
                 _local=False, _const=False):
        """
        Create a new symbol with the given name.

        If a declaration type is specified, the symbol is considered a
        declaration and unparsed with the type.
        """
        self.name = name
        if sym_type is not None:
            assert not isinstance(sym_type, type)
        self.type = sym_type
        self._global = _global
        self._local = _local
        self._const = _const
        super(SymbolRef, self).__init__()

    def __str__(self):
        return self.name

    @classmethod
    def unique(cls, name="name", sym_type=None):
        """ Factory for making unique symbols. """
        sym = SymbolRef("%s_%d" % (name, cls._next_id), sym_type)
        cls._next_id += 1
        return sym

class EntityDecl(Statement):
    """ docstring dummy. """
    _fields = ['params']

    def __init__(self, return_type=None, name=None, params=None):
        self.return_type = return_type
        self.name = name
        self.params = params if params else []
        self.inline = False
        self.static = False
        self.kernel = False
        super(EntityDecl, self).__init__()


class Architecture(Statement):
    """ docstring dummy. """
    _fields = ['body']

    def __init__(self, body=None):
        self.body = body if body else []
        self.components = set()
        super(Architecture, self).__init__()

    def add_component(self, node):
        """ Create set of instantiated components. """
        self.components.add(node)


class ComponentCall(Expression):
    """ docstring dummy. """
    _fields = ['comp', 'args']

    def __init__(self, comp=None, args=None):
        self.comp = comp
        self.args = args if args else []
        super(ComponentCall, self).__init__()
