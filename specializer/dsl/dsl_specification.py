__author__ = 'philipp ebensberger'
"""
.. module:: dsl_specification
   :platform: Unix
   :synopsis: Describes the DSL

.. moduleauthor:: Philipp Ebensberger <philipp.ebensberger@fau.de>
"""

import ast
import types


dsl = '''

    Expr = Constant
         | Identifier
         | ImageObj
         | InImageObj

    Index(n=types.IntType)

    KernelModule(id=types.StringType, body)

    Input(id=types.StringType)

    Int(id=types.StringType|types.NoneType,n=types.IntType, args)
    Float(id=types.StringType|types.NoneType,n=types.FloatType, args)
    Constant(id=types.StringType, value=Int|Float, args)

    Identifier(name=types.StringType)

    DataOp = ImageFilter
           | ImagePointOp
           | BinOp

    BinOp(left=Int|Float|Identifier|InImageObj|DataOp, op,
          right=Int|Float|Identifier|InImageObj|DataOp)

    InImageObj(id=types.StringType,
               mode=types.StringType,
               size=types.TupleType,
               args)
    OutImageObj(id=types.StringType,
                mode=types.StringType,
                size=types.TupleType)

    ReturnAssign(value=OutImageObj)
    TempAssign(var=Identifier, value=Expr|DataOp)
    OutAssign(var=OutImageObj, value=Expr|DataOp)

    # -------------------------------------------------------------------------
    # Image Filter
    # -------------------------------------------------------------------------
    Filter = MinFilter
           | MaxFilter
           | Kernel

    MinFilter(size=Int)
    MaxFilter(size=Int)
    Kernel(size=Int,
           kernel=types.ListType,
           scale=Int|Types.NoneType,
           offset=Int)

    ImageFilter(target=(InImageObj|Identifier|DataOp), filter=Filter)
    ImagePointOp(target=(InImageObj|Identifier|DataOp), op=Expr|ast.BinOp)
    '''


"""


###############################################################################


    #FIAKernel(globals_used=types.DictType, body=)

    ImageObj(id=types.StringType, mode=types.StringType, size=types.TupleType)
    #Constant(id=types.StringType, type=types.IntType)

    InImagesList(type=types.StringType)

    # dsl representation if in_images consists of single image objects
    #   in_images[x1, x2, x3, x4]
    #InImageObj(width=types.IntType, height=types.IntType)

    # dsl representation if in_images consists of single lists of image objects
    #   in_images[[x1, x2], [x3, x4]]
    InImageObjIdx(index=types.IntType, width=types.IntType, height=types.IntType)

    # dsl representation for output
    #OutImageObj(width=types.IntType, height=types.IntType)

    # dsl representation of image filter
    #ImageFilter(target=(InImageObj|InImageObjIdx|ImagePointOp|Identifier), filter=types.NoneType|Filter)

    #ImagePointOp(target=(InImageObj|InImageObjIdx|Identifier), op=operator|types.NoneType)

    operator = Add | Sub | Mult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv

    # dsl representation of filter
    #Filter(name=types.StringType, args=types.DictType)

    #
    Point(name)

    

    # TempAssign(target=Identifier, value=InImageObj|InImageObjIdx|ImageFilter|Identifier|ImagePointOp|ast.BinOp)
    # OutAssign(target=OutImageObj, value=InImageObj|InImageObjIdx|ImageFilter|Identifier|ImagePointOp|ast.BinOp)
"""