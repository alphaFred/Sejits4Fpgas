"""Code generator for VHDL IR."""
import ast
import logging
#
from src.types import VhdlType
from nodes import Port, Generic, VhdlSignal
from utils import TransformationError
from utils import CONFIG


logger = logging.getLogger(__name__)
logger.disabled = CONFIG.getboolean("logging", "ENABLE_LOGGING")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


class VhdlCodegen(ast.NodeVisitor):

    ENTITY = """entity {entity_name} is\
                    \r{generic_declarations}\
                    \r{port_declarations}\
                \rend {entity_name};"""

    ENTITY_noG = """entity {entity_name} is\
                    \r{port_declarations}\
                \rend {entity_name};"""

    ARCHITECTURE = """architecture {architecture_name} of {entity_name} is\
                          \r{architecture_declarations}\
                      \rbegin\
                          \r{architecture_body}\
                      \rend {architecture_name};"""
    SIGNAL = "signal {name} : {type};"
    CONSTANT = "constant {name} : {type} := {value};"
    COMPONENT = """{instance_name} : entity {component_lib}\
                       \r{generic_map}\
                       \r{port_map}; """
    COMPONENT_noG = """{instance_name} : entity {component_lib}\
                       \r{port_map}; """

    def __init__(self, indent):
        from collections import defaultdict
        self.indent = indent
        self.src_code = ""
        self.architecture_body = ""
        self.symbols = ""
        self.used_symbols = set()
        self.component_ids = defaultdict(int)

    def _tab(self):
        """return correct spaces if tab found"""
        return " " * self.indent

    def visit_VhdlModule(self, node):
        self.src_code += self._generate_libs(node) + "\n\n"
        #
        port_src = self._port_block((node.in_port, node.out_port))
        self.src_code += self.ENTITY_noG.format(entity_name=node.name,
                                                port_declarations=port_src) + "\n\n"
        map(self.visit, node.architecture)
        #
        self.src_code += self.ARCHITECTURE.format(architecture_name="BEHAVE",
                                                  entity_name=node.name,
                                                  architecture_declarations=self.symbols.strip("\n"),
                                                  architecture_body=self.architecture_body)
        return self.src_code

    def visit_VhdlAssignment(self, node):
        self.architecture_body += "\n" + node.target.name + " <= " + node.source.name + ";"

    def visit_VhdlBinaryOp(self, node):
        temp_prev_component = [p for p in map(self.visit, node.prev) if p is not None]
        prev_component = []
        for i in temp_prev_component:
            if isinstance(i, list):
                prev_component.extend(i)
            else:
                prev_component.append(i)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        if node.generic:
            component = self.COMPONENT.format(instance_name=self._generate_name(node),
                                              component_lib=node.library,
                                              generic_map=generic_src,
                                              port_map=port_src) + "\n"
        else:
            component = self.COMPONENT_noG.format(instance_name=self._generate_name(node),
                                                  component_lib=node.library,
                                                  port_map=port_src) + "\n"
        self.architecture_body += "\n" + component
        #
        prev_component.append(component)
        return prev_component

    def visit_VhdlReturn(self, node):
        temp_prev_component = [p for p in map(self.visit, node.prev) if p is not None]
        prev_component = []
        for i in temp_prev_component:
            if isinstance(i, list):
                prev_component.extend(i)
            else:
                prev_component.append(i)
        component = ["-- RETURN"]
        for o, i in zip(node.out_port, node.in_port[2:]):
            component.append(str(o.value.name) + " <= " + str(i.value) + ";")
        #
        self.architecture_body += "\n" + "\n".join(component)
        prev_component.extend(component)
        return prev_component

    def visit_VhdlComponent(self, node):
        temp_prev_component = [p for p in map(self.visit, node.prev) if p is not None]
        prev_component = []
        for i in temp_prev_component:
            if isinstance(i, list):
                prev_component.extend(i)
            else:
                prev_component.append(i)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        if node.generic:
            component = self.COMPONENT.format(instance_name=self._generate_name(node),
                                              component_lib=node.library,
                                              generic_map=generic_src,
                                              port_map=port_src) + "\n"
        else:
            component = self.COMPONENT_noG.format(instance_name=self._generate_name(node),
                                                  component_lib=node.library,
                                                  port_map=port_src) + "\n"
        self.architecture_body += "\n" + component
        #
        prev_component.append(component)
        return prev_component

    def visit_VhdlDReg(self, node):
        temp_prev_component = [p for p in map(self.visit, node.prev) if p is not None]
        prev_component = []
        for i in temp_prev_component:
            if isinstance(i, list):
                prev_component.extend(i)
            else:
                prev_component.append(i)
        self.architecture_body += "\n"
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        if node.generic:
            component = self.COMPONENT.format(instance_name=self._generate_name(node),
                                              component_lib=node.library,
                                              generic_map=generic_src,
                                              port_map=port_src) + "\n"
        else:
            component = self.COMPONENT_noG.format(instance_name=self._generate_name(node),
                                                  component_lib=node.library,
                                                  port_map=port_src) + "\n"
        self.architecture_body += "\n" + component
        #
        prev_component.append(component)
        return prev_component

    def visit_VhdlFile(self, node):
        if node.body:
            return self.visit(node.body[0])
        else:
            return ""

    def _generic_map(self, generics):
        block_indent = " " * len("generic map(")
        #
        generic_map = [g.gmap() for g in generics]
        join_statement = ",\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "generic map("
        s += join_statement.join(generic_map)
        s += ")"
        #
        return s

    def _port_map(self, ports=([],[])):
        block_indent = " " * len("port map(")
        #
        port_map = []
        for p in ports[0]:
            frmt, lfunc = self.type_conversion(str(p.value.vhdl_type),
                                               str(p.vhdl_type))
            port_map.append(p.name + " => " + frmt.format(*lfunc(p.value, p)))
        #port_map.extend([p.name + " => " + str(p.value) for p in ports[0]])
        port_map.extend([p.name + " => " + str(p.value) for p in ports[1]])
        join_statement = ",\n" + self._tab() + block_indent
        #
        for port in ports[1]:
            # add support for collections
            if port.value.name not in self.used_symbols:
                self.symbols += self._tab() + self.SIGNAL.format(name=port.value.name,
                                                                 type=repr(port.value.vhdl_type)) + "\n"
                self.used_symbols.add(port.value.name)
        #
        s = "\n"
        s += self._tab() + "port map("
        s += join_statement.join(port_map)
        s += ")"
        #
        return s

    def _generic_block(self, generics):
        block_indent = " " * len("generic(")
        #
        generic_block = [g.name + " : " + self.visit(g.vhdl_type) for g in generics]
        join_statement = ";\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "generic("
        s += join_statement.join(generic_block)
        s += ");"
        return s

    def _port_block(self, ports=([],[])):
        block_indent = " " * len("port(")
        #
        port_block = []
        port_block.extend([p.name + " : " + p.direction + " " + repr(p.vhdl_type) for p in ports[0]])
        port_block.extend([p.name + " : " + p.direction + " " + repr(p.vhdl_type) for p in ports[1]])
        join_statement = ";\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "port("
        s += join_statement.join(port_block)
        s += ");"
        #
        return s

    def _generate_name(self, node):
        c_id = self.component_ids[node.__class__.__name__]
        self.component_ids[node.__class__.__name__] += 1
        if c_id != 0:
            return node.__class__.__name__ + "_" + str(c_id)
        else:
            return node.__class__.__name__

    def _generate_libs(self, node):
        src = ""
        for lib in node.libraries:
            src += "library " + lib.mainlib_name + ";\n" if lib.mainlib_name else ""
            for sublib in lib.sublib:
                src += "use " + sublib + ";\n"
        return src

    def type_conversion(self, source, sink):
        def check_equal_len(src, snk):
            if len(src.vhdl_type) == len(snk.vhdl_type):
                return str(src)
            else:
                error_msg = "Can not assign {0} of size {1} to {0} of size {2}".\
                            format(src.vhdl_type, len(src.vhdl_type), len(snk.vhdl_type))
                raise TransformationError(error_msg)

        type_conv = {"integer": {"integer":
                                 ("{}", lambda src, snk: (check_equal_len(src, snk),)),
                                 "signed":
                                 ("to_signed({0}, {1})",
                                     lambda src, snk: (str(src), len(snk.vhdl_type))),
                                 "unsigned":
                                 ("to_unsigned({0}, {1})",
                                     lambda src, snk: (str(src), len(snk.vhdl_type))),
                                 "std_logic_vector":
                                 ("std_logic_vector(to_signed({0}, {1}))",
                                     lambda src, snk: (str(src), len(snk.vhdl_type)))},
                     "signed": {"integer":
                                ("to_integer({})",
                                    lambda src, snk: (src,)),
                                "signed":
                                ("{}",
                                    lambda src, snk: (check_equal_len(src, snk),)),
                                "unsigned":
                                ("unsigned(std_logic_vector({}))",
                                    lambda src, snk: (src,)),
                                "std_logic_vector":
                                ("std_logic_vector({})",
                                    lambda src, snk: (src,))},
                     "unsigned": {"integer":
                                  ("to_integer({})",
                                      lambda src, snk: (src,)),
                                  "signed":
                                  ("signed(std_logic_vector({}))",
                                      lambda src, snk: (src,)),
                                  "unsigned":
                                  ("{}",
                                      lambda src, snk: (check_equal_len(src, snk),)),
                                  "std_logic_vector":
                                  ("std_logic_vector({})",
                                      lambda src, snk: (src,))},
                     "std_logic_vector": {"integer":
                                          ("to_integer(signed({}))",
                                              lambda src, snk: (src,)),
                                          "signed":
                                          ("signed({})",
                                              lambda src, snk: (src,)),
                                          "unsigned":
                                          ("unsigned({})",
                                              lambda src, snk: (src,)),
                                          "std_logic_vector":
                                          ("{}",
                                              lambda src, snk: (check_equal_len(src, snk),))},
                     "std_logic": {"std_logic": ("{}", lambda src, snk: (src,))},
                     "array": {"array": ("{}", lambda src, snk: (src,))}}
        try:
            frmt_string, lambda_func = type_conv[source][sink]
        except KeyError:
            error_msg = "Invalid conversion from {0} to {1}".format(source, sink)
            raise TransformationError(error_msg)
        return (frmt_string, lambda_func)
