import ast
import numpy as np
import ctypes

from ctree.c.nodes import FunctionCall, SymbolRef, Return, BinaryOp, Op, Constant, FunctionDecl

from src.nodes import VhdlComponent, VhdlSource
from src.types import VhdlType
from src.utils import TransformationError


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
        BasicBlockBaseTransformer.lifted_functions.append(func_def)
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
        inport_info = [("FILTERMATRIX", VhdlType.VhdlArray(9, VhdlType.VhdlInteger, -20, 20, type_def="filtMASK")),
                       ("FILTER_SCALE", VhdlType.VhdlInteger()),
                       ("IMG_WIDTH", VhdlType.VhdlPositive()),
                       ("IMG_HEIGHT", VhdlType.VhdlPositive()),
                       ("IN_BITWIDTH", VhdlType.VhdlPositive()),
                       ("OUT_BITWIDTH", VhdlType.VhdlPositive()),
                       ("DATA_IN", "in", VhdlType.VhdlStdLogicVector(8))]
        #
        outport_info = [("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(8))]
        defn = VhdlComponent(name="bb_convolve",
                             generic_slice=slice(0, 6),
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.Convolve")
        return defn


class DSLTransformer(object):
    """Transformer for all basic block transformer."""

    transformers = [ConvolveTransformer]

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
        return BasicBlockBaseTransformer.lifted_functions


def get_dsl_type(params=None):
    #
    MAX_IPT_BYTEWIDTH = 1
    #
    def _get_vhdltype(dtype):
        if isinstance(dtype.type(), np.integer):
            if dtype.itemsize <= MAX_IPT_BYTEWIDTH:
                return VhdlType.VhdlStdLogicVector(8 * dtype.itemsize)
            else:
                raise TransformationError("Input data of width {}bit not supported".format(dtype.itemsize * 8))
        else:
            raise TransformationError("Invalid parameter type: {}".format(type(dtype)))

    def process_2darray(param):
        return _get_vhdltype(param.dtype)

    def process_3darray(param):
        raise NotImplementedError()

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
    def __init__(self):
        pass

