""" Nodes contains all vhdl nodes """
__author__ = "philipp ebensberger"

import os
import ast
import logging

from sejits_ctree.vhdl import STDLIBS
from sejits_ctree.vhdl import TransformationError
from collections import defaultdict, namedtuple
from sejits_ctree.vhdl.dotgen import VhdlDotGenVisitor
from ctree.nodes import File, Project, CtreeNode
from ctree.c.nodes import Op
from sejits_ctree.vhdl.utils import CONFIG


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
        from sejits_ctree.vhdl.codegen import VhdlCodegen
        return VhdlCodegen(indent).visit(self)

    def label(self):
        """ Return node label for dot file.

        :return: string describing dot label of node
        :rtype: str
        """
        from dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)


Interface = namedtuple("Interface", ["iports", "oport"])


class VhdlFile(VhdlBaseNode, File):

    _ext = "vhd"
    generated = True
    file_path = ""

    def __init__(self, name="generated", body=[], path=""):
        VhdlBaseNode.__init__(self)
        File.__init__(self, name, body, path)

    @property
    def file_path(self):
        return self._filepath

    @file_path.setter
    def file_path(self, value):
        self._filepath = value
        if not os.path.exists(self._filepath):
            os.makedirs(self._filepath)

    def get_filename(self):
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
        from sejits_ctree.vhdl.codegen import VhdlCodegen
        return VhdlCodegen(indent).visit(self)

    @classmethod
    def fromPrebuilt(cls, name="prebuilt", path=""):
        vhdlfile = VhdlFile(name, [], "")
        vhdlfile.generated = False
        vhdlfile.file_path = path
        return vhdlfile

    def component(self):
        comp = VhdlComponent(name=self.name,
                             delay=self.body[0].architecture.dprev,
                             inport_info=self.body[0].inport_info,
                             outport_info=self.body[0].outport_info)
        return comp


