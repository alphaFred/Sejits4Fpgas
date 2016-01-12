""" DAG nodes for VHDL constructs. """
__author__ = 'philipp ebensberger'

import os
import logging
# set up module-level logger
log = logging.getLogger(__name__)

from collections import defaultdict, namedtuple
from sejits_ctree.vhdl import STDLIBS
from sejits_ctree.util import singleton
from sejits_ctree.nodes import VhdlTreeNode, File

from subprocess import call


class VhdlNode(VhdlTreeNode):

    """Base class for all VHDL nodes in sejits_ctree."""

    def codegen(self, indent=0):
        """
        Generate Vhdl code of node.

        Attributes:
            indent: number of spaces per indentation level (Default = 0)
        Return:
            string with source code of node
        """
        from sejits_ctree.vhdl.codegen import VhdlCodeGen
        return VhdlCodeGen(indent).visit(self)

    def label(self):
        """ Return node label for dot file. """
        from sejits_ctree.vhdl.dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)


Interface = namedtuple("Interface", ["iports", "oport"])


class VhdlFile(VhdlNode, File):

    """Represents a .vhd file."""

    _ext = "vhd"
    codegenflag = "generated"

    def __init__(self, name="generated", libs=None,
                 entity=None, architecture=None, path=None):
        """ Initialize VhdlFile. """
        VhdlNode.__init__(self)
        # body = entity, archs
        File.__init__(self, name, [entity, architecture], path)
        #
        self._interface = Interface(entity.in_ports, entity.out_port)
        #
        self.libs = STDLIBS + libs if libs else STDLIBS

    @property
    def interface(self):
        return self._interface

    def codegen(self, indent=0):
        """ Generate vhdl descriptioin of VhdlFile if it is generated. """
        if self.codegenflag == "generated":
            from sejits_ctree.vhdl.codegen import VhdlCodeGen
            return VhdlCodeGen(indent).visit(self)
        else:
            return ""

    def _compile(self, program_text):
        pass


class VhdlProject(object):

    """ Base class for an Vhdl Project. """

    def __init__(self, files=None, synthesis_dir=""):
        """ Initialize VhdlProject. """
        self.files = files if files else []
        self.synthesis_dir = synthesis_dir

    def codegen(self, indent=0):
        """ Generate vhdl descriptions for all vhdl files in project. """
        if not os.path.exists(self.synthesis_dir):
            os.makedirs(self.synthesis_dir)
        for vhdl_file in self.files:
            if vhdl_file.codegenflag == "generated":
                # generate file name
                fname = self.synthesis_dir + vhdl_file.get_filename()
                # save generated vhdl file
                with open(fname, "w") as output_file:
                    output_file.write(vhdl_file.codegen(indent=indent))
            else:
                # move imported file to synthesis directory
                call(["cp", vhdl_file.path, self.synthesis_dir])

    def synthesize(self):
        """ Integrate VhdlFiles and synthesise VhdlProject. """
        pass

# =============================================================================
# COMPONENT NODE CLASSES
# =============================================================================

PORT_DIRECTIONs = ({"in", "out"})
VHDL_TYPEs = ({})


class Statement(VhdlNode):
    """ docstring dummy."""
    pass


class Expression(VhdlNode):
    """ Base class for Expression nodes. """

    # instance counter to generate unique instance names
    _ids = defaultdict(int)

    def out_type(self):
        """ Return node's output type. """
        raise NotImplementedError()


class Literal(VhdlNode):
    """ docstring dummy. """
    pass


# LITERALS

@singleton
class Op(Literal):
    class _Op(object):
        def __str__(self):
            return self._str

    class Add(_Op):
        _str = '"Add"'

    class Mul(_Op):
        _str = "Mul"

    class Sub(_Op):
        _str = "Sub"

    class Div(_Op):
        _str = "Div"


class Signal(Literal):

    """ Node class for Vhdl Signal. """

    _fields = ["name", "vhdl_type", "def_value"]

    def __init__(self, name="", vhdl_type="", def_value=None):
        """ Create a new signal with the given name. """
        if name != "":
            self.name = name
        else:
            raise Exception
        #
        self.vhdl_type = vhdl_type
        #
        if def_value is not None:
            # TODO: check if default value is of type self.vhdl_type
            self.def_value = def_value
        else:
            self.def_value = def_value


