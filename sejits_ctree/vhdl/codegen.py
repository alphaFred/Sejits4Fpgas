""" Code generator for VHDL constructs. """
__author__ = 'philipp ebensberger'


import ast

from nodes import VhdlType


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


class VhdlCodeGen(ast.NodeVisitor):

    active_entity = None
    active_arch = None

    def __init__(self, indent=4):
        self._indent = indent

    def _tab(self):
        """return correct spaces if tab found"""
        return " " * self._indent

    def visit_ProjectWrapper(self, node):
        return self.visit_VhdlFile(node)

    def visit_VhdlFile(self, node):
        """ Generate Vhdl description of VhdlFile. """
        libraries = "library " + ";\nuse ".join(node.libs) + ";"
        #
        self.active_entity = node.body[0]
        self.active_arch = node.body[1]
        #
        entity = self.visit(self.active_entity)
        architecture = self.visit(self.active_arch)
        return VHDLMODULE.format(libraries=libraries,
                                 entity=entity,
                                 architecture=architecture)

    def visit_Entity(self, node):
        """ Generate Vhdl description of entity."""
        # generate optional vhdl description of generics
        generics = ""
        if node.generics != ():
            generics = self._generic_block(node.generics)
        # generate vhdl description of ports
        ports = self._port_block(node.in_ports + node.out_ports)
        # return vhdl description of entity
        return ENTITY.format(entity_name=node.name,
                             generic_declarations=generics,
                             port_declarations=ports)

    def visit_Architecture(self, node):
        join_statement = "\n" + self._tab()
        #
        declarations = self._tab() +\
            join_statement.join([self.visit(sig) for sig in node.signals()])
        instructions = "\n".join([self.visit(comp) for comp in node.components()])
        #
        ret_port_name = [oport.name
                         for oport in self.active_entity.out_ports]
        ret_sig_name = [oport.value.name
                        for oport in self.active_entity.out_ports]
        #
        arch_return = ";\n".join([pname + " <= " + sname
                                 for pname, sname in
                                 zip(ret_port_name, ret_sig_name)])
        arch_return += ";\n"
        # return vhdl description of architecture
        return ARCHITECTURE.format(architecture_name=node.architecture_name,
                                   entity_name=node.entity_name,
                                   architecture_declarations=declarations,
                                   architecture_instructions=instructions,
                                   architecture_return=arch_return)

    def visit_Component(self, node):
        if node.generics != ():
            generic_map = self._generic_map(node.generics)
        else:
            generic_map = ""

        port_map = self._port_map(node.in_ports + node.out_ports)
        #
        return COMPONENT.format(instance_name=node.instance_name,
                                component_name=node.name,
                                component_lib=node.lib_name,
                                generic_map=generic_map,
                                port_map=port_map)

    def visit_BinaryOp(self, node):
        generic_map = self._generic_map([node.op])
        _in_ports = [self.type_cast(VhdlType.VhdlStdLogicVector, port)
                     for port in [node.left_port, node.right_port]]
        port_map = self._port_map(node.in_ports + (node.out_port,))
        #
        return COMPONENT.format(instance_name=node.instance_name,
                                component_name=node.name,
                                component_lib=node.lib_name,
                                generic_map=generic_map,
                                port_map=port_map)

    def type_cast(self, out_type, port):
        castable = (VhdlType.VhdlSigned,
                    VhdlType.VhdlUnsigned,
                    VhdlType.VhdlStdLogicVector)

        class cast(object):

            class obj_name(object):
                def __init__(self, out_type, name):
                    self.name = out_type.vhdl_type + "(" + name + ")"

            def __init__(self, out_type, port):
                self.name = port.name
                self.value = self.obj_name(out_type, port.value.name)
        #
        if type(port.value.vhdl_type) is out_type:
            return port
        else:
            if type(port.value.vhdl_type) in castable:
                return cast(out_type, port)

    def visit_UnaryOp(self, node):
        generic_map = self._generic_map([node.op])
        port_map = self._port_map(node.in_ports + [node.out_port])
        #
        return COMPONENT.format(instance_name=node.instance_name,
                                component_name=node.name,
                                component_lib=node.lib_name,
                                generic_map=generic_map,
                                port_map=port_map)

    def visit_Signal(self, node):
        """ Return signal description for architecture declaration. """
        return SIGNAL.format(signal_name=node.name,
                             signal_type=self.visit(node.vhdl_type))

    def visit_Constant(self, node):
        """ Return constant description for architecture declaration. """
        return CONSTANT.format(const_name=node.name,
                               const_type=self.visit(node.vhdl_type),
                               const_value=node.value)

    def visit_VhdlString(self, node):
        return node.vhdl_type

    def visit_VhdlArray(self, node):
        if node.generated:
            raise Exception("Generated arrays currently unsupported")
        else:
            return node.type_def

    def visit_VhdlUnsigned(self, node):
        return node.vhdl_type

    def visit_VhdlSigned(self, node):
        return node.vhdl_type

    def visit_VhdlStdLogicVector(self, node):
        if node.default:
            if len(node.default) == 1:
                return node.vhdl_type + " := (others => " + "'" + node.default[0] + "'" + ")"
            else:
                return node.vhdl_type + ' := "' + "".join(node.default) + '"'
        else:
            return node.vhdl_type

    # ======================================================================= #
    # HELPER METHODS FOR ENTITY
    # ======================================================================= #
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

    def _port_block(self, ports):
        block_indent = " " * len("port(")
        #
        port_block = [p.name + " : " + p.direction + " " + str(p.value.vhdl_type) for p in ports]
        join_statement = ";\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "port("
        s += join_statement.join(port_block)
        s += ");"
        #
        return s

    # ======================================================================= #
    # HELPER METHODS FOR COMPONENTS
    # ======================================================================= #

    def _generic_map(self, generics):
        block_indent = " " * len("generic map(")
        #
        generic_map = [g.name + " => " + str(g.value) for g in generics]
        join_statement = ",\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "generic map("
        s += join_statement.join(generic_map)
        s += ")"
        #
        return s

    def _port_map(self, ports):
        block_indent = " " * len("port map(")
        #
        port_map = [p.name + " => " + p.value.name for p in ports]
        join_statement = ",\n" + self._tab() + block_indent
        #
        s = "\n"
        s += self._tab() + "port map("
        s += join_statement.join(port_map)
        s += ")"
        #
        return s
