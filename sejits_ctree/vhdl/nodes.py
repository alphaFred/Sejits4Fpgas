""" Nodes contains all vhdl nodes """
__author__ = "philipp ebensberger"
__name__ = "vhdl_nodes"
__package__ = "sejits_ctree.vhdl"

import os
import ast
import logging

from . import STDLIBS
from collections import defaultdict, namedtuple
from dotgen import VhdlDotGenVisitor
from ctree.nodes import File


# set up module-level logger
log = logging.getLogger(__name__)


class VhdlTreeNode(ast.AST):

    """ Base class for all Vhdl AST nodes in sejits_ctree."""

    def __init__(self):
        """Initialize a new AST Node."""
        super(VhdlTreeNode, self).__init__()
        self.deleted = False
        self._force_parentheses = False

    def __str__(self):
        return self.__class__.__name__

    def to_dot(self):
        """ Retrieve the AST in DOT format for visualization."""
        return "digraph mytree {\n%s}" % self._to_dot()

    def _to_dot(self):
        """ Retrieve the AST in DOT format for vizualization."""
        return VhdlDotGenVisitor().visit(self)

    def lift(self, **kwargs):
        for key, val in kwargs.items():
            attr = "_lift_%s" % key
            setattr(self, attr, getattr(self, attr, []) + val)
            type(self)._fields.append(attr)


class VhdlNode(VhdlTreeNode):

    """Base class for all VHDL nodes in sejits_ctree."""

    def codegen(self, indent=4):
        """
        Generate Vhdl code of node.

        Attributes:
            indent: number of spaces per indentation level (Default = 0)
        Return:
            string with source code of node
        """
        from codegen import VhdlCodeGen
        return VhdlCodeGen(indent).visit(self)

    def label(self):
        """ Return node label for dot file. """
        from dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)


Interface = namedtuple("Interface", ["iports", "oport"])


class VhdlFile(VhdlNode, File):

    """Represents a .vhd file."""

    _ext = "vhd"
    generated = True
    dependencies = []
    latency = 0

    def __init__(self, name="generated", libs=None,
                 entity=None, architecture=None,
                 config_target="vhd", path=None,
                 dependencies=[]):
        """ Initialize VhdlFile. """
        VhdlNode.__init__(self)
        File.__init__(self, name, [entity, architecture], path)
        #
        if entity:
            self._interface = Interface(entity.in_ports, entity.out_port)
        else:
            self._interface = []
        if libs:
            self.libs = STDLIBS + list(libs)
        else:
            self.libs = STDLIBS
        #
        self.config_target = config_target
        self.dependencies = dependencies

    def __repr__(self):
        """ Return entity vhdl source code for debug. """
        from codegen import VhdlCodeGen
        return VhdlCodeGen(indent=4).visit(self.body[0])

    def _compile(self, program_text):
        """ Save program_text in file. """
        vhdl_src_file = os.path.join(self.path, self.get_filename())
        # TODO: implement hasing to avoid writing already existing files
        # create vhdl source file
        with open(vhdl_src_file, "w") as vhdl_file:
            vhdl_file.write(program_text)

        return vhdl_src_file

    @property
    def interface(self):
        """ Return interface [in_ports, out_port]. """
        return self._interface

    def codegen(self, indent=4):
        """ Generate source and save in file if VhdlFile.generated == True. """
        from sejits_ctree.vhdl.codegen import VhdlCodeGen

        files = self.dependencies
        gen_files = []

        if len(files) > 0:
            for vhdl_file in files:
                gen_files += vhdl_file.codegen(indent=4)

            if self.generated:
                file_path = self._compile(VhdlCodeGen(indent).visit(self))
                if file_path:
                    gen_files = [file_path] + gen_files
            else:
                gen_files = [self.path] + gen_files
            return gen_files
        else:
            if self.generated:
                file_path = self._compile(VhdlCodeGen(indent).visit(self))
                if file_path:
                    gen_files = [file_path]
            else:
                gen_files = [self.path]
            return gen_files


