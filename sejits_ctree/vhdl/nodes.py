""" Nodes contains all vhdl nodes """
__author__ = "philipp ebensberger"

import os
import ast
import logging

from sejits_ctree.vhdl import STDLIBS
from sejits_ctree.vhdl import TransformationError, VhdlNodeError, VhdlTypeError
from collections import defaultdict, namedtuple
from sejits_ctree.vhdl.dotgen import VhdlDotGenVisitor
from sejits_ctree.nodes import File
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


class VhdlTreeNode(ast.AST):

    """ Base class for all Vhdl AST nodes in sejits_ctree."""

    def __init__(self):
        """Initialize a new AST Node."""
        super(VhdlTreeNode, self).__init__()

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


class VhdlFile(VhdlNode):

    """Represents a .vhd file."""

    _ext = "vhd"
    _fields = ['body']
    generated = True
    dependencies = []
    delay = 0

    def __init__(self, name="generated", libs=None, entity=None,
                 architecture=None, config_target="vhd", path=None,
                 dependencies=[]):
        """ Initialize VhdlFile. """
        VhdlNode.__init__(self)
        self.name = name
        self.path = path
        self.body = (entity, architecture)
        self.config_target = config_target
        self.dependencies = dependencies

        if entity:
            self.interface = Interface(entity.in_ports, entity.out_ports)
        else:
            self.interface = []

        if libs:
            self.libs = STDLIBS + list(libs)
        else:
            self.libs = STDLIBS

        if entity and architecture:
            self.component = Component(name=name,
                                       generics=entity.generics,
                                       in_ports=entity.in_ports[3:],
                                       out_ports=entity.out_ports,
                                       out_types=None)
            self.component.lib_name = "work." + self.name
        else:
            self.component = None

    def __repr__(self):
        """ Return entity vhdl source code for debug. """
        from codegen import VhdlCodeGen
        return VhdlCodeGen(indent=4).visit(self.body[0])

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def get_filename(self):
        return "%s.%s" % (self.name, self._ext)

    def _compile(self, program_text):
        """ Save program_text in file. """
        vhdl_src_file = os.path.join(self.path, self.get_filename())
        # TODO: implement hashing to avoid writing already existing files
        # create vhdl source file
        with open(vhdl_src_file, "w") as vhdl_file:
            vhdl_file.write(program_text)

        return vhdl_src_file

    def codegen(self, indent=4):
        """ Generate source and save in file if VhdlFile.generated == True. """
        from sejits_ctree.vhdl.codegen import VhdlCodeGen

        # ---------------------------------------------------------------------
        # LOGGING
        # ---------------------------------------------------------------------
        logger.info("Start codegen of VhdlFile \"{0}\"".format(self.name))
        # ---------------------------------------------------------------------

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
        m_axis_mm2s_tdata = Signal("m_axis_mm2s_tdata",
                                   VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
        m_axis_mm2s_tkeep = Signal("m_axis_mm2s_tkeep",
                                   VhdlType.VhdlStdLogicVector(4, "0"))
        m_axis_mm2s_tlast = Signal("m_axis_mm2s_tlast",
                                   VhdlType.VhdlStdLogic("0"))
        m_axis_mm2s_tready = Signal("m_axis_mm2s_tready",
                                    VhdlType.VhdlStdLogic("0"))
        m_axis_mm2s_tvalid = Signal("m_axis_mm2s_tvalid",
                                    VhdlType.VhdlStdLogic("0"))
        in_sigs = [m_axis_mm2s_tdata, m_axis_mm2s_tkeep, m_axis_mm2s_tlast,
                   m_axis_mm2s_tready, m_axis_mm2s_tvalid]

        # output signals
        s_axis_s2mm_tdata = Signal("s_axis_s2mm_tdata",
                                   VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
        s_axis_s2mm_tkeep = Signal("s_axis_s2mm_tkeep",
                                   VhdlType.VhdlStdLogicVector(4, "0"))
        s_axis_s2mm_tlast = Signal("s_axis_s2mm_tlast",
                                   VhdlType.VhdlStdLogic("0"))
        s_axis_s2mm_tready = Signal("s_axis_s2mm_tready",
                                    VhdlType.VhdlStdLogic("0"))
        s_axis_s2mm_tvalid = Signal("s_axis_s2mm_tvalid",
                                    VhdlType.VhdlStdLogic("0"))
        out_sigs = [s_axis_s2mm_tdata, s_axis_s2mm_tkeep,
                    s_axis_s2mm_tlast, s_axis_s2mm_tready,
                    s_axis_s2mm_tvalid]

        # input/ output ports
        in_ports = [Port(sig.name, "in", sig) for sig in in_sigs]
        out_ports = [Port(sig.name, "out", sig) for sig in out_sigs]

        wrappee_comp = gen_top_file.component
        wrappee_comp.in_ports[3].value = m_axis_mm2s_tdata

        ret_sig = Signal("ret_tdata", VhdlType.VhdlStdLogicVector(AXI_STREAM_WIDTH, "0"))
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


class Statement(VhdlNode):
    """ docstring dummy."""
    pass


class Expression(VhdlNode):
    """ Base class for Expression nodes. """

    # instance counter to generate unique instance names
    _ids = defaultdict(int)
    lib_name = ""
    delay = 0
    in_ports = []
    out_ports = None


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
        if isinstance(value, Literal):
            self.value = value
            self.vhdl_type = value.vhdl_type
        else:
            raise TypeError

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


class VhdlSymbol(VhdlTreeNode):
    def label(self):
        """ Return node label for dot file. """
        from sejits_ctree.vhdl.dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)

class VhdlSource(VhdlSymbol):
    _fields = ["name", "vhdl_type"]

    def __init__(self, name="", vhdl_type=None):
        self.name = name
        self.vhdl_type = vhdl_type

class VhdlSignal(VhdlSymbol):
    _fields = ["name", "vhdl_type"]

    def __init__(self, name="", vhdl_type=None):
        self.name = name
        self.vhdl_type = vhdl_type

class VhdlConstant(VhdlSymbol):
    _fields = ["name", "vhdl_type", "value"]

    def __init__(self, name="", vhdl_type=None, value=None, ):
        if name == "":
            self.name = str(value)
        else:
            self.name = name
        self.vhdl_type = vhdl_type
        self.value = value

class VhdlModule(VhdlTreeNode):
    _fields = ["entity", "architecture"]

    def __init__(self, name="", entity=[], architecture=[]):
        self.name = name
        self.entity = entity
        self.architecture = architecture

    def label(self):
        """ Return node label for dot file. """
        from sejits_ctree.vhdl.dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)

