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
from nodes import VhdlReturn, VhdlSource, VhdlNode, VhdlSignal, VhdlSink, VhdlDReg
from nodes import VhdlLibrary
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
        self.lifted_functions = {f.name: f for f in lifted_functions}
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
        # retime, beginning with Return node
        VhdlDag().visit(body[-1])
        #
        libraries = [VhdlLibrary("ieee",["ieee.std_logic_1164.all"]),
                     VhdlLibrary(None,["work.the_filter_package.all"])]
        #
        return VhdlModule(node.name, libraries, None, params, body[-1])

    def visit_FunctionCall(self, node):
        args = map(self.visit, node.args)
        if node.func.name in self.lifted_functions:
            vhdl_node = self.lifted_functions[node.func.name]
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
                                vhdl_type=VhdlType.VhdlStdLogicVector(8),
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


class PortFinalizer(ast.NodeVisitor):

    def __init__(self):
        # ICP - Input Command Ports
        self.icps = [VhdlSignal("CLK", VhdlType.VhdlStdLogic()),
                    VhdlSignal("RST", VhdlType.VhdlStdLogic())]
        self.icps_info = [("CLK", "in", VhdlType.VhdlStdLogic()),
                         ("RST", "in", VhdlType.VhdlStdLogic())]

        # ICCP - Input Cascading Command Ports
        self.iccps = [VhdlSignal("VALID_IN", VhdlType.VhdlStdLogic())]
        self.iccps_info = [("VALID_IN", "in", VhdlType.VhdlStdLogic())]

        # OCCP - Output Cascading Command Ports
        self.occps = [VhdlSignal("VALID_OUT", VhdlType.VhdlStdLogic())]
        self.occps_info = [("VALID_OUT", "out", VhdlType.VhdlStdLogic())]

        cpe_id = 0  # command port edge ID

    def visit_VhdlReturn(self, node):
        pass

    def visit_VhdlBinaryOp(self, node):
        pass

    def visit_VhdlComponent(self, node):
        pass

    def visit_VhdlDReg(self, node):
        pass







    def finalize_ports(self, node):
        # add command ports
        # add cascading command ports
        _finalize_ports(node)
        _finalize_cascades(nodes, [self.casc_cmd_port(2, 0)])

    def _finalize_ports(self, node):
        try:
            inport_info = node.inport_info
            in_port = node.in_port
            #
            outport_info = node.outport_info
            out_port = node.out_port
            #
            generic_info = node.generic_info
            generic_port = node.generic
        except AttributeError as ae:
            raise TransformationError(ae.message)
        else:
            # finalize in port
            final_inport = self._finalize_port(self.cmd_iport,
                                               self.cmd_iinfo,
                                               in_port,
                                               inport_info)
            if final_inport:
                node.in_port = final_inport

            # finalize out port
            final_outport = self._finalize_port(self.cmd_oport,
                                                self.cmd_oinfo,
                                                out_port,
                                                outport_info)
            if final_outport:
                node.out_port = final_outport

            # finalize generic port
            final_generic = self._finalize_generic([],
                                                   [],
                                                   generic_port,
                                                   generic_info)
            if final_generic:
                node.generic = final_generic

    def _finalize_port(self, cmd_port, cmd_info, port, port_info):
        """Add command ports to port."""
        if all([type(p) is Port for p in port]):
            # continue if node already has ports
            return None
        else:
            if len(port_info) != len(port):
                error_msg = "Number of ports does not match port" +\
                    " information of node: %s" % node.name
                raise TransformationError(error_msg)

            cmd_port = [Port(*info, value=val)
                        for info, val in zip(cmd_info, cmd_port)]
            return cmd_port + [Port(*info, value=val)
                               for info, val in zip(port_info, port)]

    def _finalize_generic(self, cmd_generic, cmd_info, generic, generic_info):
        """Add command ports to port."""
        if all([type(g) is Generic for g in generic]):
            # continue if node already has generics
            return None
        else:
            if len(generic_info) != len(generic):
                error_msg = "Number of generic ports does not match generic"\
                            + " information of node %s" % node.name
                raise TransformationError(error_msg)

            cmd_generic = [Generic(*info, value=val)
                           for info, val in zip(cmd_info, cmd_generic)]

            return cmd_generic + [Generic(*info, value=val)
                                  for info, val in zip(generic_info, generic)]

    def _finalize_cascades(self, node, casc_ports):
        if all([isinstance(p_node, (VhdlSource, VhdlConstant))
               for p_node in node.prev]):
            # no cascading
            pass
        else:
            for casc_port in casc_ports:
                ncmd_iport = []  # new command in port
                for p_node in node.prev:
                    if isinstance(p_node, VhdlConstant):
                        pass
                    elif isinstance(p_node, VhdlSource):
                        # connect to modules cascading in port
                        ncmd_iport.append(self.cmd_iport[casc_port.iport_idx])
                    else:
                        # connect to previous components cascading out port

                        # generate connection edge
                        ce_name = p_node.name + "_CASC_" + \
                            p_node.o_port[casc_port.oport_idx].name + \
                            str(c_id)
                        ce_type = p_node.o_port[casc_port.iport_idx].vhdl_type
                        c_edge = VhdlSignal(name=ce_name,
                                            vhdl_type=ce_type)
                        # connect to previous out port
                        p_node.o_port[casc_port.oport_idx] = c_edge
                        # add to new command in port
                        ncmd_iport.append(casc_edge)
                        #
                        self.c_id += 1
                # finalize connection
                if len(ncmd_iport) > 1:
                    pass


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
        params = [SymbolRef("inpt", ctypes.c_long())]
        return_type = ctypes.c_long()
        defn = [Return(BinaryOp(SymbolRef("inpt"), Op.Mul(), Constant(2)))]
        return FunctionDecl(return_type, self.func_name, params, defn)

    def get_func_def_vhdl(self):
        inport_info = [("FILTERMATRIX", VhdlType.VhdlArray(9, VhdlType.VhdlInteger, -20, 20, type_def="filtMASK")),
                       ("FILTER_SCALE", VhdlType.VhdlInteger()),
                       ("IMG_WIDTH", VhdlType.VhdlPositive()),
                       ("IMG_HEIGHT", VhdlType.VhdlPositive()),
                       ("IN_BITWIDTH", VhdlType.VhdlPositive()),
                       ("OUT_BITWIDTH", VhdlType.VhdlPositive()),
                       ("DATA_IN", "in", VhdlType.VhdlStdLogicVector(8))]
        outport_info = [("DATA_OUT", "out", VhdlType.VhdlStdLogicVector(8))]
        defn = VhdlComponent(name="bb_convolve",
                             generic_slice=slice(0,6),
                             delay=10,
                             inport_info=inport_info,
                             outport_info=outport_info,
                             library="work.Convolve")
        return defn


class BB_FuncTransformer(object):
    transformers = [BB_ConvolveTransformer]

    def __init__(self, backend="C"):
        self.backend = backend

    def visit(self, tree):
        for transformer in self.transformers:
            transformer(self.backend).visit(tree)
        return tree

    @staticmethod
    def lifted_functions():
        return BB_BaseFuncTransformer.lifted_functions
