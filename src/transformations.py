"""Transformations."""
import ast
import copy
import logging
from collections import namedtuple
#
from utils import TransformationError
from utils import CONFIG
from nodes import VhdlType
from nodes import VhdlBinaryOp, VhdlComponent, VhdlConstant, VhdlModule
from nodes import VhdlReturn, VhdlSource, VhdlNode, VhdlSignal
from nodes import VhdlSink, VhdlDReg
from nodes import VhdlLibrary, VhdlAnd, PortInfo, Port, Generic
#
from ctree.c.nodes import *


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


UNARY_OP = namedtuple("UNARY_OP", ["i_args", "out_arg"])

class VhdlKeywordTransformer(ast.NodeTransformer):

    """Transform Name nodes with VHDL keywords."""

    # Vhdl keyword set; change every occurence in pyhton AST
    VHDL_Keywords = ({"abs", "access", "after", "alias", "all", "and",
                      "architecture", "array", "assert", "attribute",
                      "begin", "block", "body", "buffer", "bus", "case",
                      "component", "configuration", "constant",
                      "disconnect", "downto", "else", "elsif", "end",
                      "entity", "exit", "file", "for", "function",
                      "generate", "generic", "group", "guarded", "if",
                      "impure", "in", "inertial", "inout", "is", "label",
                      "library", "linkage", "literal", "loop", "map",
                      "mod", "nand", "new", "next", "nor", "not",
                      "null", "of", "on", "open", "or", "others", "out",
                      "package", "port", "postponed", "procedure",
                      "process", "pure", "range", "record", "register",
                      "reject", "rem", "report", "return", "rol", "ror",
                      "select", "severity", "signal", "shared", "sla",
                      "sll", "sra", "srl", "subtype", "then", "to",
                      "transport", "type", "unaffected", "units", "until",
                      "use", "variable", "wait", "when", "while", "width",
                      "with", "xnor", "xor"})

    def visit_Name(self, node):
        """Change id of Name node if it is a VHDL keyword."""
        if node.id.lower() in self.VHDL_Keywords:
            node.id = "sig_" + node.id
        return node


