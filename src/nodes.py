"""Nodes."""
import collections
import logging
import new
import os
from collections import namedtuple

from dotgen import VhdlDotGenVisitor
from types import VhdlType
from utils import CONFIG
from utils import TransformationError
from .vhdl_ctree.nodes import CtreeNode
from .vhdl_ctree.nodes import Project
from .vhdl_ctree.nodes import File
from .vhdl_ctree.c.nodes import Op

# set up module-level logger
logger = logging.getLogger(__name__)
logger.disabled = CONFIG.getboolean("logging", "DISABLE_LOGGING")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

VhdlLibrary = namedtuple("VhdlLibrary", ["mainlib_name", "sublib"])
PortInfo = namedtuple("PortInfo", ("name", "direction", "vhdl_type"))
GenericInfo = namedtuple("GenericInfo", ("name", "vhdl_type"))


class VhdlTreeNode(CtreeNode):
    """Base class for all Vhdl AST nodes in sejits_ctree."""

    def __init__(self):
        """Initialize a new AST Node."""
        super(VhdlTreeNode, self).__init__()

    def __str__(self):
        return self.__class__.__name__

    def to_dot(self):
        """Retrieve the AST in DOT format for visualization."""
        return "digraph mytree {\n%s}" % self._to_dot()

    def _to_dot(self):
        """Retrieve the AST in DOT format for vizualization."""
        return VhdlDotGenVisitor().visit(self)

    def lift(self, **kwargs):
        for key, val in kwargs.items():
            attr = "_lift_%s" % key
            setattr(self, attr, getattr(self, attr, []) + val)
            type(self)._fields.append(attr)


class VhdlBaseNode(VhdlTreeNode):
    """Base class for all VHDL nodes in sejits_ctree."""
    d = 0
    dprev = 0
    prev = []

    def codegen(self, indent=4):
        """
        Generate Vhdl code of node.

        :param indent: number of spaces per indentation level (Default = 0)
        :return: string with source code of node
        :rtype: str
        """
        from codegen import VhdlCodegen
        return VhdlCodegen(indent).visit(self)

    def label(self):
        """ Return node label for dot file.

        :return: string describing dot label of node
        :rtype: str
        """
        from dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)


class VhdlSignal(object):
    def __init__(self, name, vhdl_type=None):
        self.name = name
        self.vhdl_type = vhdl_type

    def __str__(self):
        return self.name


class VhdlSymbol(VhdlSignal, VhdlBaseNode):
    """Base class for vhdl symbols."""
    _fields = ["name", "vhdl_type"]


class VhdlNode(VhdlBaseNode):
    """Base class for vhdl node."""

    _fields = ["prev"]

    def __init__(self, prev, in_port=None, inport_info=None, out_port=None, outport_info=None):
        """Initialize VhdlNode node.

        :param prev: list of previous nodes in DAG
        :param in_port: list of input signals
        :param inport_info: list of tuples describing port name,
            direction and vhdl type ("PORTNAME", "direction", VhdlType) or
            generic name and vhdl type ("GENERICNAME", VhdlType)
        :param out_port: list of output signals
        :param outport_info: list of tuples describing port name,
            direction and vhdl type("PORTNAME", "direction", VhdlType)
        """
        self.prev = prev if prev is not None else []
        self.in_port = in_port if in_port is not None else []
        self.out_port = out_port if out_port is not None else []
        # save in/outport information, initialize generic_info
        self.generic_info = []
        self.inport_info = inport_info if inport_info is not None else []
        self.outport_info = outport_info if outport_info is not None else []
        # initialize generic list
        self.generic = []
        #
        super(VhdlNode, self).__init__()

    def finalize_ports(self):
        raise NotImplementedError()


class VhdlSignalCollection(collections.MutableSequence, VhdlSignal):
    """Base class for signal collections."""

    def __init__(self, *args):
        super(VhdlSignalCollection, self).__init__("", None)
        #
        self.list = list()
        for arg in args:
            if hasattr(arg, "__iter__"):
                self.extend(arg)
            else:
                self.append(arg)

    def check(self, arg):
        raise NotImplementedError()

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        self.check(v)
        self.list[i] = v

    def insert(self, i, v):
        self.check(v)
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)


