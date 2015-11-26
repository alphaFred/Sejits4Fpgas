""" Provide code generation class and helper functions. """
__author__ = 'philipp ebensberger'

import ast


class FpgaCodeGen(ast.NodeVisitor):

    """ Generate VHDL code from DAG. """

    def __init__(self):
        """ Initialize code generator. """
        self.glob_isig = set()
        self.glob_osig = set()
        self.signals = set()
        self.visited_nodes = set()
        self.components = ""
        self.tabwidth = 4  # 4 spaces per tab

    def run(self, dag):
        """ Start code generation. """
        self.visit(dag)
        print "Signals:"
        for sig in self.signals:
            print "\t signal", sig,\
                " : std_logic_vector(31 downto 0) := (others => '0');"
        print self.components

    def pprint(self):
        pass

    def generic_visit(self, node):
        """
        Generate signals and component for node.

        Only if node is visited for the first time:
            - get all signals from next node.
            - create all signals to next node.
            - create component and connect signals.
        """
        gen_sic = ""  # generic signals/parameters
        if hash(node) not in self.visited_nodes:
            if node.next != []:
                out_sigs = "osig_" + str(hash(node))
                self.signals.add(out_sigs)
                out_sigs = str(" " * self.tabwidth * 2) +\
                    "OUT => " + out_sigs + ";"
            else:
                out_sigs = ""
            # visit previous nodes
            map(self.visit, node.prev)
            # connect previous nodes
            if node.prev != []:
                in_sigs = ""
                for idx, sig in enumerate(node.prev):
                    in_sigs += str(" " * self.tabwidth * 2) +\
                        "IN" + str(idx) + " => " + "osig_" + str(hash(sig)) +\
                        ";\n"
            else:
                in_sigs = ""
            # create component
            comp = '''
COMPONENT {}
    Generic (
{}
    );
    Port (
{}
{}
    );
END COMPONENT;
            '''.format(type(node).__name__ + str(hash(node)),
                       gen_sic,
                       in_sigs,
                       out_sigs)
            #
            self.components += comp
            # add node to set of visited nodes
            self.visited_nodes.add(hash(node))
        else:
            pass

    def visit_DagNodeInput(self, node):
        """
        Generate signals and component for input node.

        Only if node is visited for the first time:
            - create all signals to next node.
            - get all signals from next node.
            - create component and connect signals.
        """
        gen_sic = ""  # generic signals/parameters
        if hash(node) not in self.visited_nodes:
            if node.next != []:
                out_sigs = "osig_" + str(hash(node))
                self.signals.add(out_sigs)
                out_sigs = str(" " * self.tabwidth * 2) +\
                    "OUT => " + out_sigs + ";"
            else:
                out_sigs = ""
            # visit previous nodes
            map(self.visit, node.prev)
            # connect previous nodes
            image_sig = "isig_image_" + str(hash(node))
            in_sigs = str(" " * self.tabwidth * 2) +\
                "IN_Image => " + image_sig + ";"
            self.glob_isig.add(in_sigs)
            # create component
            comp = '''
COMPONENT {}
    Generic (
{}
    );
    Port (
{}
{}
    );
END COMPONENT;
            '''.format(type(node).__name__ + str(hash(node)),
                       gen_sic,
                       in_sigs,
                       out_sigs)
            #
            self.components += comp
            # add node to set of visited nodes
            self.visited_nodes.add(hash(node))
        else:
            pass


"""
entity dsp_32x32Mul_block is
    Port (
        A    : in STD_LOGIC_VECTOR (31 downto 0);
        B    : in STD_LOGIC_VECTOR (31 downto 0);
        CLK  : in STD_LOGIC;
        CE   : in STD_LOGIC;
        RST  : in STD_LOGIC;
        P    : out STD_LOGIC_VECTOR (63 downto 0)
    );
end dsp_32x32Mul_block;
"""