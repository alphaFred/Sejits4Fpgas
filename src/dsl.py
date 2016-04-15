import ast
import logging
import numpy as np
import ctypes

from ctree.c.nodes import FunctionCall, SymbolRef, Return, BinaryOp, Op, Constant, FunctionDecl

from src import transformations
from src.nodes import VhdlComponent, VhdlSource, VhdlSignal, VhdlSink, VhdlSignalSplit, VhdlReturn, VhdlSignalMerge, \
    VhdlLibrary, VhdlModule, VhdlFile, VhdlConcatenation, VhdlAssignment, PortInfo, GenericInfo
from src.types import VhdlType
from src.utils import TransformationError, CONFIG

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


class BasicBlockBaseTransformer(ast.NodeTransformer):
    lifted_functions = []
    func_count = 0

    def __init__(self, backend="C"):
        self.backend = backend.lower()

    def visit_Call(self, node):
        self.generic_visit(node)
        if getattr(node.func, "id", None) != self.func_name:
            return node

        return self.convert(node)

    def convert(self, node):
        method = "get_func_def_" + self.backend
        try:
            func_def_getter = getattr(self, method)
        except AttributeError:
            error_msg = "No function definition provided for %s backend"\
                % self.backend
            raise TransformationError(error_msg)

        func_def = func_def_getter()
        # add function definition to class variable lifted_functions
        BasicBlockBaseTransformer.lifted_functions.append((node.lineno, func_def))
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

    def get_func_def_c(self, inner_function_name):
        raise NotImplementedError("Class %s should override get_func_def()"
                                  % type(self))


