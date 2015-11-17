"""
    sejits_fia Module provides the specialize decorator
"""
import sys
import traceback

from specializer.fpga_specializer import Zynq_Specializer
from specializer.cpu_specializer import X86_Specializer, ARM_Specializer
from specializer.gpu_specializer import CUDA_Specializer


# TODO: add auto initialize
core_dispatch = {"fpga" :Zynq_Specializer,
                 "x86"  :X86_Specializer,
                 "arm"  :ARM_Specializer,
                 "cuda" :CUDA_Specializer}


class Specialize(object):
    """docstring for Specialize"""
    def __init__(self, target="python"):
        super(Specialize, self).__init__()
        self.sejits_active = False
        if target in core_dispatch:
            self.target_core = core_dispatch[target]
            self.sejits_active = True
        else:
            self.sejits_active = False

    def __call__(self, wrapped_func):
        """ docstring for __call__ """
        ret_func = None
        if self.sejits_active == False:
            ret_func = wrapped_func
        else:
            try:
                assert wrapped_func.func_defaults is not None, "ERROR NO FUNC_DEFAULTS!"
                func_args = tuple(zip(wrapped_func.func_code.co_varnames,
                                      wrapped_func.func_defaults))
                # TODO: copy target execution here
                self.kernel_core = self.target_core(func_args, wrapped_func)
                self.kernel_core.run()
            except Exception, e:
                print traceback.print_exc()
                print "return wrapped func\n"
                ret_func = wrapped_func
            else:
                print "return fpga dummy"
                ret_func = fpga_dummy
        #
        def wrappee(*args,**kwargs):
            ret_func(*args,**kwargs)
        return wrappee


def specialize(target="fpga"):
    assert target in avail_targets, "Undefined specialization target '{0}'".format(target)
    #
    def decorate(func):
        print "running syntax check"
        #
        sejits_active = False
        #
        if func.func_defaults is None:
            print "ERROR NO FUNC_DEFAULTS!"
            sejits_active = False
        else:
            args = tuple(zip(func.func_code.co_varnames,func.func_defaults))
            sejits_active = True
            fia_kernel_core = FIA_Kernel_Core(args, func)
            fia_kernel_core.run(target="fpga")
        # return final function
        if sejits_active:
            ret = fpga_dummy
        else:
            ret = func
        return ret
    return decorate

def fpga_dummy(*args, **kwargs):
    print "--> FPGA DUMMY"
"""
def specialize(func):
    print "running spec"
    if func.func_defaults is None:
        print "ERROR NO FUNC_DEFAULTS!"
    func_src = inspect.getsource(func)
    func_ast = ast.parse(func_src.lstrip())
    print "#"*80
    print func_src
    print "#"*80
    print pformat_ast(func_ast)
    print "finished spec"
    @functools.wraps(func)
    def specialized(*args, **kwargs):
        kernel_src = inspect.getsource(func)
        kernel_ast = ast.parse(kernel_src.lstrip())
        print "#"*80
        for arg in args:
            print arg.__class__.__name__
    return specialized
"""