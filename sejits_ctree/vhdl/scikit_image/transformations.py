""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import numpy as np
import skimage.filters
import logging
import sejits_ctree

from skimage.filters import scharr, prewitt, sobel
from sejits_ctree.visitors import NodeTransformer

from sejits_ctree.vhdl.nodes import VhdlFile, VhdlProject, EntityDecl, Return
from sejits_ctree.vhdl.nodes import Op, SymbolRef, Constant, ComponentCall
from sejits_ctree.vhdl.nodes import Architecture, BinaryOp, DummyContainer

logger = logging.getLogger('test_transformer')


class VhdlBasicTransformer(ast.NodeTransformer):

    """ Transform ast to basic Vhdl nodes. """

    change_ref = dict()
    vhdl_files = []

    PY_OP_TO_VHDLTREE_OP = {ast.Add: Op.Add,
                            ast.Mult: Op.Mul,
                            ast.Sub: Op.Sub,
                            ast.Div: Op.Div,
                            ast.Pow: Op.Pow}

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
        if node.id in self.change_ref:
            return self.change_ref[node.id]
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
        body = filter(None, [self.visit(body) for body in node.body])
        assert type(body[-1]) is Return,\
            "Function %s must contain return statement!" % node.name
        in_args = [self.visit(p) for p in node.args.args]
        out_arg = body[-1].sig_ref()
        # resolve FunctionDef into Entity and Architecture
        entity = EntityDecl(name=node.name,
                            in_args=in_args,
                            out_arg=out_arg)
        # TODO: check for Dummy Container as Return value
        if isinstance(body[-1].value, ComponentCall):
            body = body[:-1] + [body[-1].value]
        elif isinstance(body[-1].value, SymbolRef):
            body = body[:-1]
        else:
            assert False
        #
        arch_body = []
        for elem in body:
            if type(elem) is DummyContainer:
                arch_body = arch_body + list(self.flatten_DummyContainer(elem))
            else:
                arch_body.append(elem)
        #
        arch = Architecture(body=arch_body)
        return (entity, arch)

    def visit_Return(self, node):
        """ Visit Return, return Return(Vhdl). """
        if hasattr(node, 'value'):
            value = self.visit(node.value)
            assert type(value) is not list
            if isinstance(value, ComponentCall):
                value.out_args = SymbolRef(name="out_sig", sym_type=None)
            return Return(value=value)
        else:
            assert False, "Empty return statement not allowed!"

    def visit_Expr(self, node):
        """ Visit Expr, remove comments or return value. """
        if type(node.value) is ast.Str:
            return None
        else:
            return self.visit(node.value)

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
        elif type(value) is DummyContainer and\
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
            calls to b with a in the ast
            """
            return None
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
        return DummyContainer(body=ret)

    def visit_Attribute(self, node):
        return SymbolRef(name=node.attr)

    def visit_Call(self, node):
        func = self.visit(node.func)
        if func.name in self.COMP_TO_RESOLVE:
            vhdl_file = VhdlBasicTransformer().\
                visit(sejits_ctree.get_ast(self.COMP_TO_RESOLVE[func.name]))
            self.vhdl_files.append(vhdl_file)
        # check arguments
        _args = [self.visit(arg) for arg in node.args]
        dummy_cont = [arg for arg in _args if isinstance(arg, DummyContainer)]
        args = [arg for arg in _args if not isinstance(arg, DummyContainer)]
        if len(dummy_cont) >= 1:
            args = args + [dc.sig_ref() for dc in dummy_cont]
            ret = ComponentCall(comp=func.name,
                                in_args=args,
                                out_args=None)
            ret = [ret] + dummy_cont
            return DummyContainer(body=ret)
        else:
            return ComponentCall(comp=func.name,
                                 in_args=args,
                                 out_args=None)

    def flatten(self, lst):
        for elem in lst:
            if type(elem) in (tuple, list):
                for i in self.flatten(elem):
                    yield i
            else:
                yield elem

    def flatten_DummyContainer(self, dummy_cont):
        for elem in dummy_cont.body:
            if type(elem) is DummyContainer:
                for ielem in self.flatten_DummyContainer(elem):
                    yield ielem
            else:
                yield elem













# ============================================================================ #
# ============================================================================ #
# ============================================================================ #
# ============================================================================ #
# ============================================================================ #
class VhdlTransformer(ast.NodeTransformer):

    """ Transforms kernel ast to vhdl ast. """

    visited_nodes = dict()
    enable_caching = True

    def __init__(self):
        """ docstring dummy. """
        self.temp_dict = {}
        #
        self.names_dict = {"HSOBEL_WEIGHTS": 'HSOBEL_WEIGHTS',
                           "VSOBEL_WEIGHTS": 'VSOBEL_WEIGHTS'}
        #
        self.active_architecture = None
        #
        super(VhdlTransformer, self).__init__()

    PY_OP_TO_VHDLTREE_OP = {ast.Add: Op.Add,
                            ast.Mult: Op.Mul,
                            ast.Sub: Op.Sub,
                            ast.Div: Op.Div,
                            ast.Pow: Op.Pow}

    def visit_Name(self, node):
        """ Remove ctx node and linearize local variable calls. """
        node.ctx = None
        # if local variable exists return cached data, else return node
        if node.id in self.temp_dict:
            return self.temp_dict[node.id]
        else:
            return SymbolRef(node.id,
                             _global=node.id in self.names_dict,
                             _local=node.id not in self.names_dict)

    def visit_Num(self, node):
        """ Transform ast.Num into Constant node. """
        node_hash = hash(node)
        if self.enable_caching and node_hash in self.visited_nodes:
            return self.visited_nodes[node_hash]
        else:
            ret = Constant(value=node.n)
            self.visited_nodes[node_hash] = ret
            return ret

    def visit_Module(self, node):
        """ Return .vhdl-file node. """
        node_hash = hash(node)
        if self.enable_caching and node_hash in self.visited_nodes:
            print "visit cache"
            return self.visited_nodes[node_hash]
        else:
            body = [self.visit(body) for body in node.body]
            assert len(body) == 1
            body = body[0]  # body is now [EntityDecl, Architecture]
            # body = (entity, arch)
            ret = VhdlFile(name=body[0].name,
                           body=body)
            # update next in child nodes
            [item.next.append(ret) for item in body]
            # cache node
            self.visited_nodes[body[0].name] = ret
            print "visit new"
            return ret

    def visit_FunctionDef(self, node):
        """
        Return function node.

        # TODO: implement full linearization
        # TODO: handle decorators
        # TODO: implement architecture/entity
        """
        node_hash = hash(node)
        if self.enable_caching and node_hash in self.visited_nodes:
            return self.visited_nodes[node_hash]
        else:
            # save previously active architecture
            prev_arch = self.active_architecture
            name = node.name
            params = [self.visit(p) for p in node.args.args]
            # add new active architecture
            self.active_architecture = Architecture()
            # filter out None bodies caused by linearization
            body = filter(None, [self.visit(body) for body in node.body])
            assert type(body[-1]) is Return, "Function %s must contain return statement!" % name
            self.active_architecture.body = body
            # update next in child nodes
            [item.next.append(self.active_architecture) for item in body]
            ret = EntityDecl(return_type=None,
                             name=name,
                             params=params)
            ret = [ret, self.active_architecture]
            self.active_architecture = prev_arch
            # cache node
            self.visited_nodes[node_hash] = ret
            return ret

    # TODO: check necessity of visit_arg
    def visit_arg(self, node):
        """ docstring dummy. """
        node_hash = hash(node)
        if self.enable_caching and node_hash in self.visited_nodes:
            return self.visited_nodes[node_hash]
        else:
            ret = SymbolRef(node.arg, node.annotation)
            # cache node
            self.visited_nodes[node_hash] = ret
            return ret

    def visit_Return(self, node):
        """ docstring dummy. """
        if hasattr(node, 'value'):
            value = self.visit(node.value)
            ret = Return(value)
            # update next in child node
            value.next.append(ret)
            return ret
        else:
            assert False, "Empty return statement not allowed!"

    def visit_Expr(self, node):
        """ Remove comments. """
        if type(node.value) is ast.Str:
            return None
        else:
            return self.visit(node.value)

    def visit_Assign(self, node):
        """ docstring dummy. """
        assert len(node.targets) == 1, "Multiple assignments are currently not \
            supported!"
        # cache assignment to ast.Name node
        if type(node.targets[0]) is ast.Name:
            self.temp_dict[node.targets[0].id] = self.visit(node.value)
            return None
        else:
            return node

    def visit_AugAssign(self, node):
        """ docstring dummy. """
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

    def visit_Attribute(self, node):
        """ docstring dummy. """
        value = self.visit(node.value)
        if type(value) is SymbolRef:
            _node = SymbolRef(name=value.name + "." + node.attr)
        else:
            # TODO: implement vhdl ast node return &| log entry|exception
            _node = ast.Attribute(value=value, attr=node.attr, ctx=None)
        return ast.copy_location(_node, node)

    def visit_BinOp(self, node):
        """ docstring dummy. """
        return BinaryOp(left=self.visit(node.left),
                        op=self.PY_OP_TO_VHDLTREE_OP[type(node.op)](),
                        right=self.visit(node.right))

    def visit_Call(self, node):
        """ docstring dummy. """
        if hasattr(node.func, 'id') and hasattr(skimage.filters, node.func.id):
            func_obj = getattr(skimage.filters, node.func.id)
            #
            func = VhdlTransformer().visit(sejits_ctree.get_ast(func_obj))
            args = [self.visit(arg) for arg in node.args]
            # keywords = [self.visit(keyword) for keyword in node.keywords]

            # TODO: visit starargs and kwargs
            # starargs = self.visit(node.starargs)
            # kwargs = self.visit(node.kwargs)
        else:
            func = self.visit(node.func)
            args = [self.visit(arg) for arg in node.args]
            # keywords = [self.visit(keyword) for keyword in node.keywords]

            # TODO: visit starargs and kwargs
            '''
            starargs/kwargs probably unsuitable for compilation/synthetisation
            anyway
            '''
            # starargs = self.visit(node.starargs)
            # kwargs = self.visit(node.kwargs)
        # TODO: resolve usage of keyword, starargs and kwargs
        ret = ComponentCall(comp=func,
                            args=args)
        self.active_architecture.add_component(ret)
        return ret


class IfTransformer(NodeTransformer):
    def visit_Expr(self, node):
        """ Remove comments. """
        if type(node.value) is str:
            return None

    def visit_Name(self, node):
        """ Remove ctx node. """
        node.ctx = None
        return node

    def visit_Attribute(self, node):
        """ Remove ctx node. """
        node.ctx = None
        return node
