"""Transformations."""
import ast
import logging
from collections import namedtuple
from collections import defaultdict
from itertools import izip_longest

from nodes import VhdlSyncNode
from nodes import VhdlConstant
from nodes import VhdlModule
from nodes import VhdlLibrary
from nodes import VhdlAnd
from nodes import PortInfo
from nodes import Port
from nodes import VhdlReturn
from nodes import VhdlSource
from nodes import VhdlNode
from nodes import VhdlSignal
from nodes import VhdlSink
from nodes import VhdlDReg
from nodes import VhdlSignalSplit
from nodes import VhdlConcatenation
from types import VhdlType
from utils import CONFIG
from utils import TransformationError
from vhdl_ctree.c.nodes import Op


logger = logging.getLogger(__name__)
logger.disabled = CONFIG.getboolean("logging", "DISABLE_LOGGING")
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


class VhdlBaseTransformer(object):
    """Base Transformer for the VHDL Back-End.

        This transformer coordinates all subtransformer necessary to transform and CTree AST
        into an valid VHDL IR AST.

        The currently implemented transformers are:
            - VhdlKwdTransformer
            - VhdlIRTransformer
            - VhdlGraphTransformer
            - VhdlPortTransformer
    """

    def __init__(self, ipt_params, lifted_functions):
        """Initialize transforer parameters."""
        self.ipt_params = ipt_params
        self.lifted_functions = lifted_functions

    def visit(self, tree):
        """Process tree with all transformers sequentially.

        :param tree: CTree IR ast

        .. note::
            Each transformer that should be applied to the tree must be called within this method
        """
        from src.vhdl_ctree.visual.dot_manager import DotManager
        img_path = "/home/philipp/University/M4/Masterthesis/src/VhdlSejits/vhdl_sejits/images/"
        # ----
        # DotManager().dot_ast_to_file(tree, file_name=img_path + "raw_tree")
        tree = VhdlKwdTransformer().visit(tree)
        # DotManager().dot_ast_to_file(tree, file_name=img_path + "kwd_trans_tree")
        tree = VhdlIRTransformer(self.ipt_params, self.lifted_functions).visit(tree)
        # DotManager().dot_ast_to_file(tree, file_name=img_path + "ir_trans_tree")
        tree = VhdlGraphTransformer().visit(tree)
        DotManager().dot_ast_to_file(tree, file_name=img_path + "graph_trans_tree")
        tree = VhdlPortTransformer().visit(tree)
        DotManager().dot_ast_to_file(tree, file_name=img_path + "port_trans_tree")
        return tree


class VhdlKwdTransformer(ast.NodeTransformer):

    """Transform SymbolRef nodes with VHDL keywords as name."""

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

    def visit_SymbolRef(self, node):
        """Change id of Name node if it is a VHDL keyword."""
        if node.name.lower() in self.VHDL_Keywords:
            node.name = "sig_" + node.name
        return node


