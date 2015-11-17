__author__ = 'philipp'


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


class FIA_Kernel_Linearizer(ast.NodeTransformer):
    def __init__(self):
        super(FIA_Kernel_Linearizer, self).__init__()
        #
        self.local_vars = dict()

    def run(self, ast):
        return self.visit(ast)

    def visit_TempAssign(self, node):
        if node.target.name not in self.local_vars:
            node_value = self.visit(node.value)
            self.local_vars[node.target.name] = node_value
        else:
            assert False, "{0} has been already used as assignment target!".format(node.target.name)

    def visit_Identifier(self, node):
        if node.name in self.local_vars:
            return self.local_vars[node.name]
        else:
            return node
            #assert False, "{0} undefined!".format(node.name)

    def visit_OutAssign(self, node):
        node_value = self.visit(node.value)
        return OutAssign(target=node.target, value=node_value)


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