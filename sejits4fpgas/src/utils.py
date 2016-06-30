# ---------------------------------------------------------------------------
STDLIBS = ["ieee", "ieee.std_logic_1164.all"]
# ---------------------------------------------------------------------------
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
