""" Code generator for VHDL constructs. """
__author__ = 'philipp ebensberger'


import ast
import logging
from nodes import VhdlType

from sejits_ctree.vhdl import TransformationError
from sejits_ctree.vhdl.utils import CONFIG
from sejits_ctree.vhdl.nodes import Port, Generic, VhdlSignal


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
    SIGNAL = "signal {name} : {type} := {default};"
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
        self._generate_ports(node)
        #
        port_src = self._port_block((node.in_port, node.out_port))
        self.src_code += self.ENTITY_noG.format(entity_name=node.name,
                                                port_declarations=port_src) + "\n\n"
        self.visit(node.architecture)
        self.src_code += self.ARCHITECTURE.format(architecture_name="BEHAVE",
                                                  entity_name=node.name,
                                                  architecture_declarations=self.symbols.strip("\n"),
                                                  architecture_body=self.architecture_body)
        return self.src_code

    def visit_VhdlBinaryOp(self, node):
        map(self.visit, node.prev)
        #
        self._generate_ports(node)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        if node.generic:
            self.architecture_body += self.COMPONENT.format(instance_name=self._generate_name(node),
                                                            component_lib=node.library,
                                                            generic_map=generic_src,
                                                            port_map=port_src) + "\n"
        else:
            self.architecture_body += self.COMPONENT_noG.format(instance_name=self._generate_name(node),
                                                                component_lib=node.library,
                                                                port_map=port_src) + "\n"

    def visit_VhdlReturn(self, node):
        map(self.visit, node.prev)
        self.architecture_body += node.out_port[0].name + " <= " + node.in_port[0].name

    def visit_VhdlComponent(self, node):
        map(self.visit, node.prev)
        #
        self._generate_ports(node)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        if node.generic:
            self.architecture_body += self.COMPONENT.format(instance_name=self._generate_name(node),
                                                            component_lib=node.library,
                                                            generic_map=generic_src,
                                                            port_map=port_src) + "\n"
        else:
            self.architecture_body += self.COMPONENT_noG.format(instance_name=self._generate_name(node),
                                                                component_lib=node.library,
                                                                port_map=port_src) + "\n"

    def visit_VhdlDReg(self, node):
        map(self.visit, node.prev)
        #
        self._generate_ports(node)
        #
        generic_src = self._generic_map(node.generic)
        port_src = self._port_map((node.in_port, node.out_port))
        if node.generic:
            self.architecture_body += self.COMPONENT.format(instance_name=self._generate_name(node),
                                                            component_lib=node.library,
                                                            generic_map=generic_src,
                                                            port_map=port_src) + "\n"
        else:
            self.architecture_body += self.COMPONENT_noG.format(instance_name=self._generate_name(node),
                                                                component_lib=node.library,
                                                                port_map=port_src) + "\n"

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
        port_map.extend([p.name + " => " + p.value.name for p in ports[0]])
        port_map.extend([p.name + " => " + p.value.name for p in ports[1]])
        join_statement = ",\n" + self._tab() + block_indent
        #
        for port in ports[1]:
            if port.value.name not in self.used_symbols:
                self.symbols += self._tab() + self.SIGNAL.format(name=port.value.name,
                                                                 type=port.value.vhdl_type,
                                                                 default=port.value.vhdl_type.default) + "\n"
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
        port_block.extend([p.name + " : " + p.direction + " " + str(p.value.vhdl_type) for p in ports[0]])
        port_block.extend([p.name + " : " + p.direction + " " + str(p.value.vhdl_type) for p in ports[1]])
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
            node.finalize_ports()
            #
            inport_info = node.inport_info
            in_port = node.in_port
            #
            outport_info = node.outport_info
            out_port = node.out_port
            #
            generic_info = node.generic_info
            generic_port = node.generic
        except AttributeError as ae:
            raise TransformationError(ae.message)

        if all([type(port) is Port for port in in_port]):
            # continue if node already has ports
            pass
        else:
            if len(inport_info) != len(in_port):
                error_msg = "Number of in ports does not match inport" +\
                    " information of node %s" % node.name
                raise TransformationError(error_msg)

            cmd_info = [("CLK", "in", VhdlType.VhdlStdLogic()),
                        ("EN", "in", VhdlType.VhdlStdLogic()),
                        ("RST", "in", VhdlType.VhdlStdLogic())]
            cmd_symb = [VhdlSignal("CLK", VhdlType.VhdlStdLogic()),
                        VhdlSignal("EN", VhdlType.VhdlStdLogic()),
                        VhdlSignal("RST", VhdlType.VhdlStdLogic())]
            cmd_port = [Port(info[0], info[1], info[2], port) for info,port in zip(cmd_info, cmd_symb)]
            node.in_port = cmd_port + [Port(info[0], info[1], None, port) for info,port in zip(inport_info, in_port)]

        if all([type(port) is Port for port in out_port]):
            # continue if node already has ports
            pass
        else:
            if len(outport_info) != len(out_port):
                raise TransformationError("Number of out ports does not match outport information of node %s" % node.name)

            node.out_port = [Port(info[0], info[1], None, port) for info,port in zip(outport_info, out_port)]

        if all([type(port) is Generic for port in generic_port]):
            # continue if node already has generics
            pass
        else:
            if len(generic_info) != len(generic_port):
                raise TransformationError("Number of generic ports does not match generic information of node %s" % node.name)

            node.generic = [Generic(info[0], info[1], port) for info,port in zip(generic_info, generic_port)]

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


def type_conversion(source, sink):
    type_conv = {"integer": {"integer":
                             ("{}", lambda src, snk: (src.name)),
                             "signed":
                             ("to_signed({0}, {1}'length)",
                                 lambda src, snk: (src.name, snk.name)),
                             "unsigned":
                             ("to_unsigned({0}, {1}'length)",
                                 lambda src, snk: (src.name, snk.name)),
                             "std_logic_vector":
                             ("std_logic_vector(to_signed({0}, {1}'length))",
                                 lambda src, snk: (src.name, snk.name))},
                 "signed": {"integer":
                            ("to_integer({})",
                                lambda src, snk: (src.name)),
                            "signed":
                            ("{}",
                                lambda src, snk: (src.name)),
                            "unsigned":
                            ("unsigned(std_logic_vector({}))",
                                lambda src, snk: (src.name)),
                            "std_logic_vector":
                            ("std_logic_vector({})",
                                lambda src, snk: (src.name))},
                 "unsigned": {"integer":
                              ("to_integer({})",
                                  lambda src, snk: (src.name)),
                              "signed":
                              ("{}",
                                  lambda src, snk: (src.name)),
                              "unsigned":
                              ("unsigned(std_logic_vector({}))",
                                  lambda src, snk: (src.name)),
                              "std_logic_vector":
                              ("std_logic_vector({})",
                                  lambda src, snk: (src.name))},
                 "std_logic_vector": {"integer":
                                      ("to_integer(signed({}))",
                                          lambda src, snk: (src.name)),
                                      "signed":
                                      ("signed({})",
                                          lambda src, snk: (src.name)),
                                      "unsigned":
                                      ("unsigned({})",
                                          lambda src, snk: (src.name)),
                                      "std_logic_vector":
                                      ("{}",
                                          lambda src, snk: (src.name))}}
    frmt_string, lambda_func = type_conv[source][sink]
    return frmt_string.format(*lambda_func(source, sink))
