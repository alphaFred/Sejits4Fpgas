__author__ = 'philipp ebensberger'

import ast
import PIL
import numpy

class DslAstTransformer(ast.NodeTransformer):
    """ docstring for DslAstTransformer """
    def __init__(self, ast, args, dsl_classes):
        """ docstring for __init__"""
        # add dsl classes to global scope
        globals().update(dsl_classes)
        super(DslAstTransformer, self).__init__()
        #
        self.ast = ast
        self.argVars = self.check_args(args)
        self.localVars = {}

    # ======================================================================= #
    #   HELPER METHODS                                                        #
    # ======================================================================= #
    def check_args(self, args):
        """ docstring for check_args """
        arg_dict = dict()

        # ---------------------------------------------------------------------
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
                            #trans_arg_value.append(Constant(id=arg_name, value=sub_arg_value,args=Index(n=index)))
                            trans_arg_value.append(Int(id=arg_name, n=sub_arg_value, args=Index(n=index)))
                        elif type(sub_arg_value) is float:
                            trans_arg_value.append(Float(id=arg_name, n=sub_arg_value, args=Index(n=index)))
                        else:
                            raise Exception, "Illegal argument type in iterable"
                arg_dict[arg_name] = trans_arg_value
            except TypeError:
                if isinstance(arg_value, PIL.Image.Image):
                    arg_dict[arg_name] = InImageObj(id=arg_name,mode=arg_value.mode,size=arg_value.size,args=None)
                else:
                    if type(arg_value) is int:
                        #arg_dict[arg_name] = Constant(id=arg_name, value=arg_value,args=None)
                        arg_dict[arg_name] = Int(id=arg_name, n=arg_value, args=None)
                    elif type(arg_value) is float:
                        arg_dict[arg_name] = Float(id=arg_name, n=arg_value, args=None)
                    else:
                        raise Exception, "Illegal argument type {0}".format(arg_name)
        return arg_dict

    def run(self):
        """ docstring for run """
        return self.visit(self.ast)

    # ======================================================================= #
    #   VISITOR METHODS                                                       #
    # ======================================================================= #
    def visit_Module(self, node):
        """ docstring for visit_Module """
        assert len(node.body) == 1, "Too many items in body module"
        return self.visit(node.body[0])

    def visit_FunctionDef(self, node):
        """ docstring for visit_FunctionDef """
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
        """ docstring for visit_Return """
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
        """ docstring for visit_Subscript """
        try:
            ret = self.argVars[node.value.id][self.visit(node.slice).n]
        except TypeError:
            raise Exception, "{0} is not iterable!".format(node.value.id)
        else:
            return ret

    def visit_Index(self, node):
        """ docstring for visit_Index """
        return self.visit(node.value)

    def visit_Assign(self, node):
        """ docstring for visit_Assign """
        node_targets = map(self.visit, node.targets)
        node_value = self.visit(node.value)
        #
        assert len(node_targets) == 1, "Illegal number of targets for assignment in line {0}".format(node.lineno)
        node_target = node_targets[0]
        #
        if type(node_target) is Identifier:
            if node_target.name in self.localVars:
                assert False, "Multiple assignment to identifier {0} in line {1}".format(node_target.name, node.lineno)
            else:
                self.localVars[node_target.name] = node_target
            return TempAssign(var=node_target, value=node_value)
        elif type(node_target) is OutImageObj:
            return OutAssign(var=node_target, value=node_value)
        else:
            assert False, "Illegal assignment to identifier of type {0} in line {1}".format(type(node_target).__name__, node.lineno)

    def visit_Name(self, node):
        """ docstring for visit_Name """
        if node.id in self.argVars:
            return self.argVars[node.id]
        if node.id in self.localVars:
            return self.localVars[node.id]
        else:
            return Identifier(name=node.id)
            # assert False, "NAME ERROR {0}; line {1}".format(node.id,node.lineno)

    def visit_Call(self, node):
        """ docstring for visit_Call """
        # dispatch call
        call_method = "visit_call_" + node.func.attr
        call_visitor = getattr(self, call_method, self.generic_visit)
        return call_visitor(node.args, node.func.value)

    def visit_call_filter(self, args, value):
        """ docstring for visit_call_filter """
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
        """ docstring for visit_call_point """
        assert len(args) == 1, "PointOperator takes at least 1 argument ({0} given)".format(len(args))
        # TODO: implement BinOp in DSL
        return ImagePointOp(target=self.visit(value), op=self.visit(args[0]))

    def visit_List(self, node):
        list_items = [self.visit(x) for x in node.elts]
        # TODO: change check; only int types is supported by FPGA
        if all(isinstance(x, int) for x in list_items):
            pass
        return np.array(list_items)

    def visit_Lambda(self, node):
        """ docstring for visit_Lambda """
        assert len(node.args.args) == 1,\
            "Lambda Expression takes at least 1 argument ({0} given);".\
            format(len(node.args.args))
        arg = self.visit(node.args.args[0])
        body = self.visit(node.body)
        return body

    def visit_BinOp(self, node):
        """ docstring for visit_BinOp """
        return BinOp(left=self.visit(node.left),
                     op=node.op,
                     right=self.visit(node.right))

    def visit_Num(self, node):
        """ docstring for visit_Num """
        if type(node.n) is int:
            return Int(id=None,n=node.n, args=None)
            # return Int(id=None, n=node.n, args=None)
        elif type(node.n) is float:
            return Float(id=None, n=node.n, args=None)
        else:
            assert False, "Illegal numeric type!"

    def visit_If(self, node):
        assert False,\
            "If statement  in line {0} not supported".format(node.lineno)
