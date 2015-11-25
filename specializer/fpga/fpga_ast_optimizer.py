""" docstring for module fpga_ast_optimizer. """
__author__ = 'philipp'


import ast
import fpga_dag_specification as dag

from asp import tree_grammar
from specializer.dsl.fpga_dag_specification import dag_spec


class FpgaAstOptimizer(ast.NodeTransformer):

    """ docstring for FpgaAstOptimizer. """

    class FpgaDag(object):

        """ docstring for FpgaDag. """

        def __init__(self):
            self.dag_objects = []
            self.dag_obj_dict = dict()

        def add(self, node, dag_node):
            if hash(node) not in self.dag_obj_dict:
                self.dag_objects.append(dag_node)
                self.dag_obj_dict[hash(node)] = len(self.dag_objects) - 1

        def update_next(self, prev_hash, next_node):
            obj_idx = self.dag_obj_dict[prev_hash]
            self.dag_objects[obj_idx].next.append(next_node)

    def __init__(self, ast, dsl_ast_classes):
        """
        docstring for __init__.

        Update globals() with:
            - DSL object classes
            - DAG object classes
        """
        super(FpgaAstOptimizer, self).__init__()
        # add dsl ast object classes
        globals().update(dsl_ast_classes)
        # add dag object classes
        self.dag_classes = dict()
        tree_grammar.parse(dag_spec, self.dag_classes, checker=None)
        globals().update(self.dag_classes)
        #
        self.FpgaDAG = self.FpgaDag()
        # self.FpgaDAG = namedtuple('FpgaDAG', ['objects', 'objs_dict'])
        # self.FpgaDAG(objects=[], objs_dict=dict())
        #
        self.ast = ast
        self.identifiers = dict()
        self.data_flow = dict()
        self.flow_id = 0
        self.data_flow_graph = []
        #
        self.dag_obj = []
        self.dag_dict = dict()
        #
        self.node_visits = dict()
        #
        self.ast_dag = []
        self.current_ast_dag = []
        self.ast_dag_set = set()
        self.dag_creation = False

    def run(self):
        """ docstring for run. """
        run_return = self.visit(self.lin_ast)
        self.dag_creation = True
        # run visitor again to create DAG
        self.visit(self.lin_ast)
        for item in self.ast_dag:
            print item
        return run_return

    def run_lin(self):
        """ docstring for run_lin. """
        linearizer = FpgaAstLinearizer()
        self.lin_ast = linearizer.run(self.ast)
        return(self.lin_ast)

    def getAstNodes(self):
        """ return dict of all special DataFlow nodes. """
        return self.dag_classes

    def visit_KernelModule(self, node):
        self.current_ast_dag = self.ast_dag
        return self.visit(node.body[0])

    def visit_DFOutImage(self, node):
        """ Visitor-Method for DFOutImage. """
        if self.dag_creation is False:
            node_hash = hash(node)
            self.node_visits[node_hash] =\
                self.node_visits.get(node_hash, 0) + 1
            return DagOutImageObj(id=node.id,
                                  mode=node.mode,
                                  size=node.size,
                                  cons=Datum(bit_size=32),
                                  prod=Datum(bit_size=24),
                                  prev=self.visit(node.prev),
                                  args=None,
                                  node_hash=hash(node))
        else:
            self.current_ast_dag.append(node)
            self.ast_dag_set.add(hash(node))
            self.visit(node.prev)

    def visit_ImagePointOp(self, node):
        """ Visitor-Method for ImagePointOp. """
        if self.dag_creation is False:
            self.node_visits[hash(node)] =\
                self.node_visits.get(hash(node), 0) + 1
            return DagImagePointOp(op=node.op,
                                   cons=Data(width=3, bit_size=24),
                                   prod=Datum(bit_size=32),
                                   prev=self.visit(node.target),
                                   node_hash=hash(node))
        else:
            node_hash = hash(node)
            if node_hash not in self.ast_dag_set and self.node_visits[node_hash] > 1:
                self.ast_dag.append(node)
                self.current_ast_dag = self.ast_dag
                self.ast_dag_set.add(node_hash)
            elif node_hash not in self.ast_dag_set:
                self.current_ast_dag.append(node)
                self.ast_dag_set.add(hash(node))
            else:
                pass
            self.visit(node.target)

    def visit_ImageFilter(self, node):
        """ Visitor-Method for ImageFilter. """
        if self.dag_creation is False:
            self.node_visits[hash(node)] =\
                self.node_visits.get(hash(node), 0) + 1
            return DagImageFilter(cons=Data(width=3, bit_size=24),
                                  prod=Datum(bit_size=24),
                                  prev=self.visit(node.target),
                                  node_hash=hash(node))
        else:
            node_hash = hash(node)
            if node_hash not in self.ast_dag_set and self.node_visits[node_hash] > 1:
                self.ast_dag.append(node)
                self.current_ast_dag = self.ast_dag
                self.ast_dag_set.add(node_hash)
            elif node_hash not in self.ast_dag_set:
                self.current_ast_dag.append(node)
                self.ast_dag_set.add(hash(node))
            else:
                pass
            self.visit(node.target)

    def visit_BinOp(self, node):
        """ Visitor-Method for BinOp. """
        if self.dag_creation is False:
            self.node_visits[hash(node)] =\
                self.node_visits.get(hash(node), 0) + 1
            left = self.visit(node.left)
            right = self.visit(node.right)

            assert type(left.prod) is type(right.prod)

            return DagBinOp(op=node.op,
                            left=left,
                            right=right,
                            cons=left.prod,
                            prod=left.prod,
                            node_hash=hash(node))
        else:
            self.current_ast_dag.append([[], []])
            #
            left_ref = self.current_ast_dag[-1][0]
            right_ref = self.current_ast_dag[-1][1]
            #
            self.current_ast_dag = left_ref
            self.visit(node.left)
            self.current_ast_dag = right_ref
            self.visit(node.right)
            pass

    def visit_InImageObj(self, node):
        """ Visitor-Method for InImageObj. """
        if self.dag_creation is False:
            self.node_visits[hash(node)] =\
                self.node_visits.get(hash(node), 0) + 1
            return DagInImageObj(id=node.id,
                                 node_hash=hash(node),
                                 mode=node.mode,
                                 size=node.size,
                                 cons=Datum(bit_size=24),
                                 prod=Datum(bit_size=32),
                                 args=node.args)
        else:
            node_hash = hash(node)
            if node_hash not in self.ast_dag_set and self.node_visits[node_hash] > 1:
                self.ast_dag.append(node)
                self.current_ast_dag = self.ast_dag
                self.ast_dag_set.add(node_hash)
            elif node_hash not in self.ast_dag_set:
                self.current_ast_dag.append(node)
                self.ast_dag_set.add(hash(node))
            else:
                pass