class VhdlProject(Project):

    def __init__(self, files=None, indent=4, synthesis_dir=""):
        self.files = files if files else []
        self.synthesis_dir = synthesis_dir
        self.indent = indent

    def codegen(self):
        from sejits_ctree.vhdl.jit_synth import VhdlSynthModule
        self._module = VhdlSynthModule()

        self.files.append(self._generate_wrapper())

        for f in self.files:
            submodule = f._compile(f.codegen(self.indent))
            if submodule:
                self._module._link_in(submodule)
        return self._module

    def _generate_wrapper(self):
        logger.info("Generate project wrapper")

        AXI_STREAM_WIDTH = 32
        # input signals
        m_axis_mm2s_tdata = VhdlSignal("m_axis_mm2s_tdata",
                                       VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
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
        s_axis_s2mm_tdata = VhdlSignal("s_axis_s2mm_tdata",
                                   VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
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
        component.in_port = [m_axis_mm2s_tdata]

        ret_sig = VhdlSignal("ret_tdata", VhdlType.VhdlStdLogicVector(8, "0"))
        component.out_port = [ret_sig]
        #
        ret_component = VhdlReturn([component], [ret_sig], [out_sigs[0]])

        libraries = [VhdlLibrary("ieee",["ieee.std_logic_1164.all"]),
                     VhdlLibrary(None,["work.the_filter_package.all"])]
        #
        inport_slice = slice(0, len(in_sigs))
        params = in_sigs + out_sigs
        module = VhdlModule("accel_wrapper", libraries, inport_slice, params, ret_component)
        return VhdlFile("accel_wrapper", [module])

    @property
    def module(self):
        if self._module:
            return self._module
        return self.codegen(indent=self.indent)


class VhdlProject1(object):

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
        from jit_synth import VhdlSynthModule, VhdlSyntData

        # ---------------------------------------------------------------------
        # LOGGING
        # ---------------------------------------------------------------------
        logger.info("Start codegen of VhdlProject")
        # ---------------------------------------------------------------------

        self._module = VhdlSynthModule()

        wrapper_file = self.generate_wrapper(self.files[0])
        self.files = [wrapper_file] + self.files

        # process vhdl-files in project
        temp_submodules = []
        if len(self.files) > 0:
            for vhdl_file in self.files:
                temp_submodules += vhdl_file.codegen(indent)
            synth_data = VhdlSyntData(self.files[0], set(temp_submodules))

            # return VhdlSynthModule with linked VhdlSyntData
            self._module._link_in(synth_data)
            return self._module
        else:
            raise Exception()

    def generate_wrapper(self, gen_top_file):
        # ---------------------------------------------------------------------
        # LOGGING
        # ---------------------------------------------------------------------
        logger.info("Generate project wrapper")
        # ---------------------------------------------------------------------

        AXI_STREAM_WIDTH = 32

        # input signals
        m_axis_mm2s_tdata = VhdlSignal("m_axis_mm2s_tdata",
                                       VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
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
        s_axis_s2mm_tdata = VhdlSignal("s_axis_s2mm_tdata",
                                   VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
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

        # input/ output ports
        in_ports = [Port(sig.name, "in", sig) for sig in in_sigs]
        out_ports = [Port(sig.name, "out", sig) for sig in out_sigs]

        wrappee_comp = gen_top_file.component
        wrappee_comp.in_ports[3].value = m_axis_mm2s_tdata

        ret_sig = VhdlSignal("ret_tdata", VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
        wrappee_comp.out_ports[0].value = ret_sig

        out_ports[0].value = ret_sig
        for o_port,osig in zip(out_ports[1:], in_sigs[1:]):
            o_port.value = osig

        entity = Entity(name="project_wrapper",
                        generics=[],
                        in_ports=in_ports,
                        out_ports=out_ports)

        arch = Architecture(entity_name="project_wrapper",
                            architecture_name="behaviour",
                            signals=[],
                            components=[wrappee_comp])
        # =============================================================== #
        # Initialize Base Class
        # =============================================================== #
        path = "/home/philipp/University/M4/Masterthesis/src/git_repo/" + \
               "ebensberger_ma/sejits_ctree/vhdl/vivado/tmp_vhdl_files"
        return VhdlFile(name="project_wrapper",
                        libs=None,
                        entity=entity,
                        architecture=arch,
                        config_target="vhd",
                        path=path,
                        dependencies=[])

# =============================================================================
# COMPONENT NODE CLASSES
# =============================================================================

VhdlLibrary = namedtuple("VhdlLibrary", ["mainlib_name", "sublib"])


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
                self.default = "'0'"

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
                        error_msg = "Length of default = {0}; " + \
                                    "should be {1} or {2}".format(len(temp_default), 1, self.len)
                        raise ValueError(error_msg)
                else:
                    error_msg = "Values of default not in std_logic_dvalues"
                    raise ValueError(error_msg)
            else:
                self.default = "'" + "0" * self.len + "'"

        def __len__(self):
            return self.len


class VhdlSymbol(VhdlBaseNode):
    """Base class for vhdl symbols."""

    d = 0
    dprev = 0


class VhdlNode(VhdlBaseNode):
    """Base class for vhdl node."""

    _fields = ["prev"]

    def __init__(self, prev=[], in_port=[], inport_info=None, out_port=[],
                 outport_info=None):
        """Initialize VhdlNode node.

        :param prev: list of previous nodes in DAG
        :param in_port: list of input signals
        :param inport_info: list of tuples describing port name and
            direction ("PORTNAME", "direction") or
            generic name and vhdl type ("GENERICNAME", VhdlType)
        :param out_port: list of output signals
        :param outport_info: list of tuples describing port name and
            direction ("PORTNAME", "direction")
        """
        self.prev = prev
        self.in_port = in_port
        self.out_port = out_port
        # initalize delay and cumulative previous delay
        self.d = -1
        self.dprev = -1
        # save in/outport information, initialize generic_info
        self.generic_info = []
        self.inport_info = inport_info
        self.outport_info = outport_info
        # initialize generic list
        self.generic = []


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


class Port(VhdlSymbol):
    """Base class of Vhld Port item."""

    _fields = ["name", "direction", "value"]

    def __init__(self, name="", direction="", value=None):
        """ Initialize name, direction and value of Port. """
        self.name = name
        self.direction = direction
        self.value = value


class Generic(VhdlSymbol):
    """Base class of Vhdl Generic item."""

    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type=None, value=None):
        """ Initialize name and value of Generic. """
        self.name = name
        self.vhdl_type = vhdl_type
        self.value = value



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
            in_port_info = [(port.name, "in") for port in entity[inport_slice]]
            in_port = entity[inport_slice]
            #
            out_port_info = [(port.name, "out") for port in entity[inport_slice.stop:]]
            out_port = entity[inport_slice.stop:]
        else:
            in_port_info = [(port.name, "in") for port in entity[:-1]]
            in_port = entity[:-1]
            #
            out_port_info = [(port.name, "out") for port in entity[-1:]]
            out_port = entity[-1:]

        super(VhdlModule, self).__init__([],
                                         in_port,
                                         in_port_info,
                                         out_port,
                                         out_port_info)
        self.name = name
        self.libraries = libraries
        self.entity = entity
        self.architecture = architecture

    def label(self):

        from sejits_ctree.vhdl.dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)


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
        in_port_info = [("LEFT", "in"), ("RIGHT", "in")]
        out_port_info = [("BINOP_OUT", "out")]

        super(VhdlBinaryOp, self).__init__(prev,
                                           in_port,
                                           in_port_info,
                                           out_port,
                                           out_port_info)

        # operation decoder with (Operation ID, Delay)
        op_decoder = {Op.Add:(0, 4),
                      Op.Sub:(1, 4),
                      Op.Mul:(2, 5)}

        if type(op) in op_decoder:
            self.op, self.d = op_decoder[type(op)]
            self.generic_info = [("OP", VhdlType.VhdlInteger)]
            self.generic = [self.op]
        else:
            raise TransformationError("Unsupported binary operation %s" % op)


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

        in_port_info = [("RETURN_IN", "in")]
        out_port_info = [("RETURN_OUT", "out")]

        super(VhdlReturn, self).__init__(prev,
                                         in_port,
                                         in_port_info,
                                         out_port,
                                         out_port_info)
        self.d = 0


class VhdlComponent(VhdlNode):
    """Vhdl Component node class."""

    _fields = ["prev"]

    def __init__(self, name="", prev=[], generic_slice=None, delay=-1, in_port=[],
                 inport_info=None, out_port=[], outport_info=None):
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
        self.name = name
        super(VhdlComponent, self).__init__(prev,
                                            in_port,
                                            inport_info,
                                            out_port,
                                            outport_info)

        if generic_slice:
            self.generic = in_port[generic_slice]
            self.generic_info = inport_info[generic_slice]
            #
            self.in_port = in_port[generic_slice.stop:]
            self.inport_info = inport_info[generic_slice.stop:]

        if delay >= 0:
            self.d = delay
        else:
            error_msg = "Delay of Component must be >= 0"
            raise TransformationError(error_msg)


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
        inport_info = [("DREG_IN", "in")]
        outport_info = [("DREG_OUT", "out")]

        super(VhdlDReg, self).__init__(prev,
                                       in_port,
                                       inport_info,
                                       out_port,
                                       outport_info)
        if delay >= 0:
            self.d = delay
        else:
            error_msg = "Delay of Component must be >= 0"
            raise TransformationError(error_msg)
