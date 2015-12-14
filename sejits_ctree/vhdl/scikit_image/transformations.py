""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import logging
import sejits_ctree

from skimage.filters import scharr, prewitt, sobel

from sejits_ctree.vhdl.scikit_image.func_resolutions import sobel_Resolver
from sejits_ctree.vhdl.scikit_image.func_substitutes import assert_nD_Substituter

from sejits_ctree.vhdl.nodes import VhdlFile, VhdlProject, Entity, Return
from sejits_ctree.vhdl.nodes import Op, SymbolRef, Constant, ComponentCall
from sejits_ctree.vhdl.nodes import Architecture, Block

logger = logging.getLogger('test_transformer')


class FuncResolver(object):

    """
    Resolve function calls using given resolvers.

    If matching resolver is provided, the source code of the function is
    retrieved from the library and inserted into the given tree using an
    VhdlFile node.
    """

    resolvers = [sobel_Resolver]

    def __init__(self):
        """ Initialize FunctionalResolver. """
        pass

    def visit(self, tree):
        """ Visit tree with all resolvers """
        for resolver in self. resolvers:
            resolver().visit(tree)
        return tree


class FuncSubstituter(object):

    """ Substitutes function calls using given substituters. """

    substituters = [assert_nD_Substituter]

    def __init__(self):
        """ Initialize FunctionalTransformer. """
        pass

    def visit(self, tree):
        """ Visit tree with all substituters. """
        for substiturer in self.substituters:
            substiturer().visit(tree)
        return tree


class VhdlKeywordTransformer(ast.NodeTransformer):

    """ Transforms Name nodes with VHDL keywords. """

    VHDL_Keywords = {"abs", "access", "after", "alias", "all", "and",
                     "architecture", "array", "assert", "attribute", "begin",
                     "block", "body", "buffer", "bus", "case", "component",
                     "configuration", "constant", "disconnect", "downto",
                     "else", "elsif", "end", "entity", "exit", "file",
                     "for", "function", "generate", "generic", "group",
                     "guarded", "if", "impure", "in", "inertial", "inout",
                     "is", "label", "library", "linkage", "literal", "loop",
                     "map", "mod", "nand", "new", "next", "nor", "not",
                     "null", "of", "on", "open", "or", "others", "out",
                     "package", "port", "postponed", "procedure", "process",
                     "pure", "range", "record", "register", "reject", "rem",
                     "report", "return", "rol", "ror", "select", "severity",
                     "signal", "shared", "sla", "sll", "sra", "srl",
                     "subtype", "then", "to", "transport", "type",
                     "unaffected", "units", "until", "use", "variable",
                     "wait", "when", "while", "with", "xnor", "xor"}

    def visit_Name(self, node):
        """ Change id of Name node if it is a VHDL keyword. """
        if node.id in self.VHDL_Keywords:
            node.id = "sig_" + node.id
        return node