class VhdlAnd(VhdlSignalCollection):
    """Bool signal connection AND."""

    def __init__(self, *args):
        super(VhdlAnd, self).__init__(*args)

    def check(self, v):
        if self.vhdl_type is None:
            self.vhdl_type = v.vhdl_type
        else:
            if self.vhdl_type != v.vhdl_type:
                error_msg = "All types of AND must be equal"
                raise TransformationError(error_msg)

    def __str__(self):
        return " AND ".join([str(i) for i in self])


class VhdlAssignment(VhdlBaseNode):
    def __init__(self, target_signal, source_signal):
        super(VhdlAssignment, self).__init__()
        self.target = target_signal
        self.source = source_signal


class VhdlSource(VhdlSymbol):
    """Base class for kernel source signal."""

    def __init__(self, name="", vhdl_type=None):
        super(VhdlSource, self).__init__(name, vhdl_type)


class VhdlSink(VhdlSymbol):
    """Base class for kernel sink signal."""

    def __init__(self, name="", vhdl_type=None):
        super(VhdlSink, self).__init__(name, vhdl_type)


class VhdlConstant(VhdlSymbol):
    """Base class for vhdl constant."""

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type=None, value=None):
        if name == "":
            super(VhdlConstant, self).__init__(str(value), vhdl_type)
        else:
            super(VhdlConstant, self).__init__(name, vhdl_type)
        self.value = value

    def __str__(self):
        return str(self.value)

Port = namedtuple("Port", ["name", "direction", "vhdl_type", "value"])
Generic = namedtuple("Generic", ["name", "vhdl_type", "value"])


class VhdlModule(VhdlNode):
    """Base class for vhdl module."""

    _fields = ["entity", "architecture"]

    def __init__(self, name="", libraries=None, inport_slice=None, entity=None, architecture=None):
        """Initialize VhdlModule node.

        :param name: str containing name of module
        :param libraries: list containing library objects
        :param entity: list containing VhdlSource nodes, describing kernel
            parameter_process_params
        :param architecture: list containing vhdl nodes, describing body of
            architecture
        """
        if inport_slice:
            # check if input slice is slice object
            if type(inport_slice) is not slice:
                raise TransformationError("inport slice must be slice not of type{}".format(type(inport_slice)))

            in_port_info = [PortInfo(port.name, "in", port.vhdl_type) for port in entity[inport_slice]]
            in_port = entity[inport_slice]
            #
            out_port_info = [PortInfo(port.name, "out", port.vhdl_type) for port in entity[inport_slice.stop:]]
            out_port = entity[inport_slice.stop:]
        else:
            in_port_info = [PortInfo(port.name, "in", port.vhdl_type) for port in entity[:-1]]
            in_port = entity[:-1]
            #
            out_port_info = [PortInfo(port.name, "out", port.vhdl_type) for port in entity[-1:]]
            out_port = entity[-1:]

        super(VhdlModule, self).__init__([], in_port, in_port_info, out_port, out_port_info)
        self.name = name
        self.libraries = libraries
        self.entity = entity
        self.architecture = architecture

    def label(self):
        from dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)

    def finalize_ports(self):
        self.generic = [Generic(*i, value=g) for i, g in zip(self.generic_info, self.generic)]
        self.in_port = [Port(*i, value=g) for i, g in zip(self.inport_info, self.in_port)]
        self.out_port = [Port(*i, value=g) for i, g in zip(self.outport_info, self.out_port)]


class VhdlBinaryOp(VhdlNode):
    """Vhdl BinaryOp node class."""

    _fields = ["prev"]

    def __init__(self, prev=None, in_port=None, op=None, out_port=None):
        """Initialize VhdlBinaryOp node.

        :param prev: list of previous nodes in DAG
        :param in_port: list of input signals
        :param op: Op object describing binary operation
        :param out_port: list of output signals

        :raises TransformationError: raised if type of op is not supported
        """
        in_port_info = [PortInfo("LEFT", "in", VhdlType.VhdlStdLogicVector(8)),
                        PortInfo("RIGHT", "in", VhdlType.VhdlStdLogicVector(8))]
        out_port_info = [PortInfo("BINOP_OUT", "out", VhdlType.VhdlStdLogicVector(8))]

        super(VhdlBinaryOp, self).__init__(prev, in_port, in_port_info, out_port, out_port_info)
        self.library = "work.BasicArith"
        # operation decoder with (Operation ID, Delay)
        op_decoder = {Op.Add: (0, 4),
                      Op.Sub: (1, 4),
                      Op.Mul: (2, 5)}

        if type(op) in op_decoder:
            self.op, self.d = op_decoder[type(op)]
            self.generic_info = [("OP", VhdlType.VhdlInteger())]
            self.generic = [VhdlConstant("", VhdlType.VhdlInteger(), self.op)]
        else:
            raise TransformationError("Unsupported binary operation %s" % op)

    def finalize_ports(self):
        self.generic = [Generic(*i, value=g) for i, g in zip(self.generic_info, self.generic)]
        self.in_port = [Port(*i, value=g) for i, g in zip(self.inport_info, self.in_port)]
        self.out_port = [Port(*i, value=g) for i, g in zip(self.outport_info, self.out_port)]