class VhdlNode(VhdlTreeNode):
    _fields = ["prev", "next"]

    def __init__(self, prev=[], next=[], in_port=[], inport_info=None, out_port=[], outport_info=None):
        self.prev = prev
        self.next = next
        self.in_port = in_port
        self.out_port = out_port
        #
        self.inport_info = inport_info
        self.outport_info = outport_info
        #
        self.generic = []

    def label(self):
        """ Return node label for dot file. """
        from sejits_ctree.vhdl.dotgen import VhdlDotGenLabeller
        return VhdlDotGenLabeller().visit(self)

class VhdlBinaryOp(VhdlNode):
    _fields = ["prev", "next"]

    def __init__(self, prev=[], next=[], in_port=[], op=None, out_port=[]):

        in_port_info = [("LEFT", "in"), ("RIGHT", "in")]
        out_port_info = [("BINOP_OUT", "out")]

        super(VhdlBinaryOp, self).__init__(prev, next, in_port, in_port_info, out_port, out_port_info)
        self.generic = [op]
        self.op = op
        self.d = 5  # TODO: make dependent on op

class VhdlReturn(VhdlNode):
    _fields = ["prev", "next"]

    def __init__(self, prev=[], next=[], in_port=[], out_port=[]):
        if len(in_port) != 1 or len(out_port) != 1:
            raise TransformationError("VhdlReturn node supports only 1 in- and output")

        in_port_info = [("RETURN_IN", "in")]
        out_port_info = [("RETURN_OUT", "out")]

        super(VhdlReturn, self).__init__(prev, next, in_port, in_port_info, out_port, out_port_info)
        self.d = 0

class VhdlComponent(VhdlNode):

    _fields = ["prev", "next"]

    def __init__(self, prev=[], next=[], generic_slice=None, delay=0, in_port=[], inport_info=None, out_port=[], outport_info=None):
        # port info = [("PORTNAME", direction), ...]
        if generic_slice:
            in_port = in_port[generic_slice.stop:]

        super(VhdlComponent, self).__init__(prev, next, in_port, in_port_info, out_port, out_port_info)

        if generic_slice:
            self.generic = in_port[generic_slice]
        self.d = delay