class Constant(Literal):

    """ Node class for Vhdl Constant. """

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type="", value=None):
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


class Port(Literal):

    """ Base class of Vhld Port item. """

    _fields = ["name", "direction", "value"]

    def __init__(self, name="", direction="", value=None):
        """ Initialize name, direction and value of Port. """
        self.name = name
        self.direction = direction
        self.value = value


class Generic(Literal):

    """ Base class of Vhdl Generic item. """

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type="", value=None):
        """ Initialize name and value of Generic. """
        self.name = name
        self.vhdl_type = vhdl_type
        self.value = value


class BinaryOp(Expression):

    """ Node class for Vhdl binary operator. """

    _fields = ["left_port", "op", "right_port", "out_port"]
    _op_values = ({"add", "sub", "mul", "div"})
    name = "BinaryOp"

    def __init__(self, left_port=None, op=None, right_port=None,
                 out_port=None):
        """ Initialize BinaryOp node. """
        self.left_port = left_port
        self.right_port = right_port
        self.op = op
        self.out_port = out_port
        # generate unique instance id
        instance_id = self._ids[self.name.lower()]
        self._ids[self.name.lower()] += 1
        # generate unique instance name
        self.instance_name = self.name.lower() +\
            (str(instance_id) if instance_id != 0 else "")

    def out_type(self):
        """ Return node's output type. """
        # TODO: calculate output type based on input types
        return self.left_port.value.vhdl_type


class UnaryOp(Expression):

    """ Node class for Vhdl unary operator. """

    _fields = ["in_port", "op", "out_port"]
    _op_values = ({"sqrt", "pow"})
    name = "UnaryOp"

    def __init__(self, in_port=None, op=None, out_port=None):
        """ Initialize UnaryOp node. """
        self.in_port = in_port
        self.op = op
        self.out_port = out_port
        # generate unique instance id
        instance_id = self._ids[self.name]
        self._ids[self.name] += 1
        # generate unique instance name
        self.instance_name = self.name +\
            (str(instance_id) if instance_id != 0 else "")

    def out_type(self):
        """ Return node's output type. """
        return self.in_port.value.vhdl_type


class Component(Expression):

    """ Node class for generic Vhdl Component. """

    _fields = ["name", "generics", "in_ports", "out_port"]

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
        self.instance_name = self.name +\
            (str(instance_id) if instance_id != 0 else "")

    def out_type(self):
        """ Return node's output type. """
        return self._out_type


class VhdlReturn(Expression):

    """ Special Node class for Vhdl Return node. """

    _fields = ["in_port", "out_port"]
    name = "Return"

    def __init__(self, in_port, out_port):
        """ Initialize VhdlReturn node. """
        self.in_port = in_port
        self.out_port = out_port
        #
        instance_id = self._ids[self.name]
        self._ids[self.name] += 1
        #
        self.instance_name = self.name +\
            (str(instance_id) if instance_id != 0 else "")

    def out_type(self):
        """ Return Vhdl type of input signal. """
        return self.in_port.value.vhdl_type


# STATEMENTS
class Entity(Statement):

    """ Node class for Entity nodes. """

    _fields = ["name", "generics", "in_ports", "out_port"]

    def __init__(self, name, generics, in_ports, out_port):
        """ Initialize Entity generics and port lists. """
        self.name = name

        self.generics = None
        self.in_ports = None
        self.out_port = None

        if generics is not None:
            self.generics = generics if type(generics) is list else [generics]

        if in_ports is not None:
            self.in_ports = in_ports if type(in_ports) is list else [in_ports]

        if out_port is not None:
            self.out_port = out_port


class Architecture(Statement):

    """ Node class for Architecture node. """

    _fields = ["entity_name", "architecture_name", "body"]
    signals = None
    components = None

    def __init__(self, entity_name=None, architecture_name="behaviour",
                 signals=None, body=None, components=None):
        self.body = body if body else []
        self.signals = signals if signals else []
        self.entity_name = entity_name
        self.architecture_name = architecture_name
        self.components = components if components else []
        super(Architecture, self).__init__()
