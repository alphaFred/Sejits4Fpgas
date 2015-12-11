""" Code generator for VHDL constructs. """
__author__ = 'philipp ebensberger'

from sejits_ctree.codegen import CodeGenVisitor
from sejits_ctree.vhdl.nodes import SymbolRef
from sejits_ctree.nodes import CommonCodeGen
from collections import defaultdict


class VhdlCodeGen(CommonCodeGen):

    """ docstring dummy. """

    active_module = {"entity_name": ""}
    module_comp_count = defaultdict(int)
    #
    comp_port_names = {"BinOp": ["left", "op", "right"],
                       "sobel": ["image", "ret"],
                       "sobel_v": ["image", "mask"],
                       "sobel_h": ["image", "mask"],
                       "sqrt": ["in1", "out1"],
                       "assert_nD": ["array", "ndim"]}
    #
    signals = set()
    indent = "    "

    def run(self, node):
        ret = self.visit(node)
        return ret

    def visit_VhdlFile(self, node):
        s = ""
        # add libs
        for lib in node.libs:
            s += lib + ";\n"
        s += "\n"
        # add entity
        s += self.visit(node.body[0]) + "\n\n"
        # add architecture
        s += self.visit(node.body[1]) + "\n"
        # return module source code
        return s

    def visit_EntityDecl(self, node):
        s = self._make_entity_block(ent_type=node.name,
                                    ent_generics=None,
                                    ent_ports=[node.in_args, node.out_arg],
                                    indent=self.indent)
        self.active_module["entity_name"] = node.name
        return s

    def visit_Architecture(self, node):
        arch_name = "Behavioural"
        entity_name = self.active_module["entity_name"]
        arch_decl = ""
        arch_instr = "\n".join([str(self.visit(body)) for body in node.body])
        s = "architecture {0} of {1} is\n{2}\nbegin{3}end {0};"\
            .format(arch_name,
                    entity_name,
                    arch_decl,
                    arch_instr)
        return s

    def visit_ComponentCall(self, node):
        if node.comp in self.comp_port_names:
            iargs = node.in_args if type(node.in_args) is list\
                else [node.in_args]
            iargs = [str(iarg) for iarg in iargs]
            #
            oargs = node.out_args if type(node.out_args) is list\
                else [node.out_args]
            oargs = [str(oarg) for oarg in oargs]
            sigs = iargs + oargs
            #
            s = self._make_comp_block(node.comp,
                                      None,
                                      [self.comp_port_names[node.comp], sigs],
                                      self.indent)
            #
            return s
        else:
            return ""

    def _make_comp_block(self, comp_type, comp_generics, comp_ports, indent):
        comp_count = self.module_comp_count[comp_type]
        s = "{0}_{1} : {0}\n"
        # add generics map if available
        s += "generic map({2})\n\n" if comp_generics else ""
        # add port map if available
        if comp_generics:
            s += indent + "port map({3});\n\n" if comp_ports else ""
        else:
            s += indent + "port map({2});\n\n" if comp_ports else ""
        #
        maps = filter(None, [comp_generics, comp_ports])
        maps = [self._make_map(*item, indent=indent * 2) for item in maps]
        s = s.format(comp_type, comp_count, *maps)
        #
        self.module_comp_count[comp_type] += 1
        return s

    def _make_entity_block(self, ent_type, ent_generics, ent_ports, indent):
        s = "entity {0} is\n"
        s += "generic ({2})\n\n" if ent_generics else ""
        # add port map if available
        if ent_generics:
            s += indent + "port (\n{3}end {0};\n\n" if ent_ports else ""
        else:
            s += indent + "port (\n{2}end {0};\n\n" if ent_ports else ""
        #
        maps = [None,
                self._make_entitiy_io(ent_ports[0],
                                      ent_ports[1],
                                      indent + self.indent)]
        s = s.format(ent_type, *maps)
        #
        return s

    def _make_map(self, ports, sigs, indent):
        wrap = ",\n" + indent
        s = wrap.join([str(port) + " => " + sig
                       for port, sig in zip(ports, sigs)])
        return s

    def _make_entitiy_io(self, iports, oports, indent):
        iports = iports if type(iports) is list else [iports]
        oports = oports if type(oports) is list else [oports]
        #
        wrap = ";\n" + indent
        s = indent
        s += wrap.join([iport.name + " : in " + str(iport.type)
                       for iport in iports])
        s += ";\n" + indent
        s += wrap.join([oport.name + " : out " + str(oport.type)
                        for oport in oports])
        s += ");\n"
        return s

    def resolve_sig(self, node, prev_node):
        if type(prev_node) is SymbolRef:
            if prev_node._local:
                return str(prev_node)
            elif prev_node._global:
                return "GLOBAL"
            else:
                return "SIG-RESOLUTION-ERROR"
        else:
            return"DUMMY"

    def visit_Return(self, node):
        return self.visit(node.value)

    def route_signal(self, source, sink):
        # create unique signal name
        sig_name = "sig_" + str(hash(source)) + "_" +\
            source.__class__.__name__ + "__" + str(hash(sink)) +\
            "_" + sink.__class__.__name__
        # cache signal name
        self.signals.add(sig_name)
        return sig_name


class Dummy(object):
    def visit_Architecture(self, node):
        s = ""
        #
        s += "architecture %s of %s is\n" % ("Behavioural",
                                             self.active_module["entity_name"])
        # architecture declarations
        s += "\t-- components\n"
        for decl in node.components:
            s += "\tcomponent " + decl.comp.name + " is\n"
            s += "\t\tport(\n"
            for port in decl.comp.entity.params:
                s += "\t\t\t%s : %s %s;\n" % (port.name, "in", "std_logic")
            s += "\tend component;\n"
        s += "\t-- signals\n"
        s += "begin\n"
        s += "end %s;\n" % "Behavioural"
        return s

    def visit_EntityDecl(self, node):
        self.active_module["entity_name"] = node.name
        #
        s = ""
        # add entity name
        s += "entity %s is\n" % node.name
        # add ports
        ports = node.params if type(node.params) is list else list(node.params)
        s += "\tport(\n"
        for port in ports:
            s += "\t\t%s : %s %s;\n" %(port.name, "in", "std_logic")
        #
        s += "\t);\n"
        #
        s += "end entity %s;\n" % node.name
        #
        if type(node.arch) is list:
            arch = "\n".join(map(self.visit, node.arch))
        else:
            arch = "\n" + str(self.visit(node.arch))
        #
        print s + arch + "\n"
        return s + arch

