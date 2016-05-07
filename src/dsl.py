import ast
import ctypes
import logging
from collections import namedtuple

import numpy as np
import transformations
from nodes import GenericInfo
from nodes import PortInfo
from nodes import VhdlAssignment
from nodes import VhdlComponent
from nodes import VhdlFile
from nodes import VhdlLibrary
from nodes import VhdlModule
from nodes import VhdlReturn
from nodes import VhdlSignal
from nodes import VhdlSink
from nodes import VhdlSource
from types import VhdlType
from utils import TransformationError, CONFIG
from .vhdl_ctree.c.nodes import BinaryOp
from .vhdl_ctree.c.nodes import Constant
from .vhdl_ctree.c.nodes import FunctionCall
from .vhdl_ctree.c.nodes import FunctionDecl
from .vhdl_ctree.c.nodes import Op
from .vhdl_ctree.c.nodes import Return
from .vhdl_ctree.c.nodes import SymbolRef

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

LF_Data = namedtuple("LF_Data", ["lineno", "func"])


class BasicBlockBaseTransformer(object):
    lifted_functions = []
    func_count = 0

    def __init__(self, backend="C", **kwargs):
        self.backend = backend.lower()
        self.kwargs = kwargs

    def convert(self, node):
        method = "get_func_def_" + self.backend
        try:
            func_def_getter = getattr(self, method)
        except AttributeError:
            error_msg = "No function definition provided for %s backend" \
                        % self.backend
            raise TransformationError(error_msg)

        func_def = func_def_getter(**self.kwargs)
        # add function definition to class variable lifted_functions
        BasicBlockBaseTransformer.lifted_functions.append(LF_Data(node.lineno, func_def))
        # return C node FunctionCall
        return FunctionCall(SymbolRef(func_def.name), node.args)

    @property
    def gen_func_name(self):
        name = "%s_%s" % (self.func_name, str(type(self).func_count))
        type(self).func_count += 1
        return name

    @property
    def func_name(self):
        raise NotImplementedError("Class %s should override func_name()"
                                  % type(self))

    def get_func_def_c(self, *args, **kwargs):
        raise NotImplementedError("Class %s should override get_func_def_c()" % type(self))

    def get_func_def_vhdl(self, *args, **kwargs):
        raise NotImplementedError("Class %s should override get_func_def_vhdl()" % type(self))


