import ast
import ctypes

from ctree.c.nodes import FunctionCall, SymbolRef, Return, BinaryOp, Op, Constant, FunctionDecl

from src.nodes import VhdlComponent
from src.types import VhdlType
from src.utils import TransformationError


class DSLBaseTransformer(ast.NodeTransformer):
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
        DSLBaseTransformer.lifted_functions.append(func_def)
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


class ConvolveTransformer(DSLBaseTransformer):
    func_name = "bb_convolve"

    def get_func_def_c(self):
        """Return C interpretation of the BasicBlock."""
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self):
        """Return VHDL interpretation of the BasicBlock."""
        inport_info = [("FILTERMATRIX",
                        VhdlType.VhdlArray(9,
                                           VhdlType.VhdlInteger,
                                           -20,
                                           20,
                                           type_def="filtMASK")),
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


class VhdlDSLTransformer(object):
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
        return DSLBaseTransformer.lifted_functions