class VhdlIRTransformer(ast.NodeTransformer):

    """Transform an CTree AST into an VDHL Intermediate Representation DAG.

        This transformer class is responsible for translating certain CTree nodes into VHDL IR nodes
        and changing the line-by-line AST structure of the input into an data flow DAG representation.
    """

    def __init__(self, ipt_param_types, lifted_functions, axi_stream_width=32):
        """
        :param ipt_param_types: type info for all kernel parameters
        :type ipt_param_types: list of VhdlType objects
        :param lifted_functions: function call specialized by DSL specializer transformer
        :type lifted_functions: list of VhdlComponent objects
        :param axi_stream_width: width of hardware accelerator interface in bits
        :type axi_stream_width: int
        """
        self.symbols = {}
        self.assignments = set()
        self.n_con_signals = defaultdict(int)
        self.axi_stream_width = axi_stream_width
        # prepare lifte functions from DSL transformer
        self.lifted_functions = lifted_functions
        self.lifted_function_names = {f.name for f in lifted_functions}
        #
        self.ipt_param_types = ipt_param_types if ipt_param_types is not None else []

    def _process_params(self, params):
        pparams = []
        #
        if len(self.ipt_param_types) != len(params):
            raise TransformationError("Number of input parameter typesdoes not match parameters: {0} expected, got {1}"
                                      .format(len(params), len(self.ipt_param_types)))
        #
        for param, p_type in zip(params, self.ipt_param_types):
            self.symbols[param.name] = VhdlSource(param.name, p_type if p_type is not None else param.vhdl_type)
            pparams.append(self.symbols[param.name])
        return pparams

    def visit_MultiNode(self, node):
        module = map(self.visit, node.body)
        return module[0]

    def visit_FunctionDecl(self, node):
        params = self._process_params(node.params)
        #
        body = map(self.visit, node.defn)
        # add return signal
        params.append(self.symbols["MODULE_OUT"])
        #
        libraries = [VhdlLibrary("ieee", ["ieee.std_logic_1164.all",
                                          "ieee.numeric_std.all"]),
                     VhdlLibrary(None, ["work.the_filter_package.all"])]
        #
        architecture = body[-1]  # add VhdlReturn component to architecture
        return VhdlModule(node.name, libraries, None, params, [architecture])

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
                left.vhdl_type = vhdl_node.outport_info[0].vhdl_type
                vhdl_node.out_port = [left]
            elif isinstance(right, VhdlConstant):
                vhdl_node = right
                vhdl_node.name = left.name
            elif isinstance(right, VhdlSource):
                vhdl_node = right
            else:
                raise TransformationError("Illegal assignment to symbol %s" % node.left.name)
            self.symbols[left.name] = vhdl_node
            self.assignments.add(left.name)
        else:
            raise TransformationError("Unknown Binary Operation")
        return vhdl_node

    def visit_SymbolRef(self, node):
        if node.name not in self.symbols:
            vhdl_sym = VhdlSignal(name=node.name,
                                  vhdl_type=VhdlType.VhdlStdLogicVector(self.axi_stream_width))
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

    def _connect(self, node):
        if isinstance(node, VhdlNode):
            # TODO: generate better indicator for connection
            if len(node.out_port) == 0:
                if hasattr(node, "name"):
                    name = node.name.upper() + "_OUT_"
                else:
                    name = node.__class__.__name__ + "_OUT_"
                #
                con_signal_number = self.n_con_signals[name]
                self.n_con_signals[name] += 1
                #
                con_signal = VhdlSignal(name=name + str(con_signal_number),
                                        vhdl_type=node.outport_info[0].vhdl_type)
                node.out_port.append(con_signal)
                self.symbols[con_signal.name] = con_signal
                return con_signal
            else:
                return node.out_port[0]
        else:
            return node


