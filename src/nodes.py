"""Nodes."""
import collections
import logging
import os

import transformations
#
from src.types import VhdlType
from src.utils import TransformationError
from dotgen import VhdlDotGenVisitor
from collections import namedtuple
from utils import CONFIG
#
from ctree.nodes import File, Project, CtreeNode
from ctree.c.nodes import Op


# set up module-level logger
logger = logging.getLogger(__name__)
logger.disabled = CONFIG.getboolean("logging", "ENABLE_LOGGING")
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
Interface = namedtuple("Interface", ["iports", "oport"])
PortInfo = namedtuple("PortInfo", ("name", "direction", "vhdl_type"))


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


class VhdlSymbol(VhdlBaseNode):
    """Base class for vhdl symbols."""

    d = 0
    dprev = 0
    vhdl_type = None

    def __str__(self):
        return self.name


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
        # initalize delay and cumulative previous delay
        self.d = -1
        self.dprev = -1
        # save in/outport information, initialize generic_info
        self.generic_info = []
        self.inport_info = inport_info if inport_info is not None else []
        self.outport_info = outport_info if outport_info is not None else []
        # initialize generic list
        self.generic = []

    def finalize_ports(self):
        pass


class VhdlSignalCollection(collections.MutableSequence, VhdlSymbol):
    """Base class for signal collections."""
    def __init__(self, *args):
        self.list = list()
        self.extend(list(args))

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


class VhdlSignalSplit(VhdlSymbol):
    def __init__(self, sig, sig_slice):
        self.sig = sig
        self.sig_slice = sig_slice
        if hasattr(sig.vhdl_type, "size"):
            self.vhdl_type = sig.vhdl_type.__class__(sig_slice.stop - sig_slice.start)
        else:
            raise TransformationError()


    def __str__(self):
        return self.sig.name + "(" + str(self.sig_slice.stop - 1) + " downto " + str(self.sig_slice.start) + ")"


class VhdlSignalMerge(VhdlSymbol):
    def __init__(self, sig, sig_slice, fill_bitval=""):
        self.sig = sig
        self.sig_slice = sig_slice
        self.fill_bitval = "0" if fill_bitval == "" else fill_bitval

    def __str__(self):
        return "(" + str(self.sig_slice.stop - 1) + " downto " + str(self.sig_slice.start) + " => '" + self.fill_bitval + "') & " + self.sig.name


class VhdlToArray(VhdlSignalCollection):
    def __init__(self, *args):
        super(VhdlAnd, self).__init__(*args)

    def __str__(self):
        return "(" + " & ".join([str(i) for i in self]) + ")"


class VhdlFromArray(VhdlSignalCollection):
    def __init__(self, *args):
        super(VhdlAnd, self).__init__(*args)

    def __str__(self):
        return "(" + " & ".join([str(i) for i in self]) + ")"


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


class VhdlSource(VhdlSymbol):
    """Base class for kernel source signal."""

    _fields = ["name", "vhdl_type"]

    def __init__(self, name="", vhdl_type=None):
        self.name = name
        self.vhdl_type = vhdl_type


class VhdlSink(VhdlSymbol):
    """Base class for kernel sink signal."""

    _fields = ["name", "vhdl_type"]

    def __init__(self, name="", vhdl_type=None):
        self.name = name
        self.vhdl_type = vhdl_type


class VhdlSignal(VhdlSymbol):
    """Base class for vhdl signal."""

    _fields = ["name", "vhdl_type"]

    def __init__(self, name="", vhdl_type=None):
        self.name = name
        self.vhdl_type = vhdl_type


class VhdlConstant(VhdlSymbol):
    """Base class for vhdl constant."""

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type=None, value=None, ):
        if name == "":
            self.name = str(value)
        else:
            self.name = name
        self.vhdl_type = vhdl_type
        self.value = value

    def __str__(self):
        return str(self.value)


class Port(VhdlSymbol):
    """Base class of Vhld Port item."""

    _fields = ["name", "direction", "vhdl_type", "value"]

    def __init__(self, name="", direction="", vhdl_type=None, value=None):
        """ Initialize name, direction and value of Port. """
        self.name = name
        self.direction = direction
        self.vhdl_type = vhdl_type
        self.value = value
        self._type_check()

    def _type_check(self):
        pass


class Generic(VhdlSymbol):
    """Base class of Vhdl Generic item."""

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type=None, value=None):
        """ Initialize name and value of Generic. """
        self.name = name
        self.vhdl_type = vhdl_type
        self.value = value

    def gmap(self):
        if isinstance(self.value, VhdlConstant):
            return self.name + " => " + str(self.value)
        else:
            raise TransformationError("Generic value must be constant")