class ConvolveTransformer(BasicBlockBaseTransformer):
    func_name = "bb_convolve"

    def get_func_def_c(self):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self):
        """Return VHDL interpretation of the BasicBlock."""
        inport_info = [GenericInfo("FILTERMATRIX",
                                   VhdlType.VhdlArray(9, VhdlType.VhdlInteger, -20, 20, type_def="filtMASK")),
                       GenericInfo("FILTER_SCALE", VhdlType.VhdlInteger()),
                       GenericInfo("IMG_WIDTH", VhdlType.VhdlPositive()),
                       GenericInfo("IMG_HEIGHT", VhdlType.VhdlPositive()),
                       GenericInfo("IN_BITWIDTH", VhdlType.VhdlPositive()),
                       GenericInfo("OUT_BITWIDTH", VhdlType.VhdlPositive()),
                       PortInfo("DATA_IN", "in", VhdlType.VhdlStdLogicVector(8))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(8))]
        defn = VhdlComponent(name="bb_convolve",
                             generic_slice=slice(0, 6),
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.Convolve")
        return defn

class SplitTransformer(BasicBlockBaseTransformer):
    func_name = "bb_split"

    def get_func_def_c(self):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self):
        """Return VHDL interpretation of the BasicBlock."""
        inport_info = [PortInfo("DATA_IN", "in", VhdlType.VhdlStdLogicVector(24)),
                       PortInfo("INDEX", "in", VhdlType.VhdlUnsigned(8))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(8))]
        defn = VhdlComponent(name="bb_split",
                             generic_slice=None,
                             delay=0,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.split")
        return defn

class MergeTransformer(BasicBlockBaseTransformer):
    func_name = "bb_merge"

    def get_func_def_c(self):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self):
        """Return VHDL interpretation of the BasicBlock."""
        inport_info = [PortInfo("R_IN", "in", VhdlType.VhdlStdLogicVector(8)),
                       PortInfo("G_IN", "in", VhdlType.VhdlStdLogicVector(8)),
                       PortInfo("B_IN", "in", VhdlType.VhdlStdLogicVector(8))]
        #
        outport_info = [PortInfo("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(24))]
        defn = VhdlComponent(name="bb_merge",
                             generic_slice=None,
                             delay=0,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.merge")
        return defn


class DSLTransformer(object):
    """Transformer for all basic block transformer."""

    transformers = [ConvolveTransformer, SplitTransformer, MergeTransformer]

    def __init__(self, backend="C"):
        """Initialize transformation target backend."""
        self.backend = backend

    def visit(self, tree):
        """Enable all basic block Transformations."""
        for transformer in self.transformers:
            transformer(self.backend).visit(tree)
        return tree

    @staticmethod
    def lifted_functions():
        """Return all basic block transformer functions."""
        lf = BasicBlockBaseTransformer.lifted_functions
        lf.sort()
        lf = [i[1] for i in lf]
        return lf


def get_dsl_type(params=None):
    #
    MAX_IPT_BYTEWIDTH = 1
    #
    def _get_vhdltype(dtype, len=1):
        if isinstance(dtype.type(), np.integer):
            if dtype.itemsize <= MAX_IPT_BYTEWIDTH:
                return VhdlType.VhdlStdLogicVector(8 * dtype.itemsize * len)
            else:
                raise TransformationError("Input data of width {}bit not supported".format(dtype.itemsize * 8))
        else:
            raise TransformationError("Invalid parameter type: {}".format(type(dtype)))

    def process_2darray(param):
        return _get_vhdltype(param.dtype)

    def process_3darray(param):
        # TODO: make len 3=RGB) dynamic; e.g. for RGBA
        return _get_vhdltype(param.dtype, 3)

    def dispatch(param):
        if param.ndim == 2:
            return process_2darray(param)
        elif param.ndim == 3:
            return process_3darray(param)
        else:
            raise TransformationError("Processing of {}dim arrays not supported".format(param.ndim))

    _params = params if params is not None else []
    #
    if len(_params) == 1:
        if not isinstance(_params[0], np.ndarray):
            raise TransformationError("All input parameter must be of type np.ndarray")
        return [dispatch(_params[0])]
    elif len(_params) > 1:
        if not all([isinstance(p, np.ndarray) for p in _params]):
            raise TransformationError("All input parameter must be of type np.ndarray")
        return map(dispatch, _params)
    else:
        raise TransformationError("DSL kernel must have at least one input parameter")


class DSLWrapper(object):
    def __init__(self, ipt_params=None):
        self.axi_stream_width = 32
        self.ipt_params = ipt_params if ipt_params is not None else []
        #
        # input signals
        m_axis_mm2s_tdata = VhdlSource("m_axis_mm2s_tdata", VhdlType.VhdlStdLogicVector(self.axi_stream_width, "0"))
        m_axis_mm2s_tlast = VhdlSignal("m_axis_mm2s_tlast", VhdlType.VhdlStdLogic("0"))
        m_axis_mm2s_tready = VhdlSignal("m_axis_mm2s_tready", VhdlType.VhdlStdLogic("0"))
        #
        self.in_sigs = [m_axis_mm2s_tdata, m_axis_mm2s_tlast, m_axis_mm2s_tready]

        # output signals
        s_axis_s2mm_tdata = VhdlSink("s_axis_s2mm_tdata", VhdlType.VhdlStdLogicVector(self.axi_stream_width, "0"))
        s_axis_s2mm_tlast = VhdlSignal("s_axis_s2mm_tlast", VhdlType.VhdlStdLogic("0"))
        s_axis_s2mm_tready = VhdlSignal("s_axis_s2mm_tready", VhdlType.VhdlStdLogic("0"))
        #
        self.out_sigs = [s_axis_s2mm_tdata, s_axis_s2mm_tlast, s_axis_s2mm_tready]

    def generate_wrapper(self, file2wrap=None):
        try:
            component = file2wrap.component()
        except AttributeError:
            raise TransformationError("File to wrap must provide component() method")
        else:
            if type(self.ipt_params[0]) is VhdlType.VhdlStdLogicVector:
                if len(self.ipt_params[0]) == 8:
                    return self._generate_wrapper_2d(component)
                else:
                    return self._generate_wrapper_3d(component)
            else:
                raise TransformationError("Invalid parameter type {}".format(type(self.ipt_params[0])))

    def _generate_wrapper_2d(self, component):
        logger.info("Generate project wrapper")


        ret_sig = VhdlSignal("ret_tdata", VhdlType.VhdlStdLogicVector(8, "0"))
        #
        component.library = "work.apply"
        component.delay = 5
        component.prev = [self.in_sigs[0]]
        component.in_port = [VhdlSignalSplit(self.in_sigs[0], slice(0, 8))]
        component.out_port = [ret_sig]
        #
        ret_component = VhdlReturn([component], [VhdlSignalMerge(ret_sig, slice(8, 32), "0")], [self.out_sigs[0]])

        libraries = [VhdlLibrary("ieee", ["ieee.std_logic_1164.all",
                                          "ieee.numeric_std.all"]),
                     VhdlLibrary(None, ["work.the_filter_package.all"])]
        #
        architecture = [ret_component] + [VhdlAssignment(t, s) for t,s in zip(self.out_sigs[1:], self.in_sigs[1:])]
        module = VhdlModule("accel_wrapper", libraries, slice(0, len(self.in_sigs)), self.in_sigs + self.out_sigs, architecture)
        #
        module = transformations.VhdlGraphTransformer().visit(module)
        module = transformations.VhdlPortTransformer().visit(module)
        return VhdlFile("accel_wrapper", [module])

    def _generate_wrapper_3d(self, component):
        logger.info("Generate project wrapper")

        ret_sig = VhdlSignal("ret_tdata", VhdlType.VhdlStdLogicVector(24))
        #
        component.library = "work.apply"
        component.delay = 5
        component.prev = [self.in_sigs[0]]
        #
        component.in_port = [VhdlConcatenation([VhdlSignalSplit(self.in_sigs[0], slice(0, 8)),
                                                VhdlSignalSplit(self.in_sigs[0], slice(8, 16)),
                                                VhdlSignalSplit(self.in_sigs[0], slice(16, 24))])]
        component.out_port = [ret_sig]
        #
        ret_component = VhdlReturn([component], [VhdlSignalMerge(ret_sig, slice(24, 32))], [self.out_sigs[0]])

        libraries = [VhdlLibrary("ieee", ["ieee.std_logic_1164.all",
                                          "ieee.numeric_std.all"]),
                     VhdlLibrary(None, ["work.the_filter_package.all"])]
        #
        module = VhdlModule("accel_wrapper", libraries, slice(0, len(self.in_sigs)), self.in_sigs + self.out_sigs, [ret_component])
        module = transformations.VhdlGraphTransformer().visit(module)
        module = transformations.VhdlPortTransformer().visit(module)
        return VhdlFile("accel_wrapper", [module])
