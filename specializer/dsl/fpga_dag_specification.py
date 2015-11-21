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
                   args)

    DagBinOp(op,
             cons=Buffer,
             prod=Buffer,
             next=types.ListType)

    DagImageFilter(cons=Buffer,
                   prod=Buffer,
                   next=types.ListType)

    DagImagePointOp(op,
                    cons=Buffer,
                    prod=Buffer,
                    next=types.ListType)
'''
