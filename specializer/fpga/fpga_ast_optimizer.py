__author__ = 'philipp'


import ast
import os

from subprocess import Popen, PIPE
from collections import namedtuple


Pixel = namedtuple('Pixel',['mode','byte_size'])
PixelMask = namedtuple('PixelMask',['height','width','pattern','pixel'])

PipelineObj = namedtuple('PipelineObj',['id','consumer','producer', 'next_id','next'])

def pprinter(flow_data, data_flow_graph):
    formats = {"ImageFilter": ', style=filled, fillcolor="#00EB5E"',
               "ImagePointOp":', style=filled, fillcolor="#C2FF66"',
               "TempAssign":  ', style=filled, fillcolor="#66C2FF"',
               "OutAssign":   ', style=filled, fillcolor="#6675FF"',
               "InImageObj":  ', style=filled, fillcolor="#FFF066"',
               "OutImageObj": ', style=filled, fillcolor="#FFA366"'
               }
    # generate dot
    graphviz_opts = ['rankdir="LR"']
    dot_text = "digraph G {\n %s \n" % str.join("\n", graphviz_opts)
    print "\n\n"
    for f_obj in data_flow_graph:
        flow_obj = flow_data[f_obj]
        print flow_obj
        dot_text += '%s ["label"="%s"%s];\n' %(flow_obj.next_id, flow_obj.id, formats.get(flow_obj.id, ""))
        for next_obj in flow_obj.next:
            dot_text += '%s -> %s ["label"="%s"];\n' %(flow_obj.next_id, next_obj.next_id,str(flow_obj.producer.__class__.__name__ + "->" + next_obj.consumer.__class__.__name__))
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
    with open("./images/"+"data_flow_graph.png", "wb") as f:
                f.write(stdout)