class ConvolveTransformer(BasicBlockBaseTransformer):
    func_name = "bb_convolve"

    def get_func_def_c(self, **kwargs):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [GenericInfo("FILTERMATRIX",
                                   VhdlType.VhdlArray(9, VhdlType.VhdlInteger, -20, 20, type_def="filtMASK")),
                       GenericInfo("FILTER_SCALE", VhdlType.VhdlInteger()),
                       GenericInfo("IMG_WIDTH", VhdlType.VhdlPositive()),
                       GenericInfo("IMG_HEIGHT", VhdlType.VhdlPositive()),
                       PortInfo("DATA_IN", "in", VhdlType.VhdlStdLogicVector(data_width))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        defn = VhdlComponent(name=self.func_name,
                             generic_slice=slice(0, 4),
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.Convolve")
        return defn


class AddTransformer(BasicBlockBaseTransformer):
    func_name = "bb_add"

    def get_func_def_c(self, **kwargs):
        params = [SymbolRef("x", ctypes.c_long()), SymbolRef("y", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("x"), Op.Add(), SymbolRef("y")))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [PortInfo("LEFT", "in", VhdlType.VhdlStdLogicVector(data_width)),
                       PortInfo("RIGHT", "in", VhdlType.VhdlStdLogicVector(data_width))]
        outport_info = [PortInfo("ADD_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        #
        defn = VhdlComponent(name=self.func_name,
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.AddBB")
        #
        return defn


class SubTransformer(BasicBlockBaseTransformer):
    func_name = "bb_sub"

    def get_func_def_c(self, **kwargs):
        params = [SymbolRef("x", ctypes.c_long()), SymbolRef("y", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("x"), Op.Sub(), SymbolRef("y")))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [PortInfo("LEFT", "in", VhdlType.VhdlStdLogicVector(data_width)),
                       PortInfo("RIGHT", "in", VhdlType.VhdlStdLogicVector(data_width))]
        outport_info = [PortInfo("SUB_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        #
        defn = VhdlComponent(name=self.func_name,
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.SubBB")
        #
        return defn


class MulTransformer(BasicBlockBaseTransformer):
    func_name = "bb_mul"

    def get_func_def_c(self, **kwargs):
        params = [SymbolRef("x", ctypes.c_long()), SymbolRef("y", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("x"), Op.Mul(), SymbolRef("y")))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [PortInfo("LEFT", "in", VhdlType.VhdlStdLogicVector(data_width)),
                       PortInfo("RIGHT", "in", VhdlType.VhdlStdLogicVector(data_width))]
        outport_info = [PortInfo("MUL_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        #
        defn = VhdlComponent(name=self.func_name,
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.MulBB")
        #
        return defn


class SplitTransformer(BasicBlockBaseTransformer):
    func_name = "bb_split"

    def get_func_def_c(self, **kwargs):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [GenericInfo("INDEX", VhdlType.VhdlInteger()),
                       PortInfo("DATA_IN", "in", VhdlType.VhdlStdLogicVector(data_width))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        defn = VhdlComponent(name=self.func_name,
                             generic_slice=slice(0, 1),
                             delay=0,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.split")
        return defn


class MergeTransformer(BasicBlockBaseTransformer):
    func_name = "bb_merge"

    def get_func_def_c(self, **kwargs):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [PortInfo("IN_3", "in", VhdlType.VhdlStdLogicVector(data_width)),
                       PortInfo("IN_2", "in", VhdlType.VhdlStdLogicVector(data_width)),
                       PortInfo("IN_1", "in", VhdlType.VhdlStdLogicVector(data_width)),
                       PortInfo("IN_0", "in", VhdlType.VhdlStdLogicVector(data_width))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        defn = VhdlComponent(name=self.func_name,
                             generic_slice=None,
                             delay=0,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.merge")
        return defn


class LimitToTransformer(BasicBlockBaseTransformer):
    func_name = "bb_limitTo"

    def get_func_def_c(self, **kwargs):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self, **kwargs):
        """Return VHDL interpretation of the BasicBlock."""
        if "DataWidth" in kwargs:
            data_width = kwargs["DataWidth"]
        else:
            data_width = 32
        #
        inport_info = [GenericInfo("VALID_BITS", VhdlType.VhdlPositive()),
                       PortInfo("DATA_IN", "in", VhdlType.VhdlStdLogicVector(data_width))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(data_width))]
        defn = VhdlComponent(name=self.func_name,
                             generic_slice=slice(0, 1),
                             delay=0,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.LimitTo")
        return defn


class DSLTransformer(ast.NodeTransformer):
    """Transformer for all basic block transformer."""

    transformers = [ConvolveTransformer, AddTransformer,
                    SubTransformer, MulTransformer,
                    SplitTransformer, MergeTransformer,
                    LimitToTransformer]

    def __init__(self, backend="C", **kwargs):
        """Initialize transformation target backend."""
        self.backend = backend
        self.kwargs = kwargs
        #
        self.transformer_func = {t.func_name: t for t in self.transformers}

    def visit_Call(self, node):
        self.generic_visit(node)
        if getattr(node.func, "id", None) not in self.transformer_func:
            return node
        else:
            transformer = self.transformer_func[getattr(node.func, "id", None)]
            return transformer(self.backend, **self.kwargs).convert(node)

    @staticmethod
    def lifted_functions():
        """Return all basic block transformer functions."""
        lifted_functions = BasicBlockBaseTransformer.lifted_functions
        # group and reverse
        line_dict = {}
        line_nbrs = []
        #
        for lf in lifted_functions:
            if lf.lineno in line_dict:
                line_dict[lf.lineno].append(lf.func)
            else:
                line_dict[lf.lineno] = [lf.func]
                line_nbrs.append(lf.lineno)
        #
        line_nbrs.sort()
        line_nbrs.reverse()
        #
        ret = []
        for ln in line_nbrs:
            data = line_dict[ln]
            data.reverse()
            ret.extend(data)
        #
        return ret


def get_dsl_type(params, axi_stream_width=0):
    def gen_return(ipt, width):
        if not isinstance(ipt, np.ndarray):
            raise TransformationError("All input parameter must be of type np.ndarray")
        else:
            return VhdlType.VhdlStdLogicVector(width)

    #
    if hasattr(params, "__iter__"):
        ret = []
        for param in params:
            ret.append(gen_return(param, axi_stream_width))
        return ret
    else:
        return gen_return(params, axi_stream_width)


def gen_dsl_wrapper(ipt_params, axi_stream_width, file2wrap):
    axi_stream_width = axi_stream_width
    ipt_params = ipt_params

    # TODO: Change to support multiple input params

    if len(ipt_params) > 1:
        raise TransformationError("Multiple inputs currently not supported by the hardware!")
    # input signals
    m_axis_mm2s_tdata = VhdlSource("m_axis_mm2s_tdata", VhdlType.VhdlStdLogicVector(axi_stream_width, "0"))
    m_axis_mm2s_tlast = VhdlSignal("m_axis_mm2s_tlast", VhdlType.VhdlStdLogic("0"))
    s_axis_s2mm_tready = VhdlSignal("s_axis_s2mm_tready", VhdlType.VhdlStdLogic("0"))
    #
    in_sigs = [m_axis_mm2s_tdata, m_axis_mm2s_tlast, s_axis_s2mm_tready]

    # output signals
    s_axis_s2mm_tdata = VhdlSink("s_axis_s2mm_tdata", VhdlType.VhdlStdLogicVector(axi_stream_width, "0"))
    s_axis_s2mm_tlast = VhdlSignal("s_axis_s2mm_tlast", VhdlType.VhdlStdLogic("0"))
    m_axis_mm2s_tready = VhdlSignal("m_axis_mm2s_tready", VhdlType.VhdlStdLogic("0"))
    #
    out_sigs = [s_axis_s2mm_tdata, s_axis_s2mm_tlast, m_axis_mm2s_tready]

    try:
        component = file2wrap.component()
    except AttributeError:
        raise TransformationError("File to wrap must provide component() method")
    else:
        logger.info("Generate project wrapper")
        #
        ret_sig = VhdlSignal("ret_tdata", VhdlType.VhdlStdLogicVector(axi_stream_width, "0"))
        #
        component.library = "work.apply"
        component.delay = 5
        component.prev = [in_sigs[0]]
        component.in_port = [in_sigs[0]]
        component.out_port = [ret_sig]
        #
        ret_component = VhdlReturn([component], [ret_sig], [out_sigs[0]])

        libraries = [VhdlLibrary("ieee", ["ieee.std_logic_1164.all",
                                          "ieee.numeric_std.all"]),
                     VhdlLibrary(None, ["work.the_filter_package.all"])]
        #
        architecture = [ret_component] + [VhdlAssignment(t, s) for t, s in zip(out_sigs[1:], in_sigs[1:])]
        module = VhdlModule("accel_wrapper", libraries,
                            slice(0, len(in_sigs)), in_sigs + out_sigs, architecture)
        #
        module = transformations.VhdlGraphTransformer().visit(module)
        module = transformations.VhdlPortTransformer().visit(module)
        return VhdlFile("accel_wrapper", [module])
