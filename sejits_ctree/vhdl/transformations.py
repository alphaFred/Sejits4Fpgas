""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import itertools

from sejits_ctree.vhdl import TransformationError
import logging

from collections import namedtuple

from nodes import VhdlFile
from nodes import Entity, Architecture
from nodes import Op, Signal, Constant, Generic, Port
from nodes import UnaryOp, BinaryOp, Component
from nodes import Expression, Literal

from nodes import VhdlType

from basic_blocks import BASICBLOCKS
from user.nodes import UserNode


logger = logging.getLogger('test_transformer')

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
        ast.Add: Op.Add,
        ast.Mult: Op.Mul,
        ast.Sub: Op.Sub,
        ast.Div: Op.Div,
        ast.Pow: Op.Pow,
        "sqrt": Op.Sqrt
    }

    def __init__(self, names_dict={}, constants_dict={}, libs=[], bit_width=8):
        """ Initialize the VhdlBasicTransformer. """
        logger.debug("VhdlTransformer initialized")

        self.names_dict = names_dict
        self.constants_dict = constants_dict
        self.libs = libs
        # add dependency for binary operations
        basic_arith_blocks_lib = VhdlFile(path="/home/philipp/University/M4/Masterthesis/src/git_repo/ebensberger_ma/BasicArithBlocks.vhd")
        basic_arith_blocks_lib.generated = False
        self.dependencies.append(basic_arith_blocks_lib)
        #
        self.bit_width = bit_width

    def visit_Module(self, node):
        """ Visit Module node and return VhdlFile. """
        entity, architecture = self.visit(node.body[0])
        #
        return VhdlFile(name=entity.name,
                        libs=self.libs,
                        entity=entity,
                        architecture=architecture,
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
                                vhdl_type=obj.out_type)
            obj.out_port = Port("return_sig", "out", con_signal)
            #
            self.architecture_int_signals[con_signal.name] = con_signal
            return con_signal
        else:
            error_msg = "Trying to connect invalid object of type %s"\
                        % type(obj)
            raise TransformationError(error_msg)


    def visit_BinOp(self, node):
        op = self.PY_OP_TO_VHDL_OP[type(node.op)]()
        left, right = [self.create_connection(self.visit(arg))
                       for arg in [node.left, node.right]]
        #
        ret_comp = BinaryOp(left_port=Port("left", "in", left),
                            op=Generic("op", op),
                            right_port=Port("right", "in", right))
        self.arch_components.append(ret_comp)
        return ret_comp

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
        #

        if isinstance(value, Literal):
            if type(value) is Constant:
                value.name = target.id
                self.architecture_int_signals[target.id] = value
            else:
                self.architecture_temp_signals[target.id] = value
        elif isinstance(value, Expression):
            if isinstance(target, ast.Name):
                out_sig = Signal(name=target.id, vhdl_type=value.out_type)
                #
                self.architecture_int_signals[target.id] = out_sig
                #
                if value.out_port:
                    value.out_port.value = out_sig
                else:
                    value.out_port = Port("return_sig", "out", out_sig)
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
            out_sig = Signal("return_sig", value.out_type)
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
