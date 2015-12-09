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
    signals = set()

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
        generic = ""
        port = ""
        #
        if node.params:
            if type(node.params) is list:
                port += "\tport(\n"
                port += "\t\t" + ",\n\t\t".join([param.name
                                                 for param in node.params])
                port += "\n\t);"
        #
        self.active_module["entity_name"] = node.name
        #
        s = "entity {0} is\n{1}\n{2}\nend {0};".format(node.name,
                                                       generic,
                                                       port)
        return s

    def visit_Architecture(self, node):
        arch_name = "Behavioural"
        entity_name = self.active_module["entity_name"]
        arch_decl = ""
        arch_instr = "\n\t\t".join([str(self.visit(body)) for body in node.body])
        s = "architecture {0} of {1} is\n{2}\nbegin\n{3}\nend {0};"\
            .format(arch_name,
                    entity_name,
                    arch_decl,
                    arch_instr)
        return s

    def visit_BinaryOp(self, node):
        comp_count = self.module_comp_count[node.__class__.__name__]
        #
        left = "left : " + self.route_signal(node.left, node)
        op = "op : " + str(node.op)
        right = "right : " + self.route_signal(node.right, node)
        #
        ports = "\n\t\t".join([left, op, right])
        # \n\t\t".join([self.visit(node.left), self.visit(node.right)])
        s = "{0}_{1}: {0}\n\tport map(\n\t\t{2}\t);"\
            .format(node.__class__.__name__,
                    comp_count,
                    ports)
        #
        sigs = [self.resolve_sig(node, getattr(node, sig))
                for sig in node._fields]
        #
        s = self._make_comp_block(node.__class__.__name__,
                                  None,
                                  [node._fields, sigs],
                                  "    ")
        # update component count
        self.module_comp_count[node.__class__.__name__] += 1
        #
        return s + self.visit(node.left) + self.visit(node.right)

    def visit_ComponentCall(self, node):
        comp_count = self.module_comp_count[node.comp.name]
        #
        sigs = [self.resolve_sig(node, sig) for sig in node.args]
        #
        s = self._make_comp_block(node.comp.name,
                                  None,
                                  [node.args, sigs],
                                  "    ")
        # update component count
        self.module_comp_count[node.comp.name] += 1
        return s

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
        return s

    def _make_map(self, ports, sigs, indent):
        wrap = ",\n" + indent
        s = wrap.join([str(port) + " => " + sig for port, sig in zip(ports, sigs)])
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

