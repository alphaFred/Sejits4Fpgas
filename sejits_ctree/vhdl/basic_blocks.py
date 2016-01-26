""" Basic_Blocks contains all basic vdhl blocks backed by prewritten vhdl source code """

from nodes import Entity, Signal, Component, Generic, Port
from nodes import VhdlFile
from nodes import VhdlType

from ..vhdl import TransformationError


class BasicBlock(object):

    """ Base class for all vhdl basic blocks. """

    pass


class convolve(BasicBlock, VhdlFile):

    vhdl_path = "/home/philipp/University/M4/Masterthesis/src/git_repo/ebensberger_ma/BasicBlocks.vhd"
    lib_name = "work.BasicBlocks"
    # all vhdl files neccessary to build the module

    def __init__(self, args):
        # check input
        self._check_input(args)
        # process input
        args[1].vhdl_type.generated = False
        args[1].vhdl_type.type_def = "filtMASK"
        generics = [Generic("MASK", args[1]),
                    Generic("DIV", args[2]),
                    Generic("IN_BITWIDTH", args[3])]
        in_ports = [Port("rgb_input", "in", args[0])]
        #
        out_type = args[0].vhdl_type
        out_port = Port("rgb_output", "out", Signal("dummy", out_type))
        entity = Entity(name="Convolve",
                        generics=generics,
                        in_ports=in_ports,
                        out_port=out_port)
        # initialize file
        BasicBlock.__init__(self)
        VhdlFile.__init__(self,
                          name="Convolve",
                          libs=[],
                          entity=entity,
                          architecture=None,
                          path=self.vhdl_path)
        self.generated = False
        # create component
        self.component = Component(name=self.name,
                                   generics=generics,
                                   in_ports=in_ports,
                                   out_port=out_port,
                                   out_type=out_type)
        self.component.lib_name = self.lib_name

    def _check_input(self, args):
        array_range = (-30, 30)
        try:
            assert type(args[0].vhdl_type) is VhdlType.VhdlStdLogicVector,\
                "Argument 1 of convolve must be of type VhdlStdLogicVector"

            assert type(args[1].vhdl_type) is VhdlType.VhdlArray,\
                "Argument 2 of convolve must be of type VhdlArray"

            assert len(args[1].vhdl_type) == 9,\
                "Argument 2 of convolve must be an array of size==8"
            assert type(args[1].vhdl_type.item_vhdl_type) is VhdlType.VhdlUnsigned,\
                "Items of argument 2 of convolve must be of type VhdlUnsigned"
            assert args[1].vhdl_type.min >= array_range[0]\
                and args[1].vhdl_type.max <= array_range[1],\
                "Argument 2 of convolve must be in the range of {}".\
                format(str(array_range))

            assert type(args[2].vhdl_type) is VhdlType.VhdlUnsigned,\
                "Argument 3 of convolve must be of type VhdlUnsigned"
            assert type(args[3].vhdl_type) is VhdlType.VhdlUnsigned,\
                "Argument 4 of convolve must be of type VhdlUnsigned"
        except IndexError:
            error_msg = "Not enough arguments for convolve basic block"
            raise TransformationError(error_msg)

    def __call__(self):
        """ execute python code """
        pass


class sqrt(BasicBlock, VhdlFile):
    vhdl_path = "/home/philipp/University/M4/Masterthesis/src/git_repo/ebensberger_ma/BasicBlocks.vhd"
    lib_name = "work.BasicBlocks"

    def __init__(self, args):
        in_ports = [Port("sqrt_input", "in", args[0])]
        #
        out_type = args[0].vhdl_type
        out_port = Port("sqrt_output", "out", Signal("dummy", out_type))
        #
        entity = Entity(name="Squareroot",
                        generics=[],
                        in_ports=in_ports,
                        out_port=out_port)
        #
        BasicBlock.__init__(self)
        VhdlFile.__init__(self,
                          name="Squareroot",
                          libs=[],
                          entity=entity,
                          architecture=None,
                          path=self.vhdl_path)
        self.generated = False
        #
        self.component = Component(name=self.name,
                                   generics=None,
                                   in_ports=in_ports,
                                   out_port=out_port,
                                   out_type=out_type)
        self.component.lib_name = self.lib_name


BASICBLOCKS = {"convolve": convolve,
               "sqrt": sqrt}