class VhdlReturn(VhdlNode):
    """Vhdl Return node class."""

    _fields = ["prev"]

    def __init__(self, prev=None, in_port=None, out_port=None):
        """Initialize VhdlReturn node.

        :param prev: list of previous nodes in DAG
        :param in_port: list of input signals
        :param out_port: list of output signals

        :raises TransformationError: raised if len(in_port)
            and/or len(out_port) != 1
        """
        if len(in_port) != 1 or len(out_port) != 1:
            error_msg = "VhdlReturn node supports only 1 in- and output"
            raise TransformationError(error_msg)

        in_port_info = [PortInfo("RETURN_IN", "in", in_port[0].vhdl_type)]
        out_port_info = [PortInfo("RETURN_OUT", "out", out_port[0].vhdl_type)]

        super(VhdlReturn, self).__init__(prev, in_port, in_port_info, out_port, out_port_info)
        self.d = 0

    def finalize_ports(self):
        self.in_port = [Port(*i, value=g) for i, g in zip(self.inport_info, self.in_port)]
        self.out_port = [Port(*i, value=g) for i, g in zip(self.outport_info, self.out_port)]


class VhdlComponent(VhdlNode):
    """Vhdl Component node class."""

    _fields = ["prev"]

    def __init__(self, name=None, prev=None, generic_slice=None, delay=-1, in_port=None, inport_info=None,
                 out_port=None, outport_info=None, library=None):
        """Initialize VhdlComponent node.

        :param prev: list of previous nodes in DAG
        :param generic_slice: slice object to slice in_port into
            generic ports and ordinary input ports
        :param delay: int describing delay of node in clock cycles
        :param in_port: list of input signals
        :param inport_info: list of tuples describing port name and
            direction ("PORTNAME", "direction") or
            generic name and vhdl type ("GENERICNAME", VhdlType)
        :param out_port: list of output signals
        :param outport_info: list of tuples describing port name and
            direction -> [("PORTNAME", "direction"), ...]

        :raises TransformationError: raised if delay is not >= 0
        """
        self.name = name if name is not None else ""
        self.generic_slice = generic_slice
        super(VhdlComponent, self).__init__(prev, in_port, inport_info, out_port, outport_info)
        self.library = library if library is not None else ""

        if delay >= 0:
            self.d = delay
        else:
            error_msg = "Delay of Component must be >= 0"
            raise TransformationError(error_msg)
        self.ports_finalized = False

    def finalize_ports(self):
        if not self.ports_finalized:
            if self.generic_slice:
                self.generic = self.in_port[self.generic_slice]
                self.in_port = self.in_port[self.generic_slice.stop:]
                self.generic_info = self.inport_info[self.generic_slice]
                self.inport_info = self.inport_info[self.generic_slice.stop:]
                #
            self.generic = [Generic(*i, value=g) for i, g in zip(self.generic_info, self.generic)]
            self.in_port = [Port(*i, value=g) for i, g in zip(self.inport_info, self.in_port)]
            self.out_port = [Port(*i, value=g) for i, g in zip(self.outport_info, self.out_port)]
            #
            self.ports_finalized = True
        else:
            pass