class VhdlTransformer(ast.NodeTransformer):

    def __init__(self, lifted_functions=[]):
        self.symbols = {}
        self.lifted_function_names = {f.name for f in lifted_functions}
        self.lifted_functions = lifted_functions
        self.lifted_functions.reverse()
        self.assignments = set()
        self.n_con_signals = 0

        # TODO: implement direct parameter processing
        for source in ["n"]:
            source_node = VhdlSource(source, VhdlType.VhdlStdLogicVector(8))
            self.symbols[source] = source_node
            # add sources to assignments to prevent reassignment
            self.assignments.add(source)

    def visit_MultiNode(self, node):
        module = map(self.visit, node.body)
        return module[0]

    def visit_FunctionDecl(self, node):
        params = map(self.visit, node.params)
        body = map(self.visit, node.defn)
        # add return signal
        params.append(self.symbols["MODULE_OUT"])
        #
        libraries = [VhdlLibrary("ieee", ["ieee.std_logic_1164.all",
                                          "ieee.numeric_std.all"]),
                     VhdlLibrary(None, ["work.the_filter_package.all"])]
        #
        ret = VhdlModule(node.name, libraries, None, params, body[-1])
        # retime
        VhdlDag().visit(ret)
        # finalize ports
        PortFinalizer().visit(ret)
        return ret

    def visit_FunctionCall(self, node):
        args = map(self.visit, node.args)
        if node.func.name in self.lifted_function_names:
            vhdl_node = self.lifted_functions.pop()
            vhdl_node.prev = args
            vhdl_node.in_port = [self._connect(arg) for arg in args]
            return vhdl_node
        else:
            raise TransformationError("Unknown function %s" % node.func)

    def visit_BinaryOp(self, node):
        left, right = map(self.visit, [node.left, node.right])
        #
        if isinstance(node.op, Op.Assign):
            # check for source assignment
            if type(left) is VhdlSource:
                raise TransformationError("Assignment to input parameter %s" % left.name)
            # check for reassignment
            if node.left.name in self.assignments:
                raise TransformationError("Reassignment of symbol %s" % node.left.name)

            if isinstance(right, VhdlNode):
                vhdl_node = right
                vhdl_node.out_port = [left]
            elif isinstance(right, VhdlConstant):
                vhdl_node = right
                vhdl_node.name = left.name
            else:
                raise TransformationError("Illegal assignment to symbol %s" % node.left.name)
            self.symbols[left.name] = vhdl_node
            self.assignments.add(left.name)
        else:
            vhdl_node = VhdlBinaryOp(prev=[left, right],
                                     in_port=[self._connect(left),
                                               self._connect(right)],
                                     op=node.op,
                                     out_port=[])
        return vhdl_node

    def visit_SymbolRef(self, node):
        if node.name not in self.symbols:
            vhdl_sym = VhdlSignal(name=node.name,
                                  vhdl_type=VhdlType.VhdlStdLogicVector(8))
            self.symbols[vhdl_sym.name] = vhdl_sym
        return self.symbols[node.name]

    def visit_Array(self, node):
        body = map(self.visit, node.body)
        if all([isinstance(bdy_elem, VhdlConstant) for bdy_elem in body]):
            return VhdlConstant(name="",
                                vhdl_type=VhdlType.VhdlArray.from_list(body),
                                value=tuple([elem.value for elem in body]))
        else:
            raise TransformationError("All elements of array must be constant")

    def visit_Tuple(self, node):
        body = map(self.visit, node.elts)
        if all([isinstance(bdy_elem, VhdlConstant) for bdy_elem in body]):
            return VhdlConstant(name="",
                                vhdl_type=VhdlType.VhdlArray.from_list(body),
                                value=tuple([elem.value for elem in body]))
        else:
            raise TransformationError("All elements of array must be constant")

    def visit_Constant(self, node):
        vhdl_sym = VhdlConstant(name="",
                                vhdl_type=VhdlType.VhdlInteger(),
                                value=node.value)
        return vhdl_sym

    def visit_Return(self, node):
        value = self.visit(node.value)

        con_sig = self._connect(value)
        ret_signal = VhdlSink("MODULE_OUT", con_sig.vhdl_type)
        self.symbols[ret_signal.name] = ret_signal
        #
        vhdl_node = VhdlReturn(prev=[value],
                               in_port=[con_sig],
                               out_port=[ret_signal])
        return vhdl_node

    def _connect(self, node, target=None):
        if isinstance(node, VhdlNode):
            if len(node.out_port) == 0:
                con_signal = VhdlSignal(name=node.__class__.__name__.upper() + "_OUT_" + str(self.n_con_signals),
                                        vhdl_type=VhdlType.VhdlStdLogicVector(8))
                self.n_con_signals += 1
                node.out_port.append(con_signal)
                self.symbols[con_signal.name] = con_signal
                return con_signal
            else:
                return node.out_port[0]
        else:
            return node


class VhdlDag(ast.NodeTransformer):

    def __init__(self):
        self.con_edge_id = 0

    def visit_VhdlModule(self, node):
        self.visit(node.architecture)

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.retime(node)

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        self.retime(node)

    def visit_VhdlComponent(self, node):
        map(self.visit, node.prev)
        self.retime(node)

    def retime(self, node):
        prev_d = [prev.d + prev.dprev for prev in node.prev]
        max_d = max(prev_d)
        norm_prev_d = [max_d - d for d in prev_d]

        # retime every edge to match maximum delay
        for idx, prev, edge, d in zip(range(len(node.prev)), node.prev,
                                      node.in_port, norm_prev_d):
            if d > 0 and type(edge) is not VhdlConstant:
                # generate unique connection signal name
                c_id = self.con_edge_id
                self.con_edge_id += 1
                #
                con_edge = VhdlSignal(name=edge.name + "_DREG_" + str(c_id),
                                      vhdl_type=edge.vhdl_type)
                dreg = VhdlDReg(prev=[prev],
                                delay=d,
                                in_port=[edge],
                                out_port=[con_edge])
                node.prev[idx] = dreg
                node.in_port[idx] = con_edge
        node.dprev = max_d