class VhdlProject(object):

    """ Base class for an Vhdl Project. """

    def __init__(self, files=None, synthesis_dir=""):
        """ Initialize VhdlProject. """
        self.files = files if files else []
        self.synthesis_dir = synthesis_dir

    def codegen(self, indent=4):
        """
        Generate vhdl descriptions of all vhdl files in project
        and pack VhdlSynthModule.

        Attributes:
            indent: number of spaces for tab in codegen
        Return:
            VhdlSynthModule
        """
        from jit_synth import VhdlSynthModule
        from jit_synth import JitSyntDataModule
        self._module = VhdlSynthModule()

        # process vhdl-files in project
        temp_submodules = []
        if len(self.files) > 0:
            for vhdl_file in self.files:
                temp_submodules += vhdl_file.codegen(indent)
            data_module = JitSyntDataModule(self.files[0],
                                            set(temp_submodules))

            # return VhdlSynthModule with linked submodule list
            self._module._link_in(data_module)
            return self._module
        else:
            raise Exception()

# =============================================================================
# COMPONENT NODE CLASSES
# =============================================================================


class Statement(VhdlNode):
    """ docstring dummy."""
    pass


class Expression(VhdlNode):
    """ Base class for Expression nodes. """

    # instance counter to generate unique instance names
    _ids = defaultdict(int)
    lib_name = ""
    latency = 0
    in_ports = []
    out_port = None

    @property
    def out_type(self):
        """ Return node's output type. """
        raise NotImplementedError()


class Literal(VhdlNode):
    """ docstring dummy. """


class LiteralWrapper(VhdlNode):
    """ docstring dummy. """

# LITERALS


class Op(Literal):
    class _Op(Literal):
        vhdl_type = "string"

        def __str__(self):
            return self._str

    class Add(_Op):
        _str = '"Add"'

    class Mul(_Op):
        _str = '"Mul"'

    class Sub(_Op):
        _str = '"Sub"'

    class Div(_Op):
        _str = '"Div"'

    class Pow(_Op):
        _str = '"Pow"'

    class Sqrt(_Op):
        _str = '"Div"'


class Signal(Literal):

    """ Node class for Vhdl Signal. """

    _fields = ["name", "vhdl_type"]

    def __init__(self, name="", vhdl_type=None):
        """ Create a new signal with the given name. """
        if name != "":
            self.name = name
        else:
            raise Exception
        #
        self.vhdl_type = vhdl_type


class Constant(Literal):

    """ Node class for Vhdl Constant. """

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type=None, value=None):
        self._name = name
        self.vhdl_type = vhdl_type
        self.value = value

    @property
    def name(self):
        """ If Constant has a name, add it to Architecture signals. """
        if self._name == "":
            return str(self.value)
        else:
            return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __str__(self):
        return self.name


class Port(LiteralWrapper):

    """ Base class of Vhld Port item. """

    _fields = ["name", "direction", "value"]

    def __init__(self, name="", direction="", value=None):
        """ Initialize name, direction and value of Port. """
        self.name = name
        self.direction = direction
        self.value = value


class Generic(LiteralWrapper):

    """ Base class of Vhdl Generic item. """

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", value=None):
        """ Initialize name and value of Generic. """
        self.name = name
        #
        if isinstance(value, Literal) and type(value) is not Signal:
            self.value = value
            self.vhdl_type = value.vhdl_type
        else:
            raise TypeError


class BinaryOp(Expression):

    """ Node class for Vhdl binary operator. """

    _fields = ["left_port", "op", "right_port", "out_port"]
    _op_values = ({"add", "sub", "mul", "div"})
    lib_name = "work.BasicArithBlocks"
    name = "BinaryOp"

    def __init__(self, left_port=None, op=None, right_port=None,
                 out_port=None):
        """ Initialize BinaryOp node. """
        self.left_port = left_port
        self.right_port = right_port
        #
        self.in_ports = [left_port, right_port]
        #
        self.op = op
        self.out_port = out_port
        # generate unique instance id
        instance_id = self._ids[self.name.lower()]
        self._ids[self.name.lower()] += 1
        # generate unique instance name
        self.instance_name = self.name.lower() +\
            (str(instance_id) if instance_id != 0 else "")

    @property
    def out_type(self):
        """ Return node's output type. """
        # TODO: calculate output type based on input types
        return VhdlType.VhdlStdLogicVector(size=8, default='0')


