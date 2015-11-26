""" docstring for module fpga_ast_optimizer. """
__author__ = 'philipp'


import ast
import fpga_dag_specification as dag


class FpgaDagCreator(ast.NodeTransformer):

    """ docstring for FpgaAstLinearizer. """

    def __init__(self):
        """ docstring for __init__. """
        super(FpgaDagCreator, self).__init__()
        #
        self.local_vars = dict()
        self.visited_nodes = dict()

    def run(self, iast):
        """ docstring run. """
        dag_graph = self.visit(iast)
        # print ast.dump(dag_graph[-1])
        return dag_graph[-1]

    def getDagDict(self):
        return dag.dag_node_dict

    def visit_KernelModule(self, node):
        return map(self.visit, node.body)

    def visit_OutAssign(self, node):
        """
        Return DagNodeOutImage.

        If node is visited create, cache and return new DagNodeOutImage

        Args:
            node: Node object of type OutAssign

        Return:
            Dag node object of type DagNodeOutImage
        """
        # TODO: check if hashing and caching of this node is necessary
        node_hash = hash(node)
        # get previous nodes
        prev_node = self. visit(node.value)
        #
        dag_node = dag.DagNodeOutput(iput_intf=None,
                                     oput_intf=None,
                                     prev=[prev_node],
                                     next=[],
                                     d=1,
                                     d_prev=prev_node.d + prev_node.d_prev)
        self.visited_nodes[node_hash] = dag_node
        return dag_node

    def visit_TempAssign(self, node):
        """ docstring visit_TempAssign. """
        if node.var.name not in self.local_vars:
            node_value = self.visit(node.value)
            self.local_vars[node.var.name] = node_value
        else:
            assert False, "{0} has been already used as assignment target!"\
                .format(node.target.name)

    def visit_Identifier(self, node):
        """ docstring visit_Identifier. """
        if node.name in self.local_vars:
            return self.local_vars[node.name]
        else:
            return node

    def visit_BinOp(self, node):
        """
        Return DagNodeBinOp.

        If node is visited for the first time,
            create, chache and return new DagNodeBinOp.
        Else update cached DagNodeBinOp for this and return updated node.

        Args:
            node: Node object of type BinOP

        Returns:
            Dag node object of type DagNodeBinOp
        """
        node_hash = hash(node)
        # get previous nodes
        prev_node_left = self.visit(node.left)
        prev_node_right = self.visit(node.right)
        #
        d_prev_left, d_prev_right = (prev_node_left.d + prev_node_left.d_prev,
                                     prev_node_right.d + prev_node_right.d_prev)
        d_prev_diff = d_prev_left - d_prev_right
        if d_prev_diff < 0:
            dag_dreg = dag.DagNodeDReg(iput_intf=None,
                                       oput_intf=None,
                                       prev=[prev_node_left],
                                       next=prev_node_left.next
                                       if type(prev_node_left.next) is
                                       list else [prev_node_left.next],
                                       d=abs(d_prev_diff),
                                       d_prev=prev_node_left.d +
                                       prev_node_left.d_prev)
            prev_node_left.next = dag_dreg
            retimed_left = dag_dreg
            retimed_right = prev_node_right
        elif d_prev_diff > 0:
            dag_dreg = dag.DagNodeDReg(iput_intf=None,
                                       oput_intf=None,
                                       prev=[prev_node_right],
                                       next=prev_node_left.next
                                       if type(prev_node_left.next) is
                                       list else [prev_node_left.next],
                                       d=abs(d_prev_diff),
                                       d_prev=prev_node_right.d +
                                       prev_node_right.d_prev)
            prev_node_right.next = dag_dreg
            retimed_left = prev_node_left
            retimed_right = dag_dreg
        else:
            retimed_left = prev_node_left
            retimed_right = prev_node_right
        #
        if node_hash not in self.visited_nodes:
            dag_node = dag.DagNodeBinOp(iput_intf=None,
                                        oput_intf=None,
                                        prev=[retimed_left, retimed_right],
                                        next=[],
                                        d=1,
                                        d_prev=retimed_left.d + retimed_left.d_prev)
            retimed_left.next.append(dag_node)
            retimed_right.next.append(dag_node)
            # cache dag node
            self.visited_nodes[node_hash] = dag_node
            return dag_node
        else:
            assert False, "BinOp can not be visted multiple times!"


    def visit_ImagePointOp(self, node):
        """
        Return DagNodeImgPointOp.

        If node is visited for the first time,
            create, chache and return new DagNodeImgPointOp.
        Else update cached DagNodeImgPointOp for this and return updated node.

        Args:
            node: Node object of type ImagePointOp

        Returns:
            Dag node object of type DagNodeImgPointOp
        """
        node_hash = hash(node)
        # get previous node
        prev_node = self.visit(node.target)
        #
        if node_hash not in self.visited_nodes:
            dag_node = dag.DagNodePointOp(iput_intf=None,
                                          oput_intf=None,
                                          prev=[prev_node],
                                          next=[],
                                          d=1,
                                          d_prev=prev_node.d +
                                          prev_node.d_prev)
            prev_node.next.append(dag_node)
            # cache dag node
            self.visited_nodes[node_hash] = dag_node
            return dag_node
        else:
            # get cached dag node
            dag_node = self.visited_nodes[node_hash]
            #
            prev_node.next.append(dag_node)
            # update cached node
            dag_node.prev.append(prev_node)
            dag_node.d_prev = prev_node.d + prev_node.d_prev
            self.visited_nodes[node_hash] = dag_node
            # return updated dag node
            return dag_node

    def visit_ImageFilter(self, node):
        """
        Return DagNodeImgFilter.

        If node is visited for the first time,
            create, cache and return new DagNodeImgFilter.
        Else update cached DagNodeImgFilter for this and return updated node.

        Args:
            node: Node object of type ImageFilter

        Returns:
            Dag node object of type DagNodeImgFilter
        """
        node_hash = hash(node)
        # get previous node
        prev_node = self.visit(node.target)
        #
        if node_hash not in self.visited_nodes:
            dag_node = dag.DagNodeLocalOp(iput_intf=None,
                                          oput_intf=None,
                                          prev=[prev_node],
                                          next=[],
                                          d=1,
                                          d_prev=prev_node.d +
                                          prev_node.d_prev)
            prev_node.next.append(dag_node)
            # cache dag node
            self.visited_nodes[node_hash] = dag_node
            return dag_node
        else:
            prev_node.next.append(dag_node)
            # update cached node
            dag_node = self.visited_nodes[node_hash]
            dag_node.prev.append(prev_node)
            dag_node.d_prev = prev_node.d + prev_node.d_prev
            self.visited_nodes[node_hash] = dag_node
            # return updated dag node
            return dag_node

    def visit_InImageObj(self, node):
        """
        Return DagNodeInImage.

        If node is visited for the first time,
            create, cache and return new DagNodeInImage.
        Else return cached DagNodeInImage for this node.

        Args:
            node: Node object of type InImageObj

        Returns:
            Dag node object of type DagNodeInImage
        """
        node_hash = hash(node)
        if node_hash not in self.visited_nodes:
            dag_node = dag.DagNodeInput(iput_intf=None,
                                        oput_intf=None,
                                        prev=[],
                                        next=[],
                                        d=1,
                                        d_prev=0)
            # cache dag node
            self.visited_nodes[node_hash] = dag_node
            return dag_node
        else:
            # return cached dag node
            return self.visited_nodes[node_hash]
