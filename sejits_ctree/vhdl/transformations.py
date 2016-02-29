""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import logging

from sejits_ctree.vhdl import TransformationError
from sejits_ctree.vhdl.utils import CONFIG
from collections import namedtuple
from nodes import VhdlType
#
from nodes import VhdlBinaryOp, VhdlComponent, VhdlConstant, VhdlModule
from nodes import VhdlReturn, VhdlSource, VhdlNode, VhdlSignal, VhdlDReg
from nodes import VhdlLibrary
from ctree.c.nodes import Op

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

    """ Transform Name nodes with VHDL keywords. """

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
        """ Change id of Name node if it is a VHDL keyword. """
        if node.id.lower() in self.VHDL_Keywords:
            node.id = "sig_" + node.id
        return node


class VhdlTransformer(ast.NodeTransformer):

    def __init__(self):
        self.symbols = {}
        self.assignments = set()
        self.n_con_signals = 0

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
        # retime, beginning with Return node
        VhdlDag().visit(body[-1])
        #
        libraries = [VhdlLibrary("ieee",["ieee.std_logic_1164.all"]),
                     VhdlLibrary(None,["work.the_filter_package.all"])]
        #
        return VhdlModule(node.name, libraries, params, body[-1])

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
                                value=body)
        else:
            raise TransformationError("All elements of array must be constant")

    def visit_Constant(self, node):
        vhdl_sym = VhdlConstant(name="",
                                vhdl_type=VhdlType.VhdlStdLogicVector(8),
                                value=node.value)
        return vhdl_sym

    def visit_Return(self, node):
        value = self.visit(node.value)

        con_sig = self._connect(value)
        ret_signal = VhdlSignal("MODULE_OUT", con_sig.vhdl_type)
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

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.retime(node)

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        self.retime(node)

    def retime(self, node):
        prev_d = [prev.d + prev.dprev for prev in node.prev]
        max_d = max(prev_d)
        norm_prev_d = [max_d - d for d in prev_d]

        # retime every edge to match maximum delay
        for idx, prev, edge, d in zip(range(len(node.prev)), node.prev, node.in_port, norm_prev_d):
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