class DFOutImage(ast.AST):

    """ docstring for DFOutAssign. """

    _attributes = ('lineno', 'col_offset')
    _fields = ['id', 'mode', 'size', 'prev']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    id = None
    mode = None
    size = None
    prev = None

    def label(self):
        """ return label for graphviz node. """
        return ""


class FpgaAstLinearizer(ast.NodeTransformer):

    """ docstring for FpgaAstLinearizer. """

    def __init__(self):
        """ docstring for __init__. """
        super(FpgaAstLinearizer, self).__init__()
        #
        self.local_vars = dict()

    def run(self, ast):
        """ docstring run. """
        return self.visit(ast)

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

    def visit_ImageFilter(self, node):
        """ docstring visit ImageFilter. """
        return ImageFilter(filter=node.filter,
                           target=self.visit(node.target))

    def visit_BinOp(self, node):
        """ docstring visit_BinOp. """
        return BinOp(left=self.visit(node.left),
                     op=node.op,
                     right=self.visit(node.right))

    def visit_OutAssign(self, node):
        """ docstring visit_OutAssign. """
        node_value = self.visit(node.value)
        return DFOutImage(id=node.var.id,
                          mode=node.var.mode,
                          size=node.var.size,
                          prev=node_value)


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
        #print ast.dump(dag_graph[-1])
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



