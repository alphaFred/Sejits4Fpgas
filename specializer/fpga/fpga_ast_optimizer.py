""" docstring for module fpga_ast_optimizer. """
__author__ = 'philipp'


import ast

from subprocess import Popen, PIPE
from collections import namedtuple
from asp import tree_grammar
from specializer.dsl.fpga_dag_specification import dag_spec


Pixel = namedtuple('Pixel', ['mode', 'byte_size'])
PixelMask = namedtuple('PixelMask', ['height', 'width', 'pattern', 'pixel'])

PipelineObj = namedtuple(
    'PipelineObj', ['id', 'consumer', 'producer', 'next_id', 'next'])

def prittyprinter(flow_data, data_flow_graph):
    """ docstring for pprinter. """
    formats = {"ImageFilter": ', style=filled, fillcolor="#00EB5E"',
               "ImagePointOp": ', style=filled, fillcolor="#C2FF66"',
               "TempAssign": ', style=filled, fillcolor="#66C2FF"',
               "OutAssign": ', style=filled, fillcolor="#6675FF"',
               "InImageObj": ', style=filled, fillcolor="#FFF066"',
               "OutImageObj": ', style=filled, fillcolor="#FFA366"'
               }
    # generate dot
    graphviz_opts = ['rankdir="LR"']
    dot_text = "digraph G {\n %s \n" % str.join("\n", graphviz_opts)
    print "\n\n"
    for f_obj in data_flow_graph:
        flow_obj = flow_data[f_obj]
        print flow_obj
        dot_text += '%s ["label"="%s"%s];\n' % (
            flow_obj.next_id, flow_obj.id, formats.get(flow_obj.id, ""))
        for next_obj in flow_obj.next:
            dot_text += '%s -> %s ["label"="%s"];\n' % \
                (flow_obj.next_id,
                    next_obj.next_id,
                    str(flow_obj.producer.__class__.__name__
                        + "->" + next_obj.consumer.__class__.__name__))
    dot_text += "}"
    #
    print dot_text
    #
    dot_args = ['dot'] + ['-T', 'png']
    p = Popen(dot_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(dot_text.encode('utf-8'))
    #
    print "stderr:", stderr
    #
    with open("./images/" + "data_flow_graph.png", "wb") as f:
        f.write(stdout)


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
        # tree_grammar.parse(dag_spec, globals(), checker=None)
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

    def run(self):
        """ docstring for run. """
        linearizer = FpgaAstLinearizer()
        lin_ast = linearizer.run(self.ast)
        self.visit(lin_ast)
        return(self.FpgaDAG.dag_objects[0])

    def getAstNodes(self):
        """ return dict of all special DataFlow nodes. """
        ret = {"DFImageFilter": DFImageFilter,
               "DFBinOp": DFBinOp,
               "DFOutImage": DFOutImage,
               "DFInImage": DFInImage,
               "DagOutImage": DagOutImage,
               "DagImageFilter": DagImageFilter,
               "DagInImage": DagInImage,
               "DagImagePointOp": DagImagePointOp}
        return ret

    def visit_KernelModule(self, node):
        self.visit(node.body[0])

    def visit_DFOutImage(self, node):
        """ Visitor-Method for DFOutImage. """
        prev = self.visit(node.prev)
        #
        dag_node = DagOutImage()
        self.FpgaDAG.add(node, dag_node)
        self.FpgaDAG.update_next(prev, dag_node)
        #
        return hash(node)

    def visit_ImagePointOp(self, node):
        """ Visitor-Method for ImagePointOp. """
        prev = self.visit(node.target)
        #
        dag_node = DagImagePointOp(next=[])
        self.FpgaDAG.add(node, dag_node)
        self.FpgaDAG.update_next(prev, dag_node)
        #
        return hash(node)

    def visit_ImageFilter(self, node):
        """ Visitor-Method for ImageFilter. """
        prev = self.visit(node.target)
        #
        dag_node = DagImageFilter(next=[])
        self.FpgaDAG.add(node, dag_node)
        self.FpgaDAG.update_next(prev, dag_node)
        #
        return hash(node)

    def visit_BinOp(self, node):
        """ Visitor-Method for BinOp. """
        prev_left = self.visit(node.left)
        prev_right = self.visit(node.right)
        #
        dag_node = DagBinOp(next=[])
        #
        for prev in (prev_left, prev_right):
            self.FpgaDAG.add(node, dag_node)
            self.FpgaDAG.update_next(prev, dag_node)
        return hash(node)

    def visit_InImageObj(self, node):
        """ Visitor-Method for InImageObj. """
        dag_node = DagInImage(next=[])
        self.FpgaDAG.add(node, dag_node)
        #
        return hash(node)


class DagOutImage(ast.AST):
    _attributes = ('lineno', 'col_offset')
    _fields = []
    def label(self):
        """ return label for graphviz node. """
        return ""

class DagInImage(ast.AST):
    _attributes = ('lineno', 'col_offset')
    _fields = ['next']
    next = None
    def label(self):
        """ return label for graphviz node. """
        return ""

class DagImageFilter(ast.AST):
    _attributes = ('lineno', 'col_offset')
    _fields = ['next']
    next = None
    def label(self):
        """ return label for graphviz node. """
        return ""

class DagImagePointOp(ast.AST):
    _attributes = ('lineno', 'col_offset')
    _fields = ['next']
    next = None
    def label(self):
        """ return label for graphviz node. """
        return ""

class DagBinOp(ast.AST):
    _attributes = ('lineno', 'col_offset')
    _fields = ['next']
    next = None
    def label(self):
        """ return label for graphviz node. """
        return ""

class DFImageFilter(ast.AST):

    """ docstring for DFImageFilter. """

    _attributes = ('lineno', 'col_offset')
    _fields = ['filter', 'next']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    filter = None
    next = None

    def label(self):
        """ return label for graphviz node. """
        return ""


class DFBinOp(ast.AST):

    """ docstring for DFBinOp. """

    _attributes = ('lineno', 'col_offset')
    _fields = ['left', 'right']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    left = None
    right = None

    def label(self):
        """ return label for graphviz node. """
        return ""


class DFInImage(ast.AST):

    """ docstring for DFOutAssign. """

    _attributes = ('lineno', 'col_offset')
    _fields = ['id', 'mode', 'size', 'next']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    id = None
    mode = None
    size = None
    next = None

    def label(self):
        """ return label for graphviz node. """
        return ""


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