class UnaryOp(Expression):

    """ Node class for Vhdl unary operator. """

    _fields = ["in_port", "op", "out_port"]
    _op_values = ({"sqrt", "pow"})
    lib_name = "work.BasicArithBlocks"
    name = "UnaryOp"

    def __init__(self, in_port=None, op=None, out_port=None):
        """ Initialize UnaryOp node. """
        self.in_port = in_port
        #
        self.in_ports.append(in_port)
        #
        self.op = op
        self.out_port = out_port
        # generate unique instance id
        instance_id = self._ids[self.name]
        self._ids[self.name] += 1
        # generate unique instance name
        self.instance_name = self.name +\
            (str(instance_id) if instance_id != 0 else "")

    @property
    def out_type(self):
        """ Return node's output type. """
        return self.in_port.value.vhdl_type


class Component(Expression):

    """ Node class for generic Vhdl Component. """

    _fields = ["generics", "in_ports", "out_port"]
    name = ""

    def __init__(self, name="", generics=None, in_ports=None,
                 out_port=None, out_type=""):
        """ Initialize Component node. """
        self.name = name

        self.generics = []
        self.in_ports = []

        if generics is not None:
            self.generics = generics if type(generics) is list else [generics]
        if in_ports is not None:
            self.in_ports = in_ports if type(in_ports) is list else [in_ports]
        self.out_port = out_port

        self._out_type = out_type
        # generate unique instance id
        instance_id = self._ids[self.name]
        self._ids[self.name] += 1
        # generate unique instance name
        self.instance_name = "comp_" + self.name.lower() +\
            (str(instance_id) if instance_id != 0 else "")

    @property
    def out_type(self):
        """ Return node's output type. """
        return self._out_type


# STATEMENTS
class Entity(Statement):

    """ Node class for Entity nodes. """

    _fields = ["name", "generics", "in_ports", "out_port"]

    def __init__(self, name="", generics=[], in_ports=[], out_port=None):
        """ Initialize Entity generics and port lists. """
        clk_sig = Signal(name="CLK_SIG",
                         vhdl_type=VhdlType.VhdlStdLogic())
        rst_sig = Signal(name="RST_SIG",
                         vhdl_type=VhdlType.VhdlStdLogic())
        en_sig = Signal(name="EN_SIG",
                        vhdl_type=VhdlType.VhdlStdLogic())
        self.in_ports = [Port("CLK", "in", clk_sig),
                         Port("RST", "in", rst_sig),
                         Port("EN", "in", en_sig)]
        #
        if name != "":
            self.name = name
        else:
            raise ValueError("An entity name must be provided")
        #
        if all([type(itm) is Generic for itm in generics]):
            self.generics = list(generics)
        else:
            raise TypeError("Initialize generics must be of type Generic")
        #
        if all([type(itm) is Port for itm in in_ports]):
            self.in_ports = list(in_ports)
        else:
            raise TypeError("Initialize in_ports must be of type Port")
        #
        if out_port and type(out_port) is Port:
            self.out_port = out_port
        elif not out_port:
            self.out_port = None
        else:
            raise TypeError("Initialize out_port must be None or of type Port")


