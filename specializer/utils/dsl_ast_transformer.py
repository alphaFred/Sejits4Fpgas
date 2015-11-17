__author__ = 'philipp ebensberger'

import ast
import types
import PIL

from asp import tree_grammar
from collections import namedtuple
from specializer.dsl.dsl_specification import dsl


DslAstData = namedtuple("DslAstData",['ast','args'])


class DslAstTransformer(ast.NodeTransformer):
    def __init__(self, ast_data=DslAstData):
        # parse dsl specification
        # initialize super classes
        tree_grammar.parse(dsl, globals(), checker=None)
        super(DslAstTransformer, self).__init__()
        #
        self.ast = ast_data.ast
        self.argVars = self.check_args(ast_data.args)
        self.localVars = {}

    # ======================================================================= #
    #   HELPER METHODS                                                        #
    # ======================================================================= #
    def check_args(self, args):
        arg_dict = dict()
        for arg_name, arg_value in args:
            try:
                trans_arg_value = []
                for index, sub_arg_value in enumerate(arg_value):
                    # check arg type and add to arg_dict
                    if isinstance(sub_arg_value, PIL.Image.Image):
                        trans_arg_value.append(InImageObj(id=arg_name,mode=sub_arg_value.mode,size=sub_arg_value.size,args=Index(n=index)))
                    else:
                        if type(sub_arg_value) is int:
                            trans_arg_value.append(Constant(id=arg_name, value=sub_arg_value,args=Index(n=index)))
                        else:
                            raise Exception, "Illegal argument type in iterable"
                arg_dict[arg_name] = trans_arg_value
            except TypeError:
                if isinstance(arg_value, PIL.Image.Image):
                    arg_dict[arg_name] = InImageObj(id=arg_name,mode=arg_value.mode,size=arg_value.size,args=None)
                else:
                    if type(arg_value) is int:
                        arg_dict[arg_name] = Constant(id=arg_name, value=arg_value,args=None)
                    else:
                        raise Exception, "Illegal argument type {0}".format(arg_name)
        return arg_dict

    def run(self):
        return self.visit(self.ast)

    # ======================================================================= #
    #   VISITOR METHODS                                                       #
    # ======================================================================= #
    def visit_Module(self, node):
        assert len(node.body) == 1, "Too many items in body module"
        return self.visit(node.body[0])

    def visit_FunctionDef(self, node):
        kernel_return = self.visit(node.body[-1])
        assert type(kernel_return) is ReturnAssign,\
            "Kernel Function has no return statement; line{0}".format(node.lineno)
        # visit kernel body
        kernel_body = map(self.visit, node.body[:-1])
        #
        kernel_name = node.name
        return KernelModule(id=kernel_name,
                            body=kernel_body)

    def visit_Return(self, node):
        try:
            assert type(self.argVars[node.value.id]) is InImageObj,\
                "Illegal return object of type '{0}'; line {1}".format(type(self.argVars[node.value.id]), node.lineno)
        except KeyError, exp_arg:
            print "exp_arg", exp_arg
            raise Exception
        else:
            temp_imageObj = self.argVars[node.value.id]
            self.argVars[node.value.id] = OutImageObj(id=temp_imageObj.id,
                                                      mode=temp_imageObj.mode,
                                                      size=temp_imageObj.size)
            return ReturnAssign(value=self.argVars[node.value.id])

    def visit_Subscript(self, node):
        try:
            ret = self.argVars[node.value.id][self.visit(node.slice)]
        except TypeError:
            raise Exception, "{0} is not iterable!".format(node.value.id)
        else:
            return ret

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Assign(self, node):
        node_targets = map(self.visit, node.targets)
        node_value = self.visit(node.value)
        #
        assert len(node_targets) == 1, "Illegal number of targets for assignment; line {0}".format(node.lineno)
        node_target = node_targets[0]
        #
        if type(node_target) is Identifier:
            if node_target.name in self.localVars:
                assert False, "Illegal multiple assignment to identifier {0}; line {1}".format(node_value.name, node.lineno)
            else:
                self.localVars[node_target.name] = node_target
            return TempAssign(var=node_target, value=node_value)
        elif type(node_target) is OutImageObj:
            return OutAssign(var=node_target, value=node_value)
        else:
            assert False, "Illegal assignment to identifier of type {0}; line {1}".format(type(node_target).__name__, node.lineno)

    def visit_Name(self, node):
        if node.id in self.argVars:
            return self.argVars[node.id]
        if node.id in self.localVars:
            return self.localVars[node.id]
        else:
            return Identifier(name=node.id)
            # assert False, "NAME ERROR {0}; line {1}".format(node.id,node.lineno)

    def visit_Call(self, node):
        # dispatch call
        call_method = "visit_call_" + node.func.attr
        call_visitor = getattr(self, call_method, self.generic_visit)
        return call_visitor(node.args, node.func.value)

    def visit_call_filter(self, args, value):
        assert len(args) == 1, "Filter takes at least 1 argument ({0} given)".format(len(args))
        # dynamically create filter object
        try:
            # get filter name and arguments
            filter_name = args[0].func.id
            filter_args = [self.visit(arg) for arg in args[0].args]
            filter_kwargs = dict([(kwarg.arg, self.visit(kwarg.value)) for kwarg in args[0].keywords])
            # TODO: check with mixed args/kwargs
            # TODO: check without args
            filter_func = globals()[filter_name](*tuple(filter_args), **filter_kwargs)
        except KeyError:
            assert False, "Unknown Filter {0}".format(filter_name)
            raise Exception
        else:
            return ImageFilter(target=self.visit(value), filter=filter_func)

    def visit_call_point(self, args, value):
        assert len(args) == 1, "PointOperator takes at least 1 argument ({0} given)".format(len(args))
        # TODO: implement BinOp in DSL
        return ImagePointOp(target=self.visit(value), op=self.visit(args[0]))

    def visit_Lambda(self, node):
        assert len(node.args.args)==1, "Lambda Expression takes at leas 1 argument ({0} given);".format(len(node.args.args))
        arg = self.visit(node.args.args[0])
        body = self.visit(node.body)
        return body

    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        return BinOp(left=self.visit(node.left),
                     op=node.op,
                     right=self.visit(node.right))