class TypeChecker(ast.NodeVisitor):
    def __init__(self):
        pass


class PortFinalizer(ast.NodeVisitor):

    def __init__(self):
        # ICP - Input Command Ports
        self.icps_info = [PortInfo("CLK", "in", VhdlType.VhdlStdLogic()),
                          PortInfo("RST", "in", VhdlType.VhdlStdLogic())]

        # ICCP - Input Cascading Command Ports
        self.iccps_info = [PortInfo("VALID_IN", "in", VhdlType.VhdlStdLogic())]

        # OCCP - Output Cascading Command Ports
        self.occps_info = [PortInfo("VALID_OUT", "out", VhdlType.VhdlStdLogic())]

        self.cpe_id = 0  # command port edge ID

        # generate Ports
        self.icps = [Port(*info, value=VhdlSignal(info.name, info.vhdl_type))
                     for info in self.icps_info]
        self.iccps = [Port(*info, value=VhdlSignal(info.name, info.vhdl_type))
                      for info in self.iccps_info]
        self.occps = [Port(*info, value=VhdlSignal(info.name, info.vhdl_type))
                      for info in self.occps_info]

        #
        self.visited_nodes = set()

    def visit_VhdlModule(self, node):
        self.visit(node.architecture)
        self.finalize_ports(node)

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)

    def visit_VhdlComponent(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)

    def visit_VhdlDReg(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)

    def finalize_ports(self, node):
        iccps = []
        idxs = range(len(self.iccps_info))
        #
        node.finalize_ports()
        #
        if isinstance(node, VhdlModule):
            node.in_port = self.icps + self.iccps + node.in_port
            node.out_port = self.occps + node.out_port
        else:
            for iccp, occp, idx in zip(self.iccps_info, self.occps_info, idxs):
                cc_edges = VhdlAnd()
                for pnode in node.prev:
                    poccps = []
                    if hasattr(pnode, "out_port"):  # VhdlNode Class
                        # pnode already finalized
                        if hash(pnode) in self.visited_nodes:
                            # get cascading connection edge
                            cc_edge = pnode.out_port[idx].value
                        else:
                            n = pnode.__class__.__name__ + "_" + occp.name + "_" + str(self.cpe_id)
                            self.cpe_id += 1
                            cc_edge = VhdlSignal(name=n,
                                                 vhdl_type=occp.vhdl_type)
                            poccps.append(Port(occp.name,
                                               occp.direction,
                                               occp.vhdl_type,
                                               cc_edge))
                            cc_edges.append(cc_edge)
                        # finalize previous nodes out_port
                        pnode.out_port = poccps + pnode.out_port
                    else:  # VhdlSymbol Class
                        if isinstance(pnode, VhdlSource):
                            # add vhdl modules command port
                            cc_edge = VhdlSignal(iccp.name, iccp.vhdl_type)
                            cc_edges.append(cc_edge)
                    self.visited_nodes.add(hash(pnode))
                # finalize nodes in_port
                iccps.append(Port(iccp.name,
                                  iccp.direction,
                                  iccp.vhdl_type,
                                  cc_edges))
            # finalize nodes in_port
            node.in_port = self.icps + iccps + node.in_port
            if isinstance(node, VhdlReturn):
                node.out_port = self.occps + node.out_port


class BB_BaseFuncTransformer(ast.NodeTransformer):
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
        BB_BaseFuncTransformer.lifted_functions.append(func_def)
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


class BB_ConvolveTransformer(BB_BaseFuncTransformer):
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


class BB_FuncTransformer(object):
    """Transformer for all basic block transformer."""

    transformers = [BB_ConvolveTransformer]

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
        return BB_BaseFuncTransformer.lifted_functions