class VhdlModule(VhdlNode):
    """Base class for vhdl module."""

    _fields = ["entity", "architecture"]

    def __init__(self, name="", libraries=[], inport_slice=None, entity=[], architecture=[]):
        """Initialize VhdlModule node.

        :param name: str containing name of module
        :param libraries: list containing library objects
        :param entity: list containing VhdlSource nodes, describing kernel
            parameter
        :param architecture: list containing vhdl nodes, describing body of
            architecture
        """
        if inport_slice:
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

    def __init__(self, prev=[], in_port=[], op=None, out_port=[]):
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
        op_decoder = {Op.Add:(0, 4),
                      Op.Sub:(1, 4),
                      Op.Mul:(2, 5)}

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

    def __init__(self, prev=[], in_port=[], out_port=[]):
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

        in_port_info = [PortInfo("RETURN_IN", "in", VhdlType.VhdlStdLogicVector(8))]
        out_port_info = [PortInfo("RETURN_OUT", "out", VhdlType.VhdlStdLogicVector(8))]

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

    def finalize_ports(self):
        if self.generic_slice:
            self.generic = self.in_port[self.generic_slice]
            self.in_port = self.in_port[self.generic_slice.stop:]
            self.generic_info = self.inport_info[self.generic_slice]
            self.inport_info = self.inport_info[self.generic_slice.stop:]
            #
        self.generic = [Generic(*i, value=g) for i, g in zip(self.generic_info, self.generic)]
        self.in_port = [Port(*i, value=g) for i, g in zip(self.inport_info, self.in_port)]
        self.out_port = [Port(*i, value=g) for i, g in zip(self.outport_info, self.out_port)]


class VhdlDReg(VhdlNode):
    """Vhdl D-Register node class."""

    _fields = ["prev"]

    def __init__(self, prev=[], delay=-1, in_port=[], out_port=[]):
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
    generated = True
    file_path = ""

    def __init__(self, name="generated", body=[], path=""):
        """Initialize Vhdl File."""
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
        if not self.generated:
            return self.file_path
        else:
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
        vhdlfile = VhdlFile(name, body=[],path= "")
        vhdlfile.generated = False
        vhdlfile.file_path = path
        return vhdlfile

    def component(self):
        """Return VhdlComponent class for file."""
        comp = VhdlComponent(name=self.name,
                             delay=self.body[0].architecture.dprev,
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
        self.gen_wrapper = gen_wrapper

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

    def _generate_wrapper(self):
        logger.info("Generate project wrapper")
        axi_stream_width = 32
        # input signals
        m_axis_mm2s_tdata = VhdlSource("m_axis_mm2s_tdata",
                                       VhdlType.VhdlStdLogicVector(
                                           axi_stream_width,
                                           "0"))
        m_axis_mm2s_tkeep = VhdlSignal("m_axis_mm2s_tkeep",
                                       VhdlType.VhdlStdLogicVector(4, "0"))
        m_axis_mm2s_tlast = VhdlSignal("m_axis_mm2s_tlast",
                                       VhdlType.VhdlStdLogic("0"))
        m_axis_mm2s_tready = VhdlSignal("m_axis_mm2s_tready",
                                        VhdlType.VhdlStdLogic("0"))
        m_axis_mm2s_tvalid = VhdlSignal("m_axis_mm2s_tvalid",
                                        VhdlType.VhdlStdLogic("0"))
        in_sigs = [m_axis_mm2s_tdata, m_axis_mm2s_tkeep, m_axis_mm2s_tlast,
                   m_axis_mm2s_tready, m_axis_mm2s_tvalid]

        # output signals
        s_axis_s2mm_tdata = VhdlSink("s_axis_s2mm_tdata",
                                     VhdlType.VhdlStdLogicVector(
                                         axi_stream_width,
                                         "0"))
        s_axis_s2mm_tkeep = VhdlSignal("s_axis_s2mm_tkeep",
                                       VhdlType.VhdlStdLogicVector(4, "0"))
        s_axis_s2mm_tlast = VhdlSignal("s_axis_s2mm_tlast",
                                       VhdlType.VhdlStdLogic("0"))
        s_axis_s2mm_tready = VhdlSignal("s_axis_s2mm_tready",
                                        VhdlType.VhdlStdLogic("0"))
        s_axis_s2mm_tvalid = VhdlSignal("s_axis_s2mm_tvalid",
                                        VhdlType.VhdlStdLogic("0"))
        out_sigs = [s_axis_s2mm_tdata, s_axis_s2mm_tkeep,
                    s_axis_s2mm_tlast, s_axis_s2mm_tready,
                    s_axis_s2mm_tvalid]

        component = self.files[0].component()
        component.delay = 5
        component.library = "work.apply"
        component.prev = [m_axis_mm2s_tdata]
        component.in_port = [VhdlSignalSplit(m_axis_mm2s_tdata, slice(0, 8))]

        ret_sig = VhdlSignal("ret_tdata", component.outport_info[0].vhdl_type)
        component.out_port = [ret_sig]
        #
        ret_component = VhdlReturn([component], [VhdlSignalMerge(ret_sig, slice(8, 32), "0")], [out_sigs[0]])

        libraries = [VhdlLibrary("ieee", ["ieee.std_logic_1164.all",
                                          "ieee.numeric_std.all"]),
                     VhdlLibrary(None, ["work.the_filter_package.all"])]
        #
        inport_slice = slice(0, len(in_sigs))
        params = in_sigs + out_sigs
        module = VhdlModule("accel_wrapper",
                            libraries,
                            inport_slice,
                            params,
                            ret_component)
        #
        transformations.VhdlGraphTransformer().visit(module)
        transformations.VhdlPortTransformer().visit(module)
        return VhdlFile("accel_wrapper", [module])

    @property
    def module(self):
        """Return JIT module if available else create it."""
        if self._module:
            return self._module
        return self.codegen(indent=self.indent)
