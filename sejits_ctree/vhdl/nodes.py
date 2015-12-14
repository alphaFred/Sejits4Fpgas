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


class VhdlProject(object):

    """ Base class for an Vhdl Project. """

    files = []

    def __init__(self, master_file):
        self.add_file(master_file)
        # create base folder with master file

    def add_file(self, file):
        if type(file) is list:
            self.files += file
        else:
            self.files.append(file)

# =============================================================================#
# NODES
# =============================================================================#

class Op:
    class _Op(VhdlNode):
        def __str__(self):
            return self._vhdl_str

        def sig_ref(self):
            return self

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

    def sig_ref(self):
        return self.value.sig_ref()


class Constant(Literal):
    """ docstring dummy. """
    _fields = ['value', 'type']

    def __init__(self, value=None, sym_type=None):
        self.value = value
        self.type = sym_type
        """
        if type is None:
            self.type = get_ctype(self.value)
        else:
            self.type = type
        """
        super(Constant, self).__init__()

    def __str__(self):
        return str(self.value)

    def sig_ref(self):
        return self


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


class SymbolRef(Literal):
    """ docstring dummy. """
    _next_id = 0
    _fields = ['name', 'type']

    def __init__(self, name=None, sym_type=None):
        """
        Create a new symbol with the given name.

        If a declaration type is specified, the symbol is considered a
        declaration and unparsed with the type.
        """
        self.name = name
        if sym_type is not None:
            assert not isinstance(sym_type, type)
        self.type = sym_type
        super(SymbolRef, self).__init__()

    def __str__(self):
        return self.name

    def sig_ref(self):
        return self

    @classmethod
    def unique(cls, name="name", sym_type=None):
        """ Factory for making unique symbols. """
        sym = SymbolRef("%s_%d" % (name, cls._next_id), sym_type)
        cls._next_id += 1
        return sym


class Entity(Statement):
    """ docstring dummy. """
    _fields = ['in_args', 'out_arg']

    def __init__(self, name=None, in_args=None, out_arg=None):
        self.name = name
        self.in_args = in_args if in_args else []
        self.out_arg = out_arg if out_arg else None
        super(Entity, self).__init__()


class Architecture(Statement):
    """ docstring dummy. """
    _fields = ['body', 'signals']

    def __init__(self, body=None, signals=None):
        self.body = body if body else []
        self.signals = signals if signals else []
        self.components = set()
        super(Architecture, self).__init__()

    def add_component(self, node):
        """ Create set of instantiated components. """
        self.components.add(node)


class ComponentCall(Expression):
    """ docstring dummy. """
    _fields = ['comp', 'in_args', 'out_args']

    def __init__(self, comp=None, in_args=None, out_args=None):
        """ Initialize ComponentCall node. """
        self.comp = comp
        self.in_args = in_args if in_args else []
        self.out_args = out_args if out_args else\
            SymbolRef(name="sig_" + str(hash(self)), sym_type=None)
        super(ComponentCall, self).__init__()

    def sig_ref(self):
        """ Return signal reference to value/return value of node. """
        return self.out_args


class Block(Statement):
    """ docstring dummy. """
    _fields = ['body']

    def __init__(self, body=None):
        assert isinstance(body, list)
        self.body = body

    def sig_ref(self):
        return self.body[0].sig_ref()
