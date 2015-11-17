__author__ = 'philipp ebensberger'

import inspect
import ast
import types

import asp.tree_grammar as tree_grammar
from specializer.utils.ast_visualizer import pformat_ast
from specializer.dsl.dsl_specification import dsl
from specializer.utils.dsl_ast_transformer import DslAstData
from specializer.utils.dsl_ast_transformer import DslAstTransformer


class Zynq_Specializer(object):
    def __init__(self, args, func):
        # TODO: remove ALL decorators! -> multiple decorators etc.
        func_src = "\n".join(inspect.getsource(func).splitlines()[1:])
        func_ast = ast.parse(func_src.lstrip())
        # pack ast-data
        self.func_ast_data = DslAstData(ast = func_ast,
                                        args = args)

    # ======================================================================= #
    #   HELPER METHODS                                                        #
    # ======================================================================= #
    def run(self):
        ast_transformer = DslAstTransformer(self.func_ast_data)
        ret = ast_transformer.run()
        # DEBUG
        print "\nKERNEL TRANSFORMED\n"
        pformat_ast(ret)
        print "#"*80,"\n\n"
        # !DEBUG
        return ret




        """
        self.global_vars = arg_dict
        self.kernel_transformer = FIA_Kernel_Transformer()
        self.kernel_optimizer = FIA_Kernel_Optimizer()
        self.kernel_codegen = VHDL_CodeGen()
        self.in_images = in_images
        self.out_image = out_image
        # analyze in_images
        self.img_width, self.img_height, self.imgs_len, self.sub_imgs_len = \
            self.check_in_images(self.in_images)
        # create global vars for transformation/optimization
        self.global_vars = \
            {"in_images": InImageObj(width=self.img_width, height=self.img_height),
             "out_image": OutImageObj(width=self.img_width, height=self.img_height),
             "MinFilter": Filter(name="MinFilter", args={"size":int()})}
        # create kernel transformer and optimizer
        self.kernel_transformer = FIA_Kernel_Transformer()
        self.kernel_optimizer = FIA_Kernel_Optimizer()
        self.kernel_codegen = VHDL_CodeGen()
        """

"""
        def run(self, target="python"):
            # transform kernel to ast representation
            kernel_ast = self.func_ast
            #
            ast_data = Ast_Data(ast = kernel_ast,
                                global_vars = self.global_vars,
                                imgs_len = 1,
                                sub_imgs_len = 0)
            #
            if target == "python":
                #
                from Image import merge
                from ImageFilter import MinFilter
                #
                py_kernel_src = "\n".join([line.lstrip() for line in kernel_src.split("\n")[1:-1]])
                out_image = None
                for in_images in self.in_images:
                    exec(py_kernel_src)
                #
                return out_image
            elif target == "fpga":
                kernel_transformed = self.kernel_transformer.run(ast_data)
                # DEBUG
                print "\nKERNEL TRANSFORMED\n"
                pformat_ast(kernel_transformed)
                print "#"*80,"\n\n"
                # !DEBUG
                print "KERNEL OPTIMIZED\n"
                kernel_optimized = self.kernel_optimizer.run(kernel_transformed)
                #
                print "KERNEL OPTIMIZED\n"
                #
                #kernel_code = self.kernel_codegen.run(kernel_optimized)
                return None
            else:
                assert False, "Illegal target >{0}<".format(target)
    """