""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
from sejits_ctree.vhdl import USERTRANSFORMERS
import logging

from collections import namedtuple

from sejits_ctree.vhdl.nodes import VhdlFile
from sejits_ctree.vhdl.nodes import Entity, Architecture
from sejits_ctree.vhdl.nodes import Op, Signal, Constant, Generic, Port
from sejits_ctree.vhdl.nodes import UnaryOp, BinaryOp, Component, VhdlReturn
from sejits_ctree.vhdl.nodes import Expression

from sejits_ctree.vhdl.user.nodes import UserNode


logger = logging.getLogger('test_transformer')

UNARY_OP = namedtuple("UNARY_OP", ["i_args", "out_arg"])

BASIC_COMPONENTS = ({"vhdl_convolve"})
UNARY_OPs = {"sqrt": UNARY_OP(["i_sig"], ["o_sig"]),
             "pow": UNARY_OP(["i_sig"], ["o_sig"])}


class TransformationError(Exception):

    """
    Exception that caused transformation not to occur.

    Attributes:
      msg -- the message/explanation to the user
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


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
                      "use", "variable", "wait", "when", "while", "with",
                      "xnor", "xor"})

    def visit_Name(self, node):
        """ Change id of Name node if it is a VHDL keyword. """
        if node.id in self.VHDL_Keywords:
            node.id = "sig_" + node.id
        return node


class VhdlTransformer(ast.NodeTransformer):

    """ Transform Python AST to Vhdl AST. """

    # contains all additionaly created vhdl files while parsing
    vhdl_files = []

    # contains all components of the architecture
    arch_components = []

    # contains all nested components of architecture
    architecture_body_additions = []

    # contains all input/output signals defined by entity of architecture
    architecture_io_signals = {}

    # contains all architecture internal signals/constants
    architecture_int_signals = {}

    PY_OP_TO_VHDL_OP = {
        ast.Add: Op.Add,
        ast.Mult: Op.Mul,
        ast.Sub: Op.Sub,
        ast.Div: Op.Div,
    }

    def __init__(self, names_dict={}, constants_dict={}):
        """ Initialize the VhdlBasicTransformer. """
        logger.debug("VhdlTransformer initialized")

        self.names_dict = names_dict
        self.constants_dict = constants_dict

    def visit_Module(self, node):
        """ Visit Module node and return VhdlFile. """
        entity, architecture = self.visit(node.body[0])
        #
        return VhdlFile(name=entity.name,
                        entity=entity,
                        architecture=architecture)

    def visit_FunctionDef(self, node):
        """ Visit FunctionDef node and return [Entity, Architecture]. """
        # visit FunctionDef body
        in_args = []
        for arg in node.args.args:
            arg_sig = self.visit(arg)
            self.architecture_io_signals[arg.id] = arg_sig
            in_args.append(Port(arg.id, "in",
                                self.architecture_io_signals[arg.id]))

        body = [self.visit(body) for body in node.body]
        body = body + self.architecture_body_additions
        out_arg = Port("return", "out",
                       self.architecture_io_signals["return_sig"])

        # get architecture internal signals
        arch_signals = self.architecture_int_signals.values()

        # generate Entity and Architecture
        entity = Entity(name=node.name,
                        generics=[],
                        in_ports=in_args,
                        out_port=out_arg)

        architecture = Architecture(entity_name=node.name,
                                    signals=arch_signals,
                                    body=body,
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
        # TODO: transform type to VhdlType instance
        return Constant(name="",
                        vhdl_type=node.n.__class__.__name__,
                        value=node.n)

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

            comp_name = ""
            comp_generics = None
            comp_iports = None
            comp_oport = None
            comp_outtype = None

            comp_name = node.func.name
            comp_generics = None
            #
            intf = node.func.interface
            #
            comp_iports = intf.iports
            comp_oport = intf.oport
            comp_outtype = comp_oport.value.vhdl_type
            #
            node.func.codegenflag = "imported"
            self.vhdl_files.append(node.func)
        else:
            """ Resolve ordinary call. """
            comp_name = node.func.id

            in_args = [self.visit(arg) for arg in node.args]
            comp_iports = [Port("in_sig" + str(idx), "in", arg)
                           for idx, arg in enumerate(in_args)]

            comp_generics = None
            comp_oport = None
            comp_outtype = ""

            if node.func in BASIC_COMPONENTS:
                pass
            else:
                comp_name = "comp_dummy"
                comp_outtype = in_args[0].vhdl_type

        ret_comp = Component(name=comp_name,
                             generics=comp_generics,
                             in_ports=comp_iports,
                             out_port=comp_oport,
                             out_type=comp_outtype)
        self.arch_components.append(ret_comp)
        return ret_comp

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self.PY_OP_TO_VHDL_OP[type(node.op)]()
        right = self.visit(node.right)
        #
        if isinstance(left, Expression):
            #  Create additional connection signal
            con_signal = Signal(name=left.instance_name + "_return",
                                vhdl_type=left.out_type())
            left.out_port = Port("return", "out", con_signal)
            #
            self.architecture_body_additions.append(left)
            #
            self.architecture_int_signals[con_signal.name] = con_signal
            left = con_signal

        if isinstance(right, Expression):
            # Create additional connection signal
            con_signal = Signal(name=right.instance_name + "_return",
                                vhdl_type=right.out_type())
            right.out_port = Port("return", "out", con_signal)
            #
            self.architecture_body_additions.append(right)
            #
            self.architecture_int_signals[con_signal.name] = con_signal
            right = con_signal
        #
        ret_comp = BinaryOp(left_port=Port("left", "in", left),
                            op=Generic("op", "", op),
                            right_port=Port("right", "in", right))
        self.arch_components.append(ret_comp)
        return ret_comp

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = self.PY_OP_TO_VHDL_OP[type(node.op)]
        #
        if isinstance(operand, Expression):
            # Create additional connection signal
            con_signal = Signal(name=operand.instance_name + "_return",
                                vhdl_type=operand.out_type())
            operand.out_port = Port("return", "out", con_signal)
            self.architecture_body_additions.append(operand)
            #
            self.architecture_int_signals[con_signal.name] = con_signal
            operand = con_signal
        #
        ret_comp = UnaryOp(in_port=Port("operand", "in", operand),
                           op=Generic("op", "", op))
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
        if isinstance(value, Expression):
            if isinstance(target, ast.Name):
                out_sig = Signal(name=target.id, vhdl_type=value.out_type())
                #
                self.architecture_int_signals[target.id] = out_sig
                #
                value.out_port = Port("return_sig", "out", out_sig)
                return value
            else:
                error_msg = "Undefined assignment to %s" % type(target)
                raise TransformationError(error_msg)
        elif isinstance(value, Constant):
                value.name = target.id
                self.architecture_int_signals[target.id] = value
        else:
            error_msg = "Undefined assignment to %s" % type(target)
            raise TransformationError(error_msg)

    def visit_AugAssign(self, node):
        """
        Visit AugAssign node, resolve to Assign node.

        Attributes:
            node: ast.AugAssign node
        """
        left = node.target
        op = node.op
        right = node.value
        #
        value = ast.BinOp(left=left, op=op, right=right)
        #
        return self.visit(ast.Assign(targets=[node.target], value=value))

    def visit_Return(self, node):
        """ Visit Return node and add Vhdl Return. """
        value = self.visit(node.value)
        #
        if isinstance(value, Signal):
            out_sig = Signal("return_sig", value.vhdl_type)
            #
            self.architecture_io_signals["return_sig"] = out_sig
            #
            in_arg = Port("in_sig", "in", value)
            out_arg = Port("return_sig", "out", out_sig)
            #
            ret_comp = VhdlReturn(in_port=in_arg, out_port=out_arg)
            self.arch_components.append(ret_comp)
            return ret_comp
        elif isinstance(value, Expression):
            pass
        else:
            raise Exception

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
            return None

    def visit_UserCodeTemplate(self, node):
        pass

    def visit_UserFileTemplate(self, node):
        pass
# =========================================================================== #
# USER TRANSFORMERS
# =========================================================================== #


class UserTransformers(object):
    transformers = USERTRANSFORMERS

    def visit(self, tree):
        for transformer in self.transformers:
            transformer().visit(tree)
        return tree