class Architecture(Statement):

    """ Node class for Architecture node. """

    _fields = ["entity_name", "architecture_name", "body"]
    signals = None
    components = None

    def __init__(self, entity_name="", architecture_name="behaviour",
                 signals=[], body=[]):
        """
        Initialize Architecture.

        Check signals:
            all elements of singlas must be an instance of Literal.
        Check body:
            all elements of body must be an instance of Expression.
        Check entitiy name:
            an entitiy name must be provided

        Attributes:
            entity_name: Name of architectures entitiy
            architecture_name: Name of architecture
            signals: List of internal architecture signals
            body: List of architectures components
        """
        if entity_name != "":
            self.entity_name = entity_name
        else:
            raise ValueError("An entitiy name must be provided")
        #
        if all([isinstance(itm, Literal) for itm in list(signals)]):
            self.signals = list(signals)
        else:
            raise TypeError("Initialize signals are of invalid type")
        #
        if all([isinstance(itm, Expression) for itm in list(body)]):
            self.body = [self._auto_route(comp) for comp in list(body)]
        else:
            raise TypeError("Initialize body elements are of invalid type")
        #
        self.architecture_name = architecture_name
        #
        super(Architecture, self).__init__()

    def add_signal(self, new_signal):
        """ Add new signal to architecture if instance of Literal. """
        if isinstance(new_signal, Literal):
            self.signals.append(new_signal)
        else:
            raise TypeError("Invalid signal type: %s" % type(new_signal))

    def add_component(self, new_component):
        """ Add new component to architecture if instance of Expression. """
        if isinstance(new_component, Expression):
            self.body.append(self._auto_route(new_component))
        else:
            raise TypeError("Invalid component type: %s" % type(new_component))

    def _auto_route(self, component):
        """ Add infrastructure ports to component. """
        clk_sig = Signal(name="CLK_SIG",
                         vhdl_type=VhdlType.VhdlStdLogic())
        rst_sig = Signal(name="RST_SIG",
                         vhdl_type=VhdlType.VhdlStdLogic())
        en_sig = Signal(name="EN_SIG",
                        vhdl_type=VhdlType.VhdlStdLogic())
        #
        component.in_ports.extend([Port("CLK", "in", clk_sig),
                                   Port("RST", "in", rst_sig),
                                   Port("EN", "in", en_sig)])
        return component


class VhdlType(object):

    class _VhdlType(object):

        _fields = []

        bit_dvalues = ()
        std_logic_dvalues = ("U", "X", "0", "1", "Z", "W", "L", "H", "-")
        generated = True

        def __str__(self):
            return self.vhdl_type

    class VhdlSigned(_VhdlType):
        vhdl_type = "signed"

        def __init__(self, size):
            self.len = size
            self.vhdl_type = self.vhdl_type + "({} downto 0)"\
                .format(self.len - 1)

    class VhdlUnsigned(_VhdlType):
        vhdl_type = "unsigned"

        def __init__(self, size):
            self.len = size
            self.vhdl_type = self.vhdl_type + "({} downto 0)"\
                .format(self.len - 1)

    class VhdlInteger(_VhdlType):
        vhdl_type = "integer"

    class VhdlString(_VhdlType):
        vhdl_type = "string"

    class VhdlArray(_VhdlType):
        vhdl_type = "array"
        type_def = ""

        def __init__(self, size, itm_type, itm_min, itm_max, type_def=""):
            self.len = size
            self.item_vhdl_type = itm_type
            self.min = itm_min
            self.max = itm_max
            #
            self.type_def = type_def

        def __len__(self):
            return self.len

        @classmethod
        def from_list(cls, itms):
            itms = list(itms)
            size = len(itms)
            item_vhdl_type = itms[0].vhdl_type
            itm_min = min([itm.value for itm in itms])
            itm_max = max([itm.value for itm in itms])
            #
            return cls(size, item_vhdl_type, itm_min, itm_max)

    class VhdlStdLogic(_VhdlType):
        vhdl_type = "std_logic"

        def __init__(self, default=None):
            if default:
                if hasattr(default, "__len__")\
                   and len(default) == 1\
                   and default in self.std_logic_dvalues:
                    self.default = ["'" + ditm + "'" for ditm in default]
                else:
                    raise ValueError
            else:
                self.default = None

    class VhdlStdLogicVector(_VhdlType):
        vhdl_type = "std_logic_vector"

        def __init__(self, size, default=None):
            if size > 1:
                self.len = size
            else:
                raise ValueError

            # update vhdl_type to include (self.len-1 downto 0)
            self.vhdl_type = self.vhdl_type + "({} downto 0)"\
                .format(self.len - 1)

            if default:
                temp_default = list(default)

                # check if every item in default is a valid std_logic value
                val_checked = all([ditm in self.std_logic_dvalues for ditm in temp_default])

                if val_checked is True:
                    if len(temp_default) == self.len\
                       or len(temp_default) == 1:
                        self.default = temp_default
                    else:
                        error_msg = "Length of default = {0}; should be {1} or {2}".format(len(temp_default), 1, self.len)
                        raise ValueError(error_msg)
                else:
                    error_msg = "Values of default not in std_logic_dvalues"
                    raise ValueError(error_msg)
            else:
                self.default = None

        def __len__(self):
            return self.len