class VhdlBasicTransformer(ast.NodeTransformer):

    """ Transform ast to basic Vhdl nodes. """

    changed_ref = dict()
    vhdl_files = []

    PY_OP_TO_VHDLTREE_OP = {ast.Add: Op.Add,
                            ast.Mult: Op.Mul,
                            ast.Sub: Op.Sub,
                            ast.Div: Op.Div,
                            ast.Pow: Op.Pow}
    """
    COMP_TO_RESOLVE = {}
    """
    COMP_TO_RESOLVE = {"scharr": scharr,
                       "prewitt": prewitt,
                       "sobel": sobel}

    def __init__(self):
        """ initialize base class. """
        super(VhdlBasicTransformer, self).__init__()

    def run(self, tree):
        main_vhdl_file = self.visit(tree)
        main_vhdl_file = [main_vhdl_file] + self.vhdl_files
        return VhdlProject(main_vhdl_file)

    def visit_Name(self, node):
        """ Visit Name, return SigRef. """
        if node.id in self.changed_ref:
            return self.changed_ref[node.id]
        else:
            return SymbolRef(name=node.id, sym_type=None)

    def visit_Num(self, node):
        """ Visit Num, return Constant. """
        return Constant(value=node.n, sym_type=None)

    def visit_Module(self, node):
        """ Visit Module, return VhdlFile. """
        assert len(node.body) == 1
        entity, arch = self.visit(node.body[0])
        return VhdlFile(name=entity.name,
                        body=[entity, arch])

    def visit_FunctionDef(self, node):
        """ Visit FunctionDef, return Entity and Architecture. """
        # visit all body nodes, remove None nodes and flatten node.body
        body = filter(None, [self.visit(body) for body in node.body])
        assert type(body[-1]) is Return,\
            "Function %s must contain return statement!" % node.name
        # resolve FunctionDef into Entity and Architecture
        entity, io_signals = self.build_Entity(node, body)
        architecture = self.build_Architecture(node, body, io_signals)
        return (entity, architecture)

    def build_Entity(self, node, node_body):
        """
        Create and return Entity node.

        Args:
            node: FunctionDef node
            node_body: visited and filtered FunctionDef node body
        Return:
            Entity node
        """
        # visit FunctionDef node arguments and use them as input arguments
        in_args = self.visit(node.args)  # in_args is list of SymbolRef
        # get symbol reference of Return node in node body
        out_arg = node_body[-1].sig_ref()  # out_arg is SymbolRef
        #
        io_signals = {key for key in in_args + [out_arg]}
        # return Entity node
        entity = Entity(name=node.name,
                        in_args=in_args,
                        out_arg=out_arg)
        return entity, io_signals

    def visit_arguments(self, node):
        """ Visit arguments. """
        return [self.visit(arg) for arg in node.args]

    def build_Architecture(self, node, node_body, io_signals):
        """
        Create and return Architecture node.

        Args:
            node: FunctionDef node
            node_body: visited and filtered FunctionDef node body
            io_signals: set of entitie's input and output signals
        Return:
            Architecture node
        """
        # detach Return node of node_body
        node_body, ret_node = node_body[:-1], node_body[-1]
        if isinstance(ret_node.value, ComponentCall):
            # add returned ComponentCall node to node_body
            node_body.append(ret_node.value)
        elif isinstance(ret_node.value, SymbolRef):
            pass  # returned SymbolRef already attached to out_args of entity
        else:
            assert False, "Undefined Return value type"
        # flatten Block in node_body
        arch_body = []
        for elem in node_body:
            if type(elem) is Block:
                arch_body = arch_body + list(self.flatten_Block(elem))
            else:
                arch_body.append(elem)
        """
        # get all architecture signals
        for elem in arch_body:
        #
        """
        return Architecture(body=arch_body)

    def visit_Return(self, node):
        """ Visit Return node, return Vhdl-Return node. """
        if hasattr(node, 'value'):
            value = self.visit(node.value)
            assert type(value) is not list
            if isinstance(value, ComponentCall):
                value.out_args = SymbolRef(name="out_sig", sym_type=None)
            return Return(value=value)
        else:
            assert False, "Empty return statement not allowed!"

    def visit_Expr(self, node):
        """ Visit Expr node, return None if string else return node value. """
        if hasattr(node, "value"):
            if type(node.value) is ast.Str:
                return None
            else:
                return self.visit(node.value)
        else:
            return None

    def visit_Assign(self, node):
        """ Visit Assign, return or update CompCall. """
        value = self.visit(node.value)
        targets = [self.visit(target) for target in node.targets]
        # Only one output is supported
        assert len(targets) == 1
        # check of all targets is implemented for future use
        if type(value) is ComponentCall and\
                all(isinstance(t, SymbolRef) for t in targets):
            value.out_args = targets
            return value
        elif type(value) is Block and\
                all(isinstance(t, SymbolRef) for t in targets):
            value.out_args = targets
            return value
        elif type(value) is SymbolRef and\
                all(isinstance(t, SymbolRef) for t in targets):
            """
            Add new SymbolRef to change dict

            Example:
                1. a = bla()
                2. b = a
                3. c = foo(b)
            b is equal to a in (3.) therefore we can change the subsequent
            calls to b with a in the ast:
                3. c = foo(a)
            """
            targets = targets[0]
            self.changed_ref[targets.name] = value
            return None
        elif type(value) is VhdlFile and\
                all(isinstance(t, SymbolRef) for t in targets):
            self.vhdl_files.append(value)
            value = ComponentCall(comp=value.body[0].name,
                                  in_args=value.body[0].in_args,
                                  out_args=targets)
            return value
        else:
            assert False

    def visit_AugAssign(self, node):
        """ Visit AugAssign, resolve to Assign. """
        left = self.visit(node.target)
        op = self.visit(node.op)
        right = self.visit(node.value)
        '''
        resolution into ast.Assign neccessary to trigger visit of visit_Assign
        and check for temporary variable resolution!
        '''
        return self.visit(ast.Assign(targets=[node.target],
                                     value=ast.BinOp(left=left,
                                                     op=op,
                                                     right=right)))

    def visit_BinOp(self, node):
        """ Visit BinOp node and return Block. """
        left = self.visit(node.left)
        op = self.PY_OP_TO_VHDLTREE_OP[type(node.op)]()
        right = self.visit(node.right)
        ret = [ComponentCall(comp="BinOp",
                             in_args=[left.sig_ref(),
                                      op.sig_ref(),
                                      right.sig_ref()],
                             out_args=None)]
        ret = ret + filter(lambda i: not isinstance(i, SymbolRef)
                           and not isinstance(i, Constant), [left, right])
        return Block(body=ret)

    def visit_Attribute(self, node):
        """ Visit Attribute node and return SymbolRef. """
        return SymbolRef(name=node.attr)

    def visit_Call(self, node):
        """ Visit Call node and return ComponentCall or Block. """
        func = self.visit(node.func)
        if func.name in self.COMP_TO_RESOLVE:
            vhdl_file = VhdlBasicTransformer().\
                visit(sejits_ctree.get_ast(self.COMP_TO_RESOLVE[func.name]))
            self.vhdl_files.append(vhdl_file)
        # check arguments
        _args = [self.visit(arg) for arg in node.args]
        blocks = [arg for arg in _args if isinstance(arg, Block)]
        args = [arg for arg in _args if not isinstance(arg, Block)]
        if len(blocks) >= 1:
            args = args + [dc.sig_ref() for dc in blocks]
            ret = ComponentCall(comp=func.name,
                                in_args=args,
                                out_args=None)
            ret = [ret] + blocks
            return Block(body=ret)
        else:
            return ComponentCall(comp=func.name,
                                 in_args=args,
                                 out_args=None)

    def flatten_Block(self, block):
        """ Flatten Block nodes recursively. """
        for elem in block.body:
            if type(elem) is Block:
                for ielem in self.flatten_Block(elem):
                    yield ielem
            else:
                yield elem