class VhdlGraphTransformer(ast.NodeTransformer):

    def __init__(self):
        self.con_edge_id = 0

    def visit_VhdlModule(self, node):
        map(self.visit, node.architecture)
        return node

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.retime(node)
        return node

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        self.retime(node)
        return node

    def visit_VhdlComponent(self, node):
        map(self.visit, node.prev)
        self.retime(node)
        return node

    def _retime_unsynced(self, node, max_d, norm_prev_d):
        """ Retime node without adding synchronization.

        :param node: active node
        :type node: VhdlNode subclass
        :param max_d: maximum edge delay
        :type max_d: int
        :param norm_prev_d: normalized delay to be added to each edge
        :type norm_prev_d: int
        """
        # retime each edge to match maximum delay
        for idx, prev, edge, d in zip(range(len(node.prev)), node.prev, node.in_port, norm_prev_d):
            if d > 0 and type(edge) is not VhdlConstant:
                # generate unique connection signal name
                c_id = self.con_edge_id
                self.con_edge_id += 1
                #
                con_edge = VhdlSignal(name=edge.name + "_DREG_" + str(c_id), vhdl_type=edge.vhdl_type)
                dreg = VhdlDReg(prev=[prev], delay=d, in_port=[edge], out_port=[con_edge])
                node.prev[idx] = dreg
                node.in_port[idx] = con_edge
        node.dprev = max_d

    def _retime_synced(self, node, max_d, norm_prev_d, sync_ds):
        """Retime node with synchronization

        :param node: active node
        :type node: VhdlNode subclass
        :param max_d: maximum edge delay
        :type max_d: int
        :param norm_prev_d: normalized delay to be added to each edge
        :type norm_prev_d: int
        :param sync_ds: list of synchronization delays, in essence the minimum buffer width necessary
        :type sync_ds: list of int

        .. todo:: Add handling of VhdlSyncNode delay, especially passing a varaiable delay to the orignal next node

        .. todo:: Consider default dict for connection edge id counter

        """
        sync_node = VhdlSyncNode(prev=None)
        sync_node_new_in_ports = []
        overall_in_ports = []
        overall_prev = []
        # retime and synchronize each edge to match maximum delay
        for idx, prev, edge, d in zip(range(len(node.prev)), node.prev, node.in_port, norm_prev_d):
            if type(edge) is not VhdlConstant:
                if d > 0:
                    # generate unique connection signal name
                    c_id = self.con_edge_id
                    self.con_edge_id += 1
                    #
                    con_edge = VhdlSignal(name=edge.name + "_DREG_" + str(c_id), vhdl_type=edge.vhdl_type)
                    dreg = VhdlDReg(prev=[prev], delay=d, in_port=[edge], out_port=[con_edge])
                    sync_node.prev.append(dreg)
                    sync_node_new_in_ports.append(con_edge)
                else:
                    sync_node.prev.append(prev)
                    sync_node_new_in_ports.append(edge)
                overall_in_ports.append(None)
                overall_prev.append(None)
            else:
                overall_prev.append(prev)
                overall_in_ports.append(edge)
        # append data for generics WIDTH and N_IO
        generic_data = [len(sync_node_new_in_ports[0].vhdl_type), len(sync_node_new_in_ports), max(sync_ds)]
        generic_data = [VhdlConstant("", VhdlType.VhdlPositive(), gd) for gd in generic_data]
        sync_node.in_port.extend(generic_data)
        # append inports to sync node
        sync_node.in_port.append(VhdlConcatenation(sync_node_new_in_ports))

        # create sync_node output
        c_id = self.con_edge_id
        self.con_edge_id += 1
        con_size = sync_node.in_port[-1].vhdl_type.size
        sync_output_edge = VhdlSignal(name="SYNC_NODE_OUT_" + str(c_id),
                                      vhdl_type=VhdlType.VhdlStdLogicVector(size=con_size))
        sync_node.out_port.append(sync_output_edge)

        # connect sync_node with active node
        sig_sync_idx = 0
        sig_width_cnt = 0
        for idx, port in enumerate(overall_in_ports):
            if port is None:
                s_min = sig_width_cnt
                s_max = sig_width_cnt + sync_node_new_in_ports[sig_sync_idx].vhdl_type.size
                node.in_port[idx] = VhdlSignalSplit(sync_output_edge, slice(s_min, s_max))
                sig_width_cnt += sync_node_new_in_ports[sig_sync_idx].vhdl_type.size
                sig_sync_idx += 1
            else:
                node.in_port[idx] = port

        node.dprev = max_d
        overall_prev = [prev for prev in overall_prev if prev is not None]
        node.prev = [sync_node] + overall_prev

    def retime(self, node):
        need_sync = False
        sync_ds = []
        prev_d = []
        for prev in node.prev:
            try:
                prev_d.append(prev.d + prev.dprev)
            except TypeError:
                """ Detected node with variable delay"""
                prev_d.append(prev.d[0] + prev.dprev)
                need_sync = True
                sync_ds.append(prev.d[1] - prev.d[0])
        max_d = max(prev_d)
        # normalize delay by calculating difference to maximum edge delay
        norm_prev_d = [max_d - d for d in prev_d]
        #
        if need_sync:
            self._retime_synced(node, max_d, norm_prev_d, sync_ds)
        else:
            self._retime_unsynced(node, max_d, norm_prev_d)


