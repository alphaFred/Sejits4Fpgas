""" sejits_fia Module provides the specialize decorator. """
__author__ = 'philipp ebensberger'

import traceback

from specializer.fpga_specializer import ZynqSpecializer
from specializer.cpu_specializer import X86_Specializer, ARM_Specializer
from specializer.gpu_specializer import CUDA_Specializer


# TODO: add auto initialize
core_dispatch = {"fpga": ZynqSpecializer,
                 "x86": X86_Specializer,
                 "arm": ARM_Specializer,
                 "cuda": CUDA_Specializer}


class Specialize(object):

    """ docstring for Specialize. """

    def __init__(self, target="python"):
        """ docstring for __init__. """
        super(Specialize, self).__init__()
        self.sejits_active = False
        if target in core_dispatch:
            self.target_core = core_dispatch[target]
            self.sejits_active = True
        else:
            self.sejits_active = False

    def __call__(self, wrapped_func):
        """ docstring for __call__. """
        ret_func = None
        if self.sejits_active is False:
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

        def wrappee(*args, **kwargs):
            """ docstring for wrapped. """
            ret_func(*args, **kwargs)
        return wrappee


def fpga_dummy(*args, **kwargs):
    """
    fpga dummy method.

    returned in case of successfull specalization.
    """
    print "FPGA-Dummy Function"
