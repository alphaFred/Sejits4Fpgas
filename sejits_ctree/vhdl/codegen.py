""" Code generator for VHDL constructs. """
__author__ = 'philipp ebensberger'


import ast
import logging
from nodes import VhdlType

from sejits_ctree.vhdl.utils import CONFIG


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


VHDLMODULE = """{libraries}\n\n
{entity}\n
{architecture}"""

ARCHITECTURE = """architecture {architecture_name} of {entity_name} is
{architecture_declarations}
begin
{architecture_instructions}
{architecture_return}
end {architecture_name};"""

ENTITY = """entity {entity_name} is\
{generic_declarations}\
{port_declarations}
end {entity_name};"""

SIGNAL = "signal {signal_name} : {signal_type};"

CONSTANT = "constant {const_name} : {const_type} := {const_value};"

COMPONENT = """{instance_name} : entity {component_lib}\
{generic_map}\
{port_map};
"""

class VhdlCodegen(ast.NodeVisitor):

    ENTITY = """entity {entity_name} is\
                    \r{generic_declarations}\
                    \r{port_declarations}\
                \rend {entity_name};"""
    ARCHITECTURE = """architecture {architecture_name} of {entity_name} is\
                          \r{architecture_declarations}\
                      \rbegin\
                          \r{architecture_body}\
                      \rend {architecture_name};"""
    SIGNAL = "signal {name} : {type} := {default};"
    CONSTANT = "constant {name} : {type} := {value};"
    COMPONENT = """{instance_name} : entity {component_lib}\
                       \r{generic_map}\
                       \r{port_map}; """

    def __init__(self):
        from collections import defaultdict
        self.src_code = ""
        self.architecture_body = ""
        self.symbols = ""
        self.used_symols = set()
        self.component_ids = defaultdict(int)

    def _tab(self):
        """return correct spaces if tab found"""
        return " " * 4

    def visit_VhdlModule(self, node):
        port_src = self._port_block((node.entity,[]))
        self.src_code += self.ENTITY.format(entity_name=node.name,
                                            generic_declarations="",
                                            port_declarations=port_src) + "\n"
        self.visit(node.architecture)
        self.src_code += self.ARCHITECTURE.format(architecture_name="BEHAVE",
                                                  entity_name=node.name,
                                                  architecture_declarations=self.symbols,
                                                  architecture_body=self.architecture_body)
        return self.src_code

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        #
        self._generate_ports(node)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        self.architecture_body += self.COMPONENT.format(instance_name=self._generate_name(node),
                                                        component_lib="work.BasicArith",
                                                        generic_map=generic_src,
                                                        port_map=port_src) + "\n"

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.architecture_body += node.out_port[0].name + " <= " + node.in_port[0].name
        pass

    def visit_VhdlComponent(self, node):
        map(self.visit, node.prev)
        #
        self._generate_ports(node)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        self.architecture_body += self.COMPONENT.format(instance_name=self._generate_name(node),
                                                        component_lib="work.BasicArith",
                                                        generic_map=generic_src,
                                                        port_map=port_src) + "\n"

    def _generic_map(self, generics):
        block_indent = " " * len("generic map(")
        #
        generic_map = ["GENERIC" + " => " + str(g) for g in generics]
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
        port_map.extend([p.name + " => " + p.value.name for p in ports[0]])
        port_map.extend([p.name + " => " + p.value.name for p in ports[1]])
        join_statement = ",\n" + self._tab() + block_indent
        #
        for port in ports[1]:
            self.symbols += self._tab() + self.SIGNAL.format(name=port.value.name,
                                               type=port.value.vhdl_type,
                                               default=port.value.vhdl_type.default) + "\n"
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
        port_block.extend([p.name + " : " + "in" + " " + str(p.vhdl_type) for p in ports[0]])
        port_block.extend([p.name + " : " + "out" + " " + str(p.vhdl_type) for p in ports[1]])
        join_statement = ";\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "port("
        s += join_statement.join(port_block)
        s += ");"
        #
        return s

    def _generate_ports(self, node):
        # TODO add exception handling
        try:
            inport_info = node.inport_info
            in_port = node.in_port
            #
            outport_info = node.outport_info
            out_port = node.out_port
        except:
            raise TransformationError("msg0")

        if all([type(port) is Port for port in in_port]):
            # continue if node already has ports
            pass
        else:
            if len(inport_info) != len(in_port):
                raise TransformationError("msg1")

            cmd_info = [("CLK", "in"), ("EN", "in"), ("RST", "in")]
            cmd_symb = [VhdlSignal("CLK", VhdlType.VhdlStdLogic()),
                        VhdlSignal("EN", VhdlType.VhdlStdLogic()),
                        VhdlSignal("RST", VhdlType.VhdlStdLogic())]
            cmd_port = [Port(info[0], info[1], port) for info,port in zip(cmd_info, cmd_symb)]
            node.in_port = cmd_port + [Port(info[0], info[1], port) for info,port in zip(inport_info, in_port)]

        if all([type(port) is Port for port in out_port]):
            # continue if node already has ports
            pass
        else:
            if len(outport_info) != len(out_port):
                raise TransformationError("msg2")

            node.out_port = [Port(info[0], info[1], port) for info,port in zip(outport_info, out_port)]

    def _generate_name(self, node):
        c_id = self.component_ids[node.__class__.__name__]
        self.component_ids[node.__class__.__name__] += 1
        if c_id != 0:
            return node.__class__.__name__ + "_" + str(c_id)
        else:
            return node.__class__.__name__