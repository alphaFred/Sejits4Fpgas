""" Transformations for scikit-image filter functions. """
__author__ = 'philipp ebensberger'

import ast
import numpy as np
import skimage.filters
import logging
import sejits_ctree
from sejits_ctree.visitors import NodeTransformer

from sejits_ctree.vhdl.nodes import VhdlFile, EntityDecl, ComponentCall
from sejits_ctree.vhdl.nodes import Op, SymbolRef
from sejits_ctree.vhdl.nodes import Architecture, BinaryOp, Return, Constant

logger = logging.getLogger('test_transformer')


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
        """ Return function node. """
        node_hash = hash(node)
        if self.enable_caching and node_hash in self.visited_nodes:
            return self.visited_nodes[node_hash]
        else:
            # save previously active architecture
            prev_arch = self.active_architecture
            name = node.name
            params = [self.visit(p) for p in node.args.args]
            #
            self.active_architecture = Architecture()
            # filter out None bodies caused by linearization
            body = filter(None, [self.visit(body) for body in node.body])
            # TODO: implement full linearization
            # assert len(body) == 1, "Function %s is not linearized!" % name
            assert type(body[-1]) is Return, "Function %s must contain return statement!" % name
            # TODO: handle decorators
            # TODO: implement architecture/entity
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