class FpgaAstOptimizer(ast.NodeTransformer):
    """ docstring for FpgaAstOptimizer """
    def __init__(self, ast, dsl_classes):
        """ docstring for __init__ """
        globals().update(dsl_classes)
        super(FpgaAstOptimizer, self).__init__()
        self.ast = ast
        self.identifiers = dict()
        self.data_flow = dict()
        self.flow_id = 0
        self.data_flow_graph = []

    def run(self):
        bla = FIA_Kernel_Linearizer()
        return bla.run(self.ast)
        self.visit(self.ast)
        print self.data_flow
        print self.data_flow_graph
        pprinter(self.data_flow, self.data_flow_graph)

    def visit_OutAssign(self, node):
        prev = self.visit(node.value)
        if prev is not None:
            prev.next.append(self.visit(node.var))
            self.data_flow[prev.next_id] = prev
            self.data_flow_graph.append(prev.next_id)
            #
            next = self.visit(node.var)
            self.data_flow[next.next_id] = next
            self.data_flow_graph.append(next.next_id)
            """
            #
            self.data_flow_graph.append(prev)
            next = self.visit(node.var)
            if next is not None:
                self.data_flow_graph.append(next)
            """

    def visit_TempAssign(self, node):
        prev = self.visit(node.value)
        if prev is not None:
            self.data_flow_graph.append(prev)
            next = PipelineObj(id=node.var.name,
                               consumer=None,
                               producer=prev.producer)
            self.identifiers[node.var.name] = next

    def visit_ImagePointOp(self, node):
        prev = self.visit(node.value)
        if prev is not None:
            this = PipelineObj(id='ImagePointOp',
                               consumer=Pixel(mode='RGB', byte_size=3),
                               producer=Pixel(mode='RGB', byte_size=3),
                               next_id=hash(node),
                               next=[])
            prev.next.append(this)
            self.data_flow[prev.next_id] = prev
            self.data_flow_graph.append(prev.next_id)
            return this
            #
        """
        prev = self.visit(node.target)
        if prev is not None:
            self.data_flow_graph.append(prev)
            pipeObj = PipelineObj(id='ImagePointOp',
                                  consumer=Pixel(mode='RGB', byte_size=3),
                                  producer=Pixel(mode='RGB', byte_size=3))
            return pipeObj
        else:
            return None
        """

    def visit_ImageFilter(self, node):
        prev = self.visit(node.target)
        if prev is not None:
            this = PipelineObj(id='ImagePointOp',
                               consumer=PixelMask(height=node.filter.size.n,
                                                  width=node.filter.size.n,
                                                  pattern=[1,1,1,1,0,1,1,1,1],
                                                  pixel=Pixel(mode='RGB', byte_size=3)),
                               producer=Pixel(mode='RGB', byte_size=3),
                               next_id=hash(node),
                               next=[])
            prev.next.append(this)
            self.data_flow[prev.next_id] = prev
            self.data_flow_graph.append(prev.next_id)
            return this
        """
        prev = self.visit(node.target)
        if prev is not None:
            self.data_flow_graph.append(prev)
            # PixelMask = namedtuple('PixelMask',['height','width','pattern','pixel'])
            cons = PixelMask(height=node.filter.size.n,
                             width=node.filter.size.n,
                             pattern=[1,1,1,1,0,1,1,1,1],
                             pixel=Pixel(mode='RGB', byte_size=3))
            prod = Pixel(mode='RGB', byte_size=3)
            #
            pipeObj = PipelineObj(id='ImageFilter',
                                  consumer=cons,
                                  producer=prod)
            self.data_flow_graph.append(pipeObj)
            #
            return pipeObj
        else:
            return None
        """

    def visit_InImageObj(self, node):
        prod = Pixel(mode=node.mode, byte_size=3)
        ret = PipelineObj(id="InImageObj",
                          consumer=None,
                          producer=prod,
                          next_id=hash(node),
                          next=[])
        self.flow_id += 1
        return ret

    def visit_OutImageObj(self, node):
        cons = Pixel(mode=node.mode, byte_size=3)
        ret = PipelineObj(id="OutImageObj",
                          consumer=cons,
                          producer=None,
                          next_id=hash(node),
                          next=[])
        self.flow_id += 1
        return ret

    def visit_Identifier(self, node):
        return self.identifiers[node.name]







































class FIA_Kernel_Optimizer(ast.NodeTransformer):
    def __init__(self):
        # parse dsl specification
        # initialize super classes
        super(FIA_Kernel_Optimizer, self).__init__()
        #
        self.kernel_linearizer = FIA_Kernel_Linearizer()
        self.kernel_converter = FIA_Kernel_DomainConverter()
        self.localVars = {}

    def run(self, ast_data):
        return self.visit(ast_data)

    def visit_Module(self, node):
        # perform ast linearization
        kernel_linearized = self.kernel_linearizer.run(node)
        # DEBUG
        print "\nKERNEL LINEARIZED\n"
        pformat_ast(kernel_linearized)
        print "#"*80,"\n\n"
        # !DEBUG
        kernel_unrolled = self.kernel_converter.run(kernel_linearized)
        return kernel_unrolled

class DFImageFilter(ast.AST):
    """docstring for Data_Buffer"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['target']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    target = None

    def label(self):
        return ""

class DFBinOp(ast.AST):
    """docstring for Data_Buffer"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['left', 'right']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    left = None
    right = None

    def label(self):
        return ""

