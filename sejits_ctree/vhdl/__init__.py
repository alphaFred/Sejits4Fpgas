
STDLIBS = ["ieee", "ieee.std_logic_1164.all"]


class TransformationError(Exception):

    """
    Exception that caused transformation not to occur.

    Attributes:
      msg -- the message/explanation to the user
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class VhdlNodeError(TransformationError):

    """
    Exception that caused node initialization not to occure.

    Attributes:
        msg:    message/explanation to the user
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
   

class VhdlTypeError(TransformationError):

    """
    Exception that caused type initialization not to occure.

    Attributes:
        msg:    message/explanation to the user
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class VhdlCodegenError(TransformationError):

    """
    Exception that caused code generation not to occure.

    Attributes:
        msg:    message/explanation to the user
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class VhdlJitSynthError(TransformationError):

    """
    Exception that caused JIT synthetis not to occure.

    Attributes:
        msg:    message/explanation to the user
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
