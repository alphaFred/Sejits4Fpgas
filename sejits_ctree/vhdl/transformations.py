""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import itertools

from sejits_ctree.vhdl import TransformationError
from sejits_ctree.vhdl.utils import CONFIG
import logging

from collections import namedtuple

from nodes import VhdlFile
from nodes import Entity, Architecture
from nodes import Op, Signal, Constant, Generic, Port
from nodes import BinaryOp, Component
from nodes import Expression, Literal

from nodes import VhdlType

from basic_blocks import BASICBLOCKS
from user.nodes import UserNode


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

UNARY_OPs = {"sqrt": UNARY_OP(["i_sig"], ["o_sig"]),
             "pow": UNARY_OP(["i_sig"], ["o_sig"])}


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

    """ Transform Python AST to Vhdl AST. """

    # TODO: refactor class variables
    # contains all additionaly created vhdl files while parsing
    dependencies = []

    # contains all components of the architecture
    arch_components = []

    # contains all nested components of architecture
    architecture_body_additions = []

    # contains all input/output signals defined by entity of architecture
    architecture_io_signals = {}

    # contains all architecture internal signals/constants
    architecture_int_signals = {}

    architecture_temp_signals = {}

    PY_OP_TO_VHDL_OP = {
        ast.Add: Constant("", VhdlType.VhdlInteger(), 0),
        ast.Sub: Constant("", VhdlType.VhdlInteger(), 1),
        ast.Mult: Constant("", VhdlType.VhdlInteger(), 2),
    }

    def __init__(self, names_dict={}, constants_dict={}, libs=[], bit_width=8):
        """ Initialize the VhdlBasicTransformer. """

        # ---------------------------------------------------------------------
        # LOGGING
        # ---------------------------------------------------------------------
        log_data = [['names_dict', str(names_dict)],
                    ['constants_dict', str(constants_dict)],
                    ['libs', str(libs)],
                    ['bit_width', str(bit_width)]]
        col_width = max(len(row[0]) for row in log_data) + 2  # padding
        log_txt = "\n".join(["".join(word.ljust(col_width) for word in row) for row in log_data])
        logger.debug("Initialized {0}: \n{1}".format(self.__class__.__name__, log_txt))
        # ---------------------------------------------------------------------

        self.names_dict = names_dict
        self.constants_dict = constants_dict
        self.libs = libs
        # add dependency for binary operations

        # TODO: define path global in configuration
        path = "/home/philipp/University/M4/Masterthesis/src/git_repo/" + \
               "ebensberger_ma/BasicArithBlocks.vhd"
        # basic_arith_blocks_lib = VhdlFile(path)
        # basic_arith_blocks_lib.generated = False
        # self.dependencies.append(basic_arith_blocks_lib)
        #
        self.bit_width = bit_width

    def visit_Module(self, node):
        """ Visit Module node and return VhdlFile. """
        entity, architecture = self.visit(node.body[0])
        #
        logger.info("Generated VhdlFile {0}".format(entity.name))
        return VhdlFile(name=entity.name,
                        libs=self.libs,
                        entity=entity,
                        architecture=architecture,
                        path="./",
                        dependencies=self.dependencies)

    def visit_FunctionDef(self, node):
        """ Visit FunctionDef node and return [Entity, Architecture]. """
        # visit FunctionDef body
        in_args = []
        for arg in node.args.args:
            arg_sig = self.visit(arg)
            self.architecture_io_signals[arg.id] = arg_sig
            in_args.append(Port(arg.id, "in",
                                self.architecture_io_signals[arg.id]))
        # Visit all body elements
        for body_elem in node.body:
            self.visit(body_elem)

        out_port = Port("return_sig", "out",
                        self.architecture_io_signals["return_sig"])

        # get architecture internal signals
        arch_signals = self.architecture_int_signals.values()

        # generate Entity and Architecture
        entity = Entity(name=node.name,
                        generics=[],
                        in_ports=in_args,
                        out_ports=[out_port])

        architecture = Architecture(entity_name=node.name,
                                    signals=arch_signals,
                                    components=self.arch_components)
        return (entity, architecture)

    def visit_Name(self, node):
        """
        Visit Name node, return Signal node.

        If node.id is in names_dict, architecture_io_signals or
        architecture_int_signals, return cached Signal. Otherwise create a new
        Signal instance.

        Attributes:
            node: ast.Name node
        Return:
            Signal node
        """
        if node.id in self.names_dict:
            return self.names_dict[node.id]
        elif node.id in self.architecture_io_signals:
            return self.architecture_io_signals[node.id]
        elif node.id in self.architecture_int_signals:
            return self.architecture_int_signals[node.id]
        elif node.id in self.architecture_temp_signals:
            return self.architecture_temp_signals[node.id]
        else:
            ret_signal = Signal(name=node.id)
            # save internal architecture signal
            self.architecture_int_signals[node.id] = ret_signal
            return ret_signal

    def visit_Num(self, node):
        """
        Visit Num node, return Constant node.

        Attributes:
            node: ast.Num node
        Return:
            Constant node
        """
        if type(node.n) is int:
            # TODO: find smallest bit representation of integer for size
            if node.n < 0:
                return Constant(name="",
                                vhdl_type=VhdlType.VhdlSigned(size=self.bit_width),
                                value=node.n)
            else:
                return Constant(name="",
                                vhdl_type=VhdlType.VhdlUnsigned(self.bit_width),
                                value=node.n)
        else:
            error_msg = "Unsupported type {0}".format(type(node.n))
            raise TransformationError(error_msg)

    def visit_Str(self, node):
        return Constant(name="",
                        vhdl_type=VhdlType.VhdlStr(),
                        value=node.s)

    def visit_Tuple(self, node):
        # Tuple(expr* elts, expr_context ctx)
        itms = [self.visit(itm) for itm in node.elts]
        return Constant(name="",
                        vhdl_type=VhdlType.VhdlArray.from_list(itms),
                        value="(" + ",".join(str(itm.value) for itm in itms) + ")")

    def visit_List(self, node):
        itms = [self.visit(itm) for itm in node.elts]
        #
        return Constant(name="",
                        vhdl_type=VhdlType.VhdlArray.from_list(itms),
                        value="(" + ",".join(str(itm.value) for itm in itms) + ")")

    def visit_Call(self, node):
        """
        Visit Call node and return Component.

        Check whether node.func is an instance of ast.FunctionDef, hence a
        call previously transformed by a user, or not.

        A user transformed call delivers information about the port names and
        return type. A generic call will be returned with "comp_dummy" as
        its name and enumerated port names (in_sig0, in_sig1 ...).
        The return type of an generic call is equal to the type of the first
        in_port.

        Attributes:
            node: ast.Call node
        Return:
            Component node
        """
        if isinstance(node.func, UserNode):
            """ Resolve user transformed call. """
            # TODO: add additional information for logger
            logger.info("UserNode processed")
            #
            node.func.generated = False
            self.dependencies.append(node.func)
            ret_comp = None
        else:
            if node.func.id in BASICBLOCKS:
                basic_block = BASICBLOCKS[node.func.id]
                # visit arguments and create connection signals if neccessary
                _in_args = [self.create_connection(self.visit(arg)) for arg in node.args]
                # _in_args has to contain only Signals/Constants
                basic_file = basic_block(_in_args)
                ret_comp = basic_file.component
                # add new basic block to dependency file list
                self.dependencies.append(basic_file)
            else:
                raise TransformationError("Unknown function %s called" % node.func.id)
        self.arch_components.append(ret_comp)
        return ret_comp

    def create_connection(self, obj):
        if isinstance(obj, Literal):
            return obj
        elif isinstance(obj, Expression):
            con_signal = Signal(name=obj.instance_name + "_return",
                                vhdl_type=obj.out_types)
            obj.out_port = Port("return_sig", "out", con_signal)
            #
            self.architecture_int_signals[con_signal.name] = con_signal
            return con_signal
        else:
            error_msg = "Trying to connect invalid object of type %s"\
                        % type(obj)
            raise TransformationError(error_msg)

    def visit_BinOp(self, node):
        op = self.PY_OP_TO_VHDL_OP[type(node.op)]
        left, right = [self.create_connection(self.visit(arg))
                       for arg in [node.left, node.right]]
        #
        ret_comp = BinaryOp(left_port=Port("left", "in", left),
                            op=Generic("op", op),
                            right_port=Port("right", "in", right))
        self.arch_components.append(ret_comp)
        return ret_comp

    def visit_BinaryOp(self, node):
        print "visited BinaryOp"
        pass

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = self.PY_OP_TO_VHDL_OP[type(node.op)]
        #
        if isinstance(operand, Literal):
            pass
            # TODO: implement Literal handling
        elif isinstance(operand, Expression):
            # Create additional connection signal
            con_signal = Signal(name=operand.instance_name + "_return",
                                vhdl_type=operand.out_type)
            operand.out_port = Port("return_sig", "out", con_signal)
            #
            self.architecture_int_signals[con_signal.name] = con_signal
            operand = con_signal
        #
        ret_comp = UnaryOp(in_port=Port("operand", "in", operand),
                           op=Generic("op", op))
        self.arch_components.append(ret_comp)
        return ret_comp

    def visit_Assign(self, node):
        """
        Visit Assign node and add target as out_arg to value.

        Attributes:
            node: ast.Assign node
        """
        value = self.visit(node.value)
        #
        if len(node.targets) != 1:
            raise TransformationError("Only one assignment target supported")
        target = node.targets[0]
        #

        # TODO: optimize reassignment check
        error_msg = "Reassignment of {0} in line {1} is not supported"\
            .format(target.id, node.lineno)
        if target.id in self.names_dict:
            raise TransformationError(error_msg)
        elif target.id in self.architecture_io_signals:
            raise TransformationError(error_msg)
        elif target.id in self.architecture_int_signals:
            raise TransformationError(error_msg)
        elif target.id in self.architecture_temp_signals:
            raise TransformationError(error_msg)
        else:
            pass

        if isinstance(value, Literal):
            if type(value) is Constant:
                value.name = target.id
                self.architecture_int_signals[target.id] = value
            else:
                self.architecture_temp_signals[target.id] = value
        elif isinstance(value, Expression):
            if isinstance(target, ast.Name):
                out_sig = Signal(name=target.id, vhdl_type=value.out_types)
                #
                self.architecture_int_signals[target.id] = out_sig
                #
                if value.out_ports:
                    value.out_ports.value = out_sig
                else:
                    value.out_ports = Port("return_sig", "out", out_sig)
                return value
            else:
                error_msg = "Undefined assignment to %s" % type(target)
                raise TransformationError(error_msg)
        else:
            error_msg = "Undefined assignment of {1} to {2}".format(type(value), type(target))
            raise TransformationError(error_msg)

    def visit_Return(self, node):
        """ Visit Return node and add Vhdl Return. """
        value = self.visit(node.value)
        #
        # VhdlReturn(in_port, out_port)
        #
        if isinstance(value, Literal):
            self.architecture_io_signals["return_sig"] = value
        elif isinstance(value, Expression):
            out_sig = Signal("return_sig", value.out_types)
            value.out_port = Port("return_sig", "out", out_sig)
            #
            self.architecture_int_signals["return_sig"] = out_sig
            self.architecture_io_signals["return_sig"] = out_sig
        else:
            raise TransformationError("Node value has undefined instance")

    def visit_Expr(self, node):
        """
        Visit Expr node, return None if string else return node value.

        Attributes:
            node: Python AST tree or node
        """
        if hasattr(node, "value"):
            if isinstance(node.value, ast.Str):
                return None
            else:
                return self.visit(node.value)
        else:
            # TODO: check again for correctness
            return None

    def visit_UserCodeTemplate(self, node):
        pass

    def visit_UserFileTemplate(self, node):
        pass


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
