""" docstring for fpga_dag_specification. """
__author__ = 'philipp ebensberger'

import ast


class DagNode(ast.AST):

    """ Describes base class for Dag-Nodes. """

    prev = None
    next = None
    d = None

    def __init__(self, prev=[], next=[], d=int):
        """
        Initialize class variables.

        prev: List of previous Dag-Nodes
        next: List of subsequent Dag-Nodes
        d:    Propagation delay of Dag-Node
        """
        self._fields = ('prev', 'next')
        super(DagNode, self).__init__(lineno=None, col_offset=None)
        self.prev = prev
        self.next = next
        self.d = d


class DagNodeInImage(DagNode):

    """ Describes an InImage Dag-Node. """

    def __init__(self):
        """ Initalize class variables. """
        pass