'''
class FiaKernelOptimizer(ast.NodeTransformer):

    def __init__(self):
        # parse dsl specification
        # initialize super classes
        super(FIA_Kernel_Optimizer, self).__init__()
        #
        self.kernel_linearizer = FiaKernelLinearizer()
        self.kernel_converter = FIA_Kernel_DomainConverter()
        self.localVars = {}

    def run(self, ast_data):
        """ docstring for run. """
        return self.visit(ast_data)

    def visit_Module(self, node):
        """ docstring for visit_Module. """
        # perform ast linearization
        kernel_linearized = self.kernel_linearizer.run(node)
        # DEBUG
        print "\nKERNEL LINEARIZED\n"
        pformat_ast(kernel_linearized)
        print "#" * 80, "\n\n"
        # !DEBUG
        kernel_unrolled = self.kernel_converter.run(kernel_linearized)
        return kernel_unrolled


class Data_Widening(ast.AST):
    """docstring for Data_Widening"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['source', 'sink', 'factor']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    source = None
    sink = None
    factor = None


class Data_Shortening(ast.AST):
    """docstring for Data_Shortening"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['source', 'sink', 'factor']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    source = None
    sink = None
    factor = None


class Data_Buffer(ast.AST):
    """docstring for Data_Buffer"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['source', 'sink', 'width']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    source = None
    sink = None
    width = None


class Data_Get(ast.AST):
    """docstring for Data_Get"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['data_in', 'source', 'data_out']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    data_in = None
    source = None
    data_out = None


class Data_Set(ast.AST):
    """docstring for Data_Set"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['data_in', 'sink', 'mode', 'data_out']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    data_in = None
    sink = None
    mode = None
    data_out = None


class Data_Op(ast.AST):
    """docstring for Data_Op"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['data_in', 'op', 'num_op', 'data_out']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    data_in = None
    op = None
    num_op = None
    data_out = None


class Data_Op_Min(ast.AST):
    """docstring for Data_Op_Min"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['data_in', 'data_out']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    data_in = None
    data_out = None


class Data_Buffer(ast.AST):
    """docstring for Data_Buffer"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['data_in', 'buff_width', 'data_out']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    data_in = None
    buff_width = None
    data_out = None


DataIface = namedtuple('DataIface', ['width', 'depth'])


class FIA_Kernel_DomainConverter(ast.NodeTransformer):
    """docstring for FIA_Kernel_DomainConverter"""

    def __init__(self):
        super(FIA_Kernel_DomainConverter, self).__init__()
        #
        self.ChunkWidth = 32
        #
        self.DataFlowGraph = []

    def pprinter(self, item):
        if isinstance(item, Data_Get):
            print "Data_Get"
            for attr in item._fields:
                print "\t", attr, getattr(item, attr)
        elif isinstance(item, Data_Set):
            print "Data_Set"
            for attr in item._fields:
                print "\t", attr, getattr(item, attr)
        elif isinstance(item, Data_Op):
            print "Data_Op"
            for attr in item._fields:
                n_attr = getattr(item, attr)
                if isinstance(n_attr, list):
                    for i in n_attr:
                        self.pprinter(i)
                else:
                    print "\t", attr, n_attr
        else:
            print "\t", item.__class__.__name__
            for attr in item._fields:
                print "\t\t", attr, getattr(item, attr)

    def run(self, ast):
        self.visit(ast)
        for item in self.DataFlowGraph:
            self.pprinter(item)
        return self.DataFlowGraph

    def visit_OutAssign(self, node):
        self.visit(node.value)
        #
        fia_object = Data_Set()
        fia_object.data_in = DataIface(width=self.ChunkWidth, depth=4)
        fia_object.sink = id(node)
        fia_object.data_out = DataIface(
            width=self.ChunkWidth, depth=node.target.height * node.target.width)
        #
        self.DataFlowGraph.append(fia_object)
        #
        return

    def visit_ImagePointOp(self, node):
        self.visit(node.target)
        #
        fia_object = Data_Op()
        fia_object.data_in = DataIface(width=self.ChunkWidth, depth=1)
        fia_object.op = [node.op]
        fia_object.data_out = DataIface(width=self.ChunkWidth, depth=1)
        #
        self.DataFlowGraph.append(fia_object)
        #
        return

    def visit_ImageFilter(self, node):
        self.visit(node.target)
        #
        fia_object = Data_Op()
        fia_object.data_in = DataIface(
            width=self.ChunkWidth, depth=node.filter.args["size"])
        #
        fia_object.op = [Data_Op_Min(
            DataIface(width=self.ChunkWidth,
                      depth=node.filter.args["size"]**2),
            DataIface(width=self.ChunkWidth, depth=1))]
        #
        fia_object.data_out = DataIface(width=self.ChunkWidth, depth=1)
        #
        self.DataFlowGraph.append(fia_object)
        #
        return

    def visit_InImageObj(self, node):
        fia_object = Data_Get()
        fia_object.data_in = DataIface(
            width=self.ChunkWidth, depth=node.height * node.width)
        fia_object.source = id(node)
        fia_object.data_out = DataIface(width=self.ChunkWidth, depth=4)
        #
        self.DataFlowGraph.append(fia_object)
        #
        return

entity_add = "{0} : component dsp_AddSub_block\
    port map (\
        A => {1},\
        B => {2},\
        SEL => {3},\
        CLK => {4},\
        CE => {5},\
        RST => {6},\
        P => {7}\
    );"

entity_get = "{0} : component data_get\
    port map (\
        IN => {1},\
        OUT => {2},\
        CLK => {3},\
        P => {4}\
    );"


class VHDL_CodeGen(ast.NodeTransformer):

    def __init__(self):
        super(VHDL_CodeGen, self).__init__()
        self.signals = []
        self.entities = []
        self.prev_interface = None

    def run(self, ast):
        for item in ast:
            self.visit(item)

    def generic_visit(self, node):
        print type(node)

    def visit_Data_Get(self, node):
        self.prev_interface = ["chunk_sig_{0}".format(
            i) for i in range(0, node.data_out.depth)]
        print "Data_Get"
        for sig in self.prev_interface:
            print "\t output:", sig

    def visit_Data_Op(self, node):
        op_sig_out = []
        if len(self.prev_interface) % node.data_in.depth == 0:
            for new_block in range(0, len(
                    self.prev_interface) / node.data_in.depth):
                inpt_sig = []
                print "OP-Block", new_block
                for i in range(0, node.data_in.depth):
                    print "\t input:", self.prev_interface[new_block * node.data_in.depth + i]
                for i in range(0, node.data_out.depth):
                    out_sig = "chunk_sig_opBlock_{0}_{1}".format(new_block, i)
                    print "\t output:", out_sig
                    op_sig_out.append(out_sig)
        self.prev_interface = op_sig_out

    def visit_Data_Set(self, node):
        if len(self.prev_interface) <= node.data_in.depth:
            print "Data_Set"
            for sig in self.prev_interface:
                print "\t input:", sig
'''