class VhdlPortTransformer(ast.NodeVisitor):

    def __init__(self, icps_info=None, iccps_info=None, occps_info=None):
        # ICP - Input Command Ports
        if icps_info is not None:
            self.icps_info = icps_info
        else:
            self.icps_info = [PortInfo("CLK", "in", VhdlType.VhdlStdLogic()),
                              PortInfo("RST", "in", VhdlType.VhdlStdLogic())]

        # ICCP - Input Cascading Command Ports
        if iccps_info is not None:
            self.iccps_info = iccps_info
        else:
            self.iccps_info = [PortInfo("VALID_IN", "in", VhdlType.VhdlStdLogic()),
                               PortInfo("READY_IN", "in", VhdlType.VhdlStdLogic())]

        # OCCP - Output Cascading Command Ports
        if occps_info is not None:
            self.occps_info = occps_info
        else:
            self.occps_info = [PortInfo("VALID_OUT", "out", VhdlType.VhdlStdLogic()),
                               PortInfo("READY_OUT", "out", VhdlType.VhdlStdLogic())]

        self.cpe_id = defaultdict(int)  # command port edge ID

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
        map(self.visit, node.architecture)
        self.finalize_ports(node)
        return node

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)
        return node

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)
        return node

    def visit_VhdlComponent(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)
        return node

    def visit_VhdlDReg(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)
        return node

    def visit_VhdlSyncNode(self, node):
        map(self.visit, node.prev)
        self.finalize_ports(node)
        # add concacenation of valid in signals to ports
        valid_in = None
        for p in node.in_port:
            if p.name == "VALID_IN":
                valid_in = p
            else:
                pass

        valid_con_sig = VhdlConcatenation(valid_in.value.list)
        # Port = namedtuple("Port", ["name", "direction", "vhdl_type", "value"])
        valid_con_port = Port(name="VALID_IN_PORT", direction="in",
                              vhdl_type=VhdlType.VhdlStdLogicVector(size=len(valid_con_sig)),
                              value=valid_con_sig)
        node.in_port.append(valid_con_port)
        #
        return node

    def finalize_ports(self, node):
        # Finalize Generic, In- and Out-Ports
        node.finalize_ports()
        #
        iccps = []
        idxs = range(len(self.iccps_info))

        if isinstance(node, VhdlModule):
            # Just add command ports to Module
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
                            cc_edges.append(cc_edge)
                        else:
                            if hasattr(pnode, "name"):
                                name = pnode.name.upper() + "_" + occp.name + "_"
                            else:
                                name = pnode.__class__.__name__ + "_" + occp.name + "_"
                            #
                            con_signal_number = self.cpe_id[name]
                            self.cpe_id[name] += 1
                            #
                            n = name + str(con_signal_number)
                            cc_edge = VhdlSignal(name=n, vhdl_type=occp.vhdl_type)
                            poccps.append(Port(occp.name, occp.direction, occp.vhdl_type, cc_edge))
                            cc_edges.append(cc_edge)
                        # finalize previous nodes out_port
                        pnode.out_port = poccps + pnode.out_port
                    else:  # VhdlSymbol Class
                        if isinstance(pnode, VhdlSource):
                            # add vhdl modules command port
                            cc_edge = VhdlSignal(iccp.name, iccp.vhdl_type)
                            cc_edges.append(cc_edge)
                # add cascading input command ports to iccps
                iccps.append(Port(iccp.name, iccp.direction, iccp.vhdl_type, cc_edges))
            # add all visited nodes to hash storage
            for pnode in node.prev:
                self.visited_nodes.add(hash(pnode))
            # Add Cascading Command, Command and In-Ports
            node.in_port = self.icps + iccps + node.in_port

            if isinstance(node, VhdlReturn):
                # Add Cascading Command and Out-Ports
                node.out_port = self.occps + node.out_port
