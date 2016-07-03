from errors import TransformationError


class VhdlType(object):
    class _VhdlType(object):

        _fields = []
        vhdl_type = ""
        bit_dvalues = ()
        std_logic_dvalues = ("U", "X", "0", "1", "Z", "W", "L", "H", "-")
        generated = True

        def __str__(self):
            return self.vhdl_type

        def __repr__(self):
            return self.vhdl_type

    class VhdlSigned(_VhdlType):
        vhdl_type = "signed"

        def __init__(self, size):
            self.size = size

        def __len__(self):
            return self.size

        def __repr__(self):
            return self.vhdl_type + "({} downto 0)".format(self.size - 1)

    class VhdlUnsigned(_VhdlType):
        vhdl_type = "unsigned"

        def __init__(self, size):
            self.size = size

        def __len__(self):
            return self.size

        def __repr__(self):
            return self.vhdl_type + "({} downto 0)".format(self.size - 1)

    class VhdlPositive(_VhdlType):
        def __init__(self):
            # TODO: added length etc. which is normally necessary to declare positive
            pass

        vhdl_type = "positive"

    class VhdlInteger(_VhdlType):
        def __init__(self):
            pass

        vhdl_type = "integer"

    class VhdlString(_VhdlType):
        def __init__(self):
            pass

        vhdl_type = "string"

    class VhdlArray(_VhdlType):
        vhdl_type = "array"
        type_def = ""

        def __init__(self, size, itm_type, itm_min=None, itm_max=None, type_def=""):
            self.len = size
            self.item_vhdl_type = itm_type
            self.min = itm_min
            self.max = itm_max
            #
            self.type_def = type_def

        def __len__(self):
            return self.len

        @classmethod
        def from_list(cls, itms):
            itms = list(itms)
            size = len(itms)
            item_vhdl_type = itms[0].vhdl_type
            itm_min = min([itm.value for itm in itms])
            itm_max = max([itm.value for itm in itms])
            #
            return cls(size, item_vhdl_type, itm_min, itm_max)

        def __repr__(self):
            return self.vhdl_type

    class VhdlStdLogic(_VhdlType):
        vhdl_type = "std_logic"

        def __init__(self, default=None):
            if default:
                if hasattr(default, "__len__") \
                        and len(default) == 1 \
                        and default in self.std_logic_dvalues:
                    self.default = ["'" + ditm + "'" for ditm in default]
                else:
                    error_msg = "Illegal default value for {0}". \
                        format(self.__class__.__name__)
                    raise TransformationError(error_msg)
            else:
                self.default = "'0'"

    class VhdlStdLogicVector(_VhdlType):
        vhdl_type = "std_logic_vector"

        def __init__(self, size, default=None):
            if size > 1:
                self.size = size
            else:
                error_msg = "Parameter size of {0} must be > 1". \
                    format(self.__class__.__name__)
                raise TransformationError(error_msg)

            if default:
                temp_default = list(default)

                # check if every item in default is a valid std_logic value
                val_checked = all([ditm in self.std_logic_dvalues for ditm in temp_default])

                if val_checked is True:
                    if len(temp_default) == self.size:
                        self.default = "#" + "".join(temp_default) + "'"
                    elif len(temp_default) == 1:
                        self.default = "(others=>" + str(temp_default[0]) + ")"
                    else:
                        error_msg = "Length of default = {0}; " + \
                                    "should be {1} or {2}".format(len(temp_default), 1, self.size)
                        raise TransformationError(error_msg)
                else:
                    error_msg = "Values of default not in std_logic_dvalues"
                    raise TransformationError(error_msg)
            else:
                self.default = "(others=>0)"

        def __len__(self):
            return self.size

        def __repr__(self):
            return self.vhdl_type + "({} downto 0)".format(self.size - 1)

    class DummyType(_VhdlType):
        def __init__(self):
            pass
