""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import logging

from sejits_ctree.vhdl import TransformationError
from sejits_ctree.vhdl.utils import CONFIG
from collections import namedtuple
from nodes import VhdlType
#
from nodes import VhdlBinaryOp, VhdlComponent, VhdlConstant, VhdlModule, VhdlReturn, VhdlSource, VhdlNode, VhdlSignal
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
        return VhdlModule("TEST", params, body[-1])

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
                                     next=[],
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


class ADag_BaseNode(ast.AST):
    """Acyclic DAG node base class."""
    def __init__(self, node):
        try:
            self.d = node.delay
        except AttributeError as ae:
            """Report missing attribute."""
            missing_aname = ae.message.split("'")[1::2][-1]
            error_msg = "Node {0} has no object attribute {1}"\
                .format(node, missing_aname)
            raise TransformationError(error_msg)
        self.prev_d = 0
        self.vhdl_node = node

class ADag_Node(ADag_BaseNode):
    """Acyclic DAG Node class."""
    def __init__(self, node, prev, next=[]):
        super(ADag_Node, self).__init__(node)
        self.prev = prev
        self.next = next

class ADag_DReg(ADag_Node):
    """Acyclic DAG Node class."""
    def __init__(self, node, prev, next=[]):
        super(ADag_DReg, self).__init__(node, prev, next)

class ADag_Constant(ADag_BaseNode):
    """Acyclic DAG constant node class."""
    def __init__(self, next=[]):
        self.d = 0
        self.prev_d = 0
        self.next = next

class ADag_Source(ADag_BaseNode):
    """Acyclic DAG source node class."""
    def __init__(self, next=[]):
        self.d = 0
        self.prev_d = 0
        self.next = next

class ADag_Sink(ADag_BaseNode):
    """Acyclic DAG sink node class."""
    def __init__(self, node, prev=[]):
        super(ADag_Sink, self).__init__(node)
        self.prev = prev

# =====================================================================================================================
# TODO: Remove and implement DUMMY classes
# =====================================================================================================================

class SourceNode(object):
    delay = 0

class ConstantNode(object):
    delay = 0

# =====================================================================================================================

class VhdlDag(ast.NodeVisitor):

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        self.add_node(node)

    def retime(self, node):
        """Retime all previous edges and update next attribute.

            An edge in the ADAG is identical with a constant or signal in the
                VHDL Ast, connecting two components.

            - Calculate sum of delay and previous delay of each previous node
                --> sum(node.delay + node.prev_delay) = edge delay (e_dlay)
            - Calculate max(e_dlays) - e_dlay for every e_dlay


            Retime only if max(e_dlays) - e_dlay > 0:
            Step 1):    |node n-1|-->|node|
            Step 2):    |node n-1|-->|DReg|-->  |node|
                - Generate additional connection edge
                - Generate and configure DReg
                - Connect prev_node with original edge to DREG
                - Save connection edge and DReg
            Step 3):    |node n-1|-->|DReg|-->|node|
                - Connect DReg with connection edge to node
        """
        # get accumulated delay of every input edge
        e_dlays = [pn.d + pn.prev_d for pn in node.prev]
        max_e_dlay = max(e_dlays)
        e_dlays = [max_e_dlay - e_d for e_d in e_dlays]

        # retime every edge to match maximum delay
        updated_edges = []
        for edge_idx, d in enumerate(e_dlays):
            if d > 0:
                # generate additional connection signal from dreg-->node
                con_edge = deepcopy(node.prev[edge_idx].out_sig)
                con_edge.name = con_edge.name + "_dreg"

                # generate dreg and link to previous node
                dreg = VhdlDReg(delay=Generic("DELAY", VhdlType.VhdlSigned,
                                          Constant("", VhdlType.VhdlSigned, d)),
                                i_port=Port("DREG_IN", "in",
                                            node.prev[edge_idx].out_sig),
                                o_port=Port("DREG_OUT", "out",
                                            con_edge))
                adag_dreg = ADag_DReg(dreg, node.prev[edge_idx])

                # update ADAG
                node.prev[edge_idx].next.append(adag_dreg)
                node.prev[edge_idx] = adag_dreg

                # save con_edge and d_reg
                self.con_edges.append(con_edge)
                self.dregs.append(dreg)

                # add signals to update VHDL nodes
                updated_edges.append((edge_idx, con_edge))
            else:
                node.prev[edge_idx].next.append(node)

        # connect all added DRegs with vhdl_node
        self._update_iports(node, updated_edges)

    def _update_iports(self, node, updated_edges):
        """Update in_ports of vhdl_node to connect all DRegs."""
        # get nodes in_ports without cmd_ports
        in_ports = list(node.vhdl_node.in_ports[3:])
        # update all neccessary in_ports
        for updated_edge in updated_edges:
            updated_port = in_ports[edge_idx]
            updated_port.value = updated_edge
            in_ports[edge_idx] = updated_port
        # update nodes in_ports
        node.vhdl_node.in_ports = in_ports