class DFOutAssign(ast.AST):
    """docstring for Data_Buffer"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['var', 'value']
    # _attributes
    col_offset = None
    lineno = None
    # _fields
    var = None
    value = None

    def label(self):
        return ""


class FIA_Kernel_Linearizer(ast.NodeTransformer):
    def __init__(self):
        super(FIA_Kernel_Linearizer, self).__init__()
        #
        self.local_vars = dict()

    def run(self, ast):
        return self.visit(ast)

    def visit_TempAssign(self, node):
        if node.var.name not in self.local_vars:
            node_value = self.visit(node.value)
            self.local_vars[node.var.name] = node_value
        else:
            assert False, "{0} has been already used as assignment target!".format(node.target.name)

    def visit_Identifier(self, node):
        if node.name in self.local_vars:
            return self.local_vars[node.name]
        else:
            return node

    def visit_ImageFilter(self, node):
        return DFImageFilter(filter=None, target=node.target)

    def visit_BinOp(self, node):
        return DFBinOp(left=self.visit(node.left), right=self.visit(node.right))

    def visit_OutAssign(self, node):
        node_value = self.visit(node.value)
        return DFOutAssign(var=node.var, value=node_value,)


class Data_Widening(ast.AST):
    """docstring for Data_Widening"""
    _attributes = ('lineno', 'col_offset')
    _fields = ['source','sink','factor']
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
    _fields = ['source','sink','factor']
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
    _fields = ['source','sink','width']
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
    _fields = ['data_in','sink','mode','data_out']
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


DataIface = namedtuple('DataIface',['width','depth'])


class FIA_Kernel_DomainConverter(ast.NodeTransformer):
    """docstring for FIA_Kernel_DomainConverter"""
    def __init__(self):
        super(FIA_Kernel_DomainConverter, self).__init__()
        #
        self.ChunkWidth = 32
        #
        self.DataFlowGraph = []

    def pprinter(self, item):
        if type(item) is Data_Get:
            print "Data_Get"
            for attr in item._fields:
                print "\t",attr,getattr(item, attr)
        elif type(item) is Data_Set:
            print "Data_Set"
            for attr in item._fields:
                print "\t",attr,getattr(item, attr)
        elif type(item) is Data_Op:
            print "Data_Op"
            for attr in item._fields:
                n_attr = getattr(item, attr)
                if type(n_attr) is list:
                    for i in n_attr:
                        self.pprinter(i)
                else:
                    print "\t",attr, n_attr
        else:
            print "\t",item.__class__.__name__
            for attr in item._fields:
                print "\t\t",attr,getattr(item, attr)

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
        fia_object.data_out = DataIface(width=self.ChunkWidth, depth=node.target.height*node.target.width)
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
        fia_object.data_in = DataIface(width=self.ChunkWidth, depth=node.filter.args["size"])
        #
        fia_object.op = [Data_Op_Min(\
                            DataIface(width=self.ChunkWidth, depth=node.filter.args["size"]**2),
                            DataIface(width=self.ChunkWidth, depth=1))]
        #
        fia_object.data_out = DataIface(width=self.ChunkWidth, depth=1)
        #
        self.DataFlowGraph.append(fia_object)
        #
        return

    def visit_InImageObj(self, node):
        fia_object = Data_Get()
        fia_object.data_in = DataIface(width=self.ChunkWidth, depth=node.height*node.width)
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
        self.prev_interface = ["chunk_sig_{0}".format(i) for i in range(0,node.data_out.depth)]
        print "Data_Get"
        for sig in self.prev_interface:
            print "\t output:", sig

    def visit_Data_Op(self, node):
        op_sig_out = []
        if len(self.prev_interface)%node.data_in.depth == 0:
            for new_block in range(0,len(self.prev_interface)/node.data_in.depth):
                inpt_sig = []
                print "OP-Block",new_block
                for i in range(0,node.data_in.depth):
                    print "\t input:",self.prev_interface[new_block*node.data_in.depth + i]
                for i in range(0,node.data_out.depth):
                    out_sig = "chunk_sig_opBlock_{0}_{1}".format(new_block,i)
                    print "\t output:",out_sig
                    op_sig_out.append(out_sig)
        self.prev_interface = op_sig_out

    def visit_Data_Set(self, node):
        if len(self.prev_interface) <= node.data_in.depth:
            print "Data_Set"
            for sig in self.prev_interface:
                print "\t input:",sig