class VhdlDReg(VhdlNode):
    """Vhdl D-Register node class."""

    _fields = ["prev"]

    def __init__(self, prev=None, delay=-1, in_port=None, out_port=None):
        """Initialize VhdlDReg node.

        :param prev: list of previous nodes in DAG
        :param delay: int describing delay of node in clock cycles
        :param in_port: list of input signals
        :param out_port: list of output signals

        :raises TransformationError: raised if len(in_port)
            and/or len(out_port) != 1
        :raises TransformationError: raised if delay is not >= 0
        """
        inport_info = [PortInfo("DREG_IN", "in", in_port[0].vhdl_type)]
        outport_info = [PortInfo("DREG_OUT", "out", in_port[0].vhdl_type)]

        super(VhdlDReg, self).__init__(prev,
                                       in_port,
                                       inport_info,
                                       out_port,
                                       outport_info)
        self.library = "work.DReg"

        if delay > 1:
            self.d = delay
        else:
            error_msg = "Delay of Component must be >= 1"
            raise TransformationError(error_msg)

    def finalize_ports(self):
        #
        self.generic_info = [("WIDTH", VhdlType.VhdlPositive()),
                             ("LENGTH", VhdlType.VhdlPositive())]
        self.generic = [VhdlConstant("", VhdlType.VhdlPositive(),
                                     len(self.in_port[0].vhdl_type)),
                        VhdlConstant("", VhdlType.VhdlPositive(),
                                     self.d)]
        #
        self.generic = [Generic(*i, value=g)
                        for i, g in zip(self.generic_info, self.generic)]
        self.in_port = [Port(*i, value=g)
                        for i, g in zip(self.inport_info, self.in_port)]
        self.out_port = [Port(*i, value=g)
                         for i, g in zip(self.outport_info, self.out_port)]


class VhdlFile(VhdlBaseNode, File):
    """Vhdl File Class representing one vhdl source file."""

    _ext = "vhd"
    file_path = ""

    def __init__(self, name="generated", body=None, path=""):
        """Initialize Vhdl File."""
        self._filepath = None
        #
        VhdlBaseNode.__init__(self)
        File.__init__(self, name, body, path)

    @property
    def file_path(self):
        """Return path of source file."""
        return self._filepath

    @file_path.setter
    def file_path(self, value):
        """Set and create file path."""
        self._filepath = value
        if not os.path.exists(self._filepath):
            os.makedirs(self._filepath)

    def get_filename(self):
        """Return file name with file extensions."""
        return "%s.%s" % (self.name, self._ext)

    def _compile(self, program_text):
        """
        Write program_text to file.

        !!!Changed in prebuilt instances!!!.
        """
        vhdl_src_file = os.path.join(self.path, self.get_filename())
        with open(vhdl_src_file, 'w') as vhdl_file:
            vhdl_file.write(program_text)
        logger.info("file for generated VHDL: %s", vhdl_src_file)
        logger.info("generated VHDL program: (((\n%s\n)))", program_text)
        return vhdl_src_file

    def codegen(self, indent=4):
        """Run code generation of file."""
        from codegen import VhdlCodegen
        return VhdlCodegen(indent).visit(self)

    @classmethod
    def from_prebuilt(cls, name="prebuilt", path=""):
        """Generate Vhdl File from prebuilt source file."""
        vhdlfile = VhdlFile(name, body=[], path="")
        vhdlfile.file_path = path

        #
        def _compile(self, program_text):
            _ = program_text
            return self.file_path

        vhdlfile._compile = new.instancemethod(_compile, vhdlfile, None)
        #
        return vhdlfile

    def component(self):
        """Return VhdlComponent class for file."""
        # TODO: Check architecture for only 1 component tree
        # TODO: Create Component from that component tree element
        comp = VhdlComponent(name=self.name,
                             delay=self.body[0].architecture[0].dprev,
                             inport_info=self.body[0].inport_info,
                             outport_info=self.body[0].outport_info)
        return comp


class VhdlProject(Project):
    """VhdlProject class representing one vhdl project."""

    def __init__(self, files=None, indent=4, synthesis_dir="", gen_wrapper=True):
        """Initialize VhdlProject."""
        self.files = files if files else []
        self.synthesis_dir = synthesis_dir
        self.indent = indent
        self.gen_wrapper = gen_wrapper  # generate wrapper
        #
        self._module = None
        #
        super(VhdlProject, self).__init__(self.files, self.indent, self.synthesis_dir)

    def codegen(self):
        """Generate vhdl code of wrapper and files in project."""
        from jit_synth import VhdlSynthModule
        self._module = VhdlSynthModule()

        if self.gen_wrapper is True:
            self.files.append(self._generate_wrapper())

        for f in self.files:
            submodule = f._compile(f.codegen(self.indent))
            if submodule:
                self._module._link_in(submodule)
        return self._module

    @property
    def module(self):
        """Return JIT module if available else create it."""
        if self._module:
            return self._module
        return self.codegen()