class VhdlADag(ast.NodeVisitor):

    def __init__(self, sources, constants):
        # n_nodes contains number of nodes in acyclic DAG
        self.n_nodes = 0
        # nodes_hashdict contains all nodes with hash(node):node
        self.nodes_hashdict = {}
        # initialize source and constant nodes
        for source in sources:
            self.nodes_hashdict[hash(source)] = ADag_Source()

        for constant in constants:
            self.nodes_hashdict[hash(constant)] = ADag_Constant()
        #
        self.con_edges = []
        self.dregs = []
        # initialize dag root and head node
        self.source_nodes = None
        self.head_node = None

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        self.add_node(node)

    def add_node(self, node):
        """
            Add vhdl node to acyclic DAG.

            If Return:
                Add acyclic DAG sink node and add previous nodes to ADAG node
            Else (BinaryOp/Component):
                Add acyclic DAG node, add previous nodes to ADAG node and
                register output edges of node

            Attributes:
                node: VHDL node to add to ADAG
        """
        if isinstance(node, VhdlReturn):
            # generate sink node from node
            prev_edges, nxt_edges = self._extract_edges(node)
            prev_nodes = self._resolve_edges(prev_edges)
            #
            adag_node = ADag_Sink(node, prev_nodes)
        else:
            # extract node parameter
            prev_edges, nxt_edges = self._extract_edges(node)
            prev_nodes = self._resolve_edges(prev_edges)
            self._register_edges(nxt_edges, node)  # register output edges
            #
            adag_node = ADag_Node(node, prev_nodes)

        # retime adag node
        self.retime(adag_node)
        # save adag node
        self.nodes_hashdict[hash(node)] = adag_node
        # update head
        self.head_node = adag_node

    def _extract_edges(self, node):
        """Extract all in and output edges of node.
        :param node: VhdlNode
        :raises TransformationError: raised node has no attribute in_ports/out_ports
        :raises TransformationError: raised when number of output_edges != 1
        :return: tuple of (previous_edges, next_edges)
        :rtype: tuple
        """
        try:
            prev = node.in_ports
            nxt = node.out_ports
        except AttributeError as ae:
            """Report missing attribute."""
            missing_aname = ae.message.split("'")[1::2][-1]
            error_msg = "Node {0} of type {1} has no object attribute {2}"\
                .format(node, type(node), missing_aname)
            raise TransformationError(error_msg)
        else:
            # extract port values
            prev = [port.value for port in prev]
            nxt = [port.value for port in nxt]

        # assert if node has only one output
        if len(nxt) != 1:
            error_msg = "Node has {0} output edges, only 1 supported".\
                format(len(nxt))
            raise TransformationError(error_msg)

        return (prev, nxt)

    def _resolve_edges(self, prev_edges):
        """Retrieve previous nodes from nodes_hashdict via hash(edge).
        :param prev_edges: list of previous edges
        :raises TransformationError: raised when prev_edge not in nodes_hashdict
        :return: list of previous nodes for current node
        :rtype: list
        """
        try:
            prev_nodes = [self.nodes_hashdict[hash(pnode)] for pnode in prev_edges[3:]]
        except KeyError as ke:
            """Report missing edges."""
            missing_key = ke.message.split("'")[1::2][-1]
            error_msg = "No target node for edge with hash {0} found"\
                .format(missing_key)
            raise TransformationError(error_msg)
        else:
            return prev_nodes

    def _register_edges(self, nxt_edges, node):
        """Register key:value of hash(nxt_edge):node.
        :param nxt_edges: list of next edges
        :param node: ADAG node
        """
        for nxt_edge in nxt_edges:
            self.nodes_hashdict[hash(nxt_edge)] = node

    def retime(self, node):
        """Retime all previous edges and update next attribute.

            An edge in the ADAG is identical with a constant or signal in the
                VHDL Ast, connecting two components.

            - Calculate sum of delay and previous delay of each previous node
                --> sum(node.delay + node.prev_delay) = edge delay (e_dlay)
            - Calculate max(e_dlays) - e_dlay for every e_dlay


            Retime only if max(e_dlays) - e_dlay > 0:
            Step 1):    |node n-1|-->|node|
            Step 2):    |node n-1|-->|DReg|-->  |node|
                - Generate additional connection edge
                - Generate and configure DReg
                - Connect prev_node with original edge to DREG
                - Save connection edge and DReg
            Step 3):    |node n-1|-->|DReg|-->|node|
                - Connect DReg with connection edge to node
        """
        # get accumulated delay of every input edge
        e_dlays = [pn.d + pn.prev_d for pn in node.prev]
        max_e_dlay = max(e_dlays)
        e_dlays = [max_e_dlay - e_d for e_d in e_dlays]

        # retime every edge to match maximum delay
        updated_edges = []
        for edge_idx, d in enumerate(e_dlays):
            if d > 0:
                # generate additional connection signal from dreg-->node
                con_edge = deepcopy(node.prev[edge_idx].out_sig)
                con_edge.name = con_edge.name + "_dreg"

                # generate dreg and link to previous node
                dreg = VhdlDReg(delay=Generic("DELAY", VhdlType.VhdlSigned,
                                          Constant("", VhdlType.VhdlSigned, d)),
                                i_port=Port("DREG_IN", "in",
                                            node.prev[edge_idx].out_sig),
                                o_port=Port("DREG_OUT", "out",
                                            con_edge))
                adag_dreg = ADag_DReg(dreg, node.prev[edge_idx])

                # update ADAG
                node.prev[edge_idx].next.append(adag_dreg)
                node.prev[edge_idx] = adag_dreg

                # save con_edge and d_reg
                self.con_edges.append(con_edge)
                self.dregs.append(dreg)

                # add signals to update VHDL nodes
                updated_edges.append((edge_idx, con_edge))
            else:
                node.prev[edge_idx].next.append(node)

        # connect all added DRegs with vhdl_node
        self._update_iports(node, updated_edges)

    def _update_iports(self, node, updated_edges):
        """Update in_ports of vhdl_node to connect all DRegs."""
        # get nodes in_ports without cmd_ports
        in_ports = list(node.vhdl_node.in_ports[3:])
        # update all neccessary in_ports
        for updated_edge in updated_edges:
            updated_port = in_ports[edge_idx]
            updated_port.value = updated_edge
            in_ports[edge_idx] = updated_port
        # update nodes in_ports
        node.vhdl_node.in_ports = in_ports

    def finalize(self):
        """Retime acyclic DAG and return additional signals."""
        _rec_finalize(self.head_node, None)

    @staticmethod
    def _rec_finalize(node, next_node):
        """Recusively traverse ADAG from head and update next attribute."""
        try:
            node.next.append(next_node)
        except AttributeError as ae:
            if not isinstance(node, ADag_Sink):
                """Report missing attribute."""
                missing_aname = ae.message.split("'")[1::2][-1]
                error_msg = "Node {0} of type {1} has no object attribute {0}"\
                    .format(node, type(node), missing_aname)
                raise TransformationError(error_msg)

        if hasattr(node, "prev"):
            # node is ADAG node
            for prev_node in node.prev:
                _rec_finalize(prev_node, node)
        else:  # reached Source/Constant node
            return