"""
LEGACY CALL:

        #
        if type(node_func) is ImageFilter:
            assert len(node_args) == 1, "Filter accepts 1 argument, {0} given; line {1}".format(len(node_args, node.lineno))
            assert type(node_args[0]) is Filter, "Illegal argument of type {0} for filter; line {1}".format(type(node_args[0]), node.lineno)
            # add filter to ImageFilter
            node_func.filter = node_args[0]
            # return complete ImageFilter object
            return node_func
        elif type(node_func) is Filter:
            # check if number of keyword arguments is identical
            assert len(node_keywords) > 0, "No keyword arguments given to Filter; line {0}".format(node.lineno)
            assert len(node_func.args) == len(node_keywords), "{0} accepts {1} arguments, {2} given; line {3}".format(node_func.name, len(node_func.args), len(node_keywords), node.lineno)
            # check if keywords match template
            try:
                for key in node_func.args.keys():
                    assert type(node_keywords[key]) == type(node_func.args[key]), "Illegal type for argument {0}; line {1}".format(key, node.lineno)
                    # copy keyword value to Filter object
                    node_func.args[key] = node_keywords[key]
            except KeyError:
                assert False, "Illegal keyword argument {0}; line {1}".format(key, node.lineno)
            # return complete Filter object
            return node_func
        elif type(node_func) is ImagePointOp:
            if type(node_args[0]) is ast.BinOp:
                node_func.op = node_args[0]
                return node_func
            else:
                assert False, "Illegal operation used in ImagePointOp; line {0}".format(node.lineno)
        else:
            return node






    def visit_Subscript(self, node):
        if self.sub_imgs_len > 0:
            # in_images consists of nested loops
            node_value = self.visit(node.value)
            node_slice = self.visit(node.slice)
            #
            if type(node_value) is InImageObj:
                assert node_slice < self.sub_imgs_len, "Index out of bound; line{0}".format(node.lineno)
                return InImageObjIdx(index=node_slice, width=512, height=512)
            else:
                assert False, "Illegal indexation; line {0}".format(node.lineno)
        else:
            # no nested loops => indexation illegal
            assert False, "Illegal indexation; line {0}".format(node.lineno)

    def visit_Index(self, node):
        if type(node.value) is ast.Num:
            return node.value.n
        else:
            assert False, "Illegal indexation; line {0}".format(node.lineno)

    def visit_Call(self, node):
        node_func = self.visit(node.func)
        node_args = [self.visit(arg) for arg in node.args]
        node_keywords = dict((keyword.arg, self.visit(keyword.value)) for keyword in node.keywords)
        #
        if type(node_func) is ImageFilter:
            assert len(node_args) == 1, "Filter accepts 1 argument, {0} given; line {1}".format(len(node_args, node.lineno))
            assert type(node_args[0]) is Filter, "Illegal argument of type {0} for filter; line {1}".format(type(node_args[0]), node.lineno)
            # add filter to ImageFilter
            node_func.filter = node_args[0]
            # return complete ImageFilter object
            return node_func
        elif type(node_func) is Filter:
            # check if number of keyword arguments is identical
            assert len(node_keywords) > 0, "No keyword arguments given to Filter; line {0}".format(node.lineno)
            assert len(node_func.args) == len(node_keywords), "{0} accepts {1} arguments, {2} given; line {3}".format(node_func.name, len(node_func.args), len(node_keywords), node.lineno)
            # check if keywords match template
            try:
                for key in node_func.args.keys():
                    assert type(node_keywords[key]) == type(node_func.args[key]), "Illegal type for argument {0}; line {1}".format(key, node.lineno)
                    # copy keyword value to Filter object
                    node_func.args[key] = node_keywords[key]
            except KeyError:
                assert False, "Illegal keyword argument {0}; line {1}".format(key, node.lineno)
            # return complete Filter object
            return node_func
        elif type(node_func) is ImagePointOp:
            if type(node_args[0]) is ast.BinOp:
                node_func.op = node_args[0]
                return node_func
            else:
                assert False, "Illegal operation used in ImagePointOp; line {0}".format(node.lineno)
        else:
            return node

    def visit_Num(self, node):
        return node.n

    def visit_Lambda(self, node):
        assert len(node.args.args)==1, "Too many arguments in Lambda expression; line {0}".format(node.lineno)
        arg = self.visit(node.args.args[0])
        assert type(arg) is Identifier, "Illegal argument type; line{0}".format(node.lineno)
        body = self.visit(node.body)
        return body

    def visit_Attribute(self, node):
        node_attr = node.attr
        node_value = self.visit(node.value)
        #
        if node_attr == "filter":
            # check if filter is applied to Image object
            if type(node_value) is InImageObj or type(node_value) is InImageObjIdx or type(node_value) is Identifier:
                return ImageFilter(target=node_value,
                                   filter=None)
            else:
                assert False, "Illegal application of filter to object of type {0}; line {1}".format(type(node_value), node.lineno)
        elif node_attr == "point":
            if type(node_value) is InImageObj or type(node_value) is InImageObjIdx or type(node_value) is Identifier:
                return ImagePointOp(target=node_value,op=None)
            else:
                assert False, "Illegal application of point to object of type {0}; line {1}".format(type(node_value), node.lineno)
        else:
            return node
"""