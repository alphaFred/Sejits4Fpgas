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
        """ Initalize Specialize. """
        super(Specialize, self).__init__()
        # check if target hardware is supported
        if target in core_dispatch:
            self.target_core = core_dispatch[target]
            self.target_supp = True
        else:
            self.target_supp = False

    def __call__(self, wrapped_func):
        """ docstring for __call__. """
        ret_func = None
        if self.target_supp:
            try:
                assert wrapped_func.func_defaults is not None,\
                    "ERROR NO FUNC_DEFAULTS!"
                # zip function arguments
                func_args = tuple(zip(wrapped_func.func_code.co_varnames,
                                      wrapped_func.func_defaults))
                # TODO: copy target execution here
                self.kernel_core = self.target_core(func_args, wrapped_func)
                self.kernel_core.run()
            except Exception:
                print traceback.print_exc()
                ret_func = wrapped_func
            else:
                ret_func = wrapped_func
        else:
            ret_func = wrapped_func

        def wrappee(*args, **kwargs):
            """ docstring for wrapped. """
            return ret_func(*args, **kwargs)
        return wrappee


def fpga_dummy(*args, **kwargs):
    """
    fpga dummy method.

    returned in case of successfull specalization.
    """
    print "FPGA-Dummy Function"
