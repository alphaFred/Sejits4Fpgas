""" Contains the DAG specification for FPGA Specializetion. """
__author__ = 'philipp ebensberger'

dag_spec = '''
    Buffer = Datum
           | Data

    Datum(bit_size=types.IntType)
    Data(width=types.IntType, bit_size=types.IntType)

    DagInImageObj(id=types.StringType,
                  mode=types.StringType,
                  size=types.TupleType,
                  prod=Buffer,
                  next=types.ListType,
                  args)

    DagOutImageObj(id=types.StringType,
                   mode=types.StringType,
                   size=types.TupleType,
                   cons=Buffer,
                   next=types.NoneType,
                   args)

    DagBinOp(left=Int|Float|Identifier|InImageObj|DataOp,
             op,
             right=Int|Float|Identifier|InImageObj|DataOp,
             cons=Buffer,
             prod=Buffer,
             next=types.ListType)

    Filter = DagMinFilter
           | DagMaxFilter
           | DagDummyFilter

    DagMinFilter(cons=Buffer, prod=Buffer)
    DagMaxFilter(cons=Buffer, prod=Buffer)
    DagDummyFilter(cons=Buffer, prod=Buffer)

    DagImageFilter(target=(InImageObj|Identifier|DataOp),
                   filter=Filter,
                   cons=Buffer,
                   prod=Buffer,
                   next=types.ListType)

    DagImagePointOp(target=(InImageObj|Identifier|DataOp),
                    op=Expr|ast.BinOp,
                    cons=Buffer,
                    prod=Buffer,
                    next=types.ListType)
'''
