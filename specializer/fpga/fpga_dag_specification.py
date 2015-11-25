""" docstring for fpga_dag_specification. """
__author__ = 'philipp ebensberger'

import ast


class DagNode(ast.AST):

    """ Describes base class for Dag-Nodes. """

    iput_intf = None
    oput_intf = None
    prev = None
    next = None
    d = None
    d_prev = None

    def __init__(self, iput_intf, oput_intf, prev=[], next=[], d=int, d_prev=int):
        """
        Initialize class variables.

        prev: List of previous Dag-Nodes
        next: List of subsequent Dag-Nodes
        d:    Propagation delay of Dag-Node
        """
        self._attributes = ('iput_intf', 'oput_intf', 'prev', 'next', 'd', 'd_prev')
        self._fields = ('prev', 'next')
        super(DagNode, self).__init__(lineno=None, col_offset=None)
        self.iput_intf = iput_intf
        self.oput_intf = oput_intf
        self.prev = prev
        self.next = next
        self.d = d
        self.d_prev = d_prev


class DagNodeInImage(DagNode):

    """ Describes an InImage Dag-Node. """

    def __init__(self, **kwargs):
        """ Initalize base class and class variables. """
        super(DagNodeInImage, self).__init__(**kwargs)


class DagNodeOutImage(DagNode):

    """ Describes an OutImage Dag-Node. """

    def __init__(self, **kwargs):
        """ Initalize base class and class variables. """
        super(DagNodeOutImage, self).__init__(**kwargs)


class DagNodeImgFilter(DagNode):

    """ Describes an Image Filter Dag-Node. """

    def __init__(self, **kwargs):
        """ Initalize base class and class variables. """
        super(DagNodeImgFilter, self).__init__(**kwargs)


class DagNodeImgPointOp(DagNode):

    """ Describes an Image Point Operator Dag-Node. """

    def __init__(self, **kwargs):
        """ Initalize base class and class variables. """
        super(DagNodeImgPointOp, self).__init__(**kwargs)


class DagNodeBinOp(DagNode):

    """ Describes an Binary Operator Dag-Node. """

    def __init__(self, **kwargs):
        """ Initialize base class and class variables. """
        super(DagNodeBinOp, self).__init__(**kwargs)


class DagNodeDReg(DagNode):

    """ Describes an Delay Register Dag-Node. """

    def __init__(self, **kwargs):
        """ Initalize base class and class variables. """
        super(DagNodeDReg, self).__init__(**kwargs)

dag_node_dict = {"DagNodeInImage": DagNodeInImage,
                 "DagNodeOutImage": DagNodeOutImage,
                 "DagNodeImgFilter": DagNodeImgFilter,
                 "DagNodeImgPointOp": DagNodeImgPointOp,
                 "DagNodeBinOp": DagNodeBinOp}
