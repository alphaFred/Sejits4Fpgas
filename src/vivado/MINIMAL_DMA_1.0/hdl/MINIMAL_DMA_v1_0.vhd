library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


library xil_defaultlib;
use xil_defaultlib.MINIMAL_DMA_v1_0_M_AXI;

entity MINIMAL_DMA_v1_0 is
    generic (
        -- Users to add parameters here
                LEN_WIDTH : integer := 16;
                ISSUE_DEPTH : integer := 2;
        -- User parameters ends
        -- Do not modify the parameters beyond this line


        -- Parameters of Axi Master Bus Interface M_AXI
                C_M_AXI_BURST_LEN	: integer	:= 16;
                C_M_AXI_ID_WIDTH	: integer	:= 1;
                C_M_AXI_ADDR_WIDTH	: integer	:= 32;
                C_M_AXI_DATA_WIDTH	: integer	:= 32;
                C_M_AXI_AWUSER_WIDTH	: integer	:= 0;
                C_M_AXI_ARUSER_WIDTH	: integer	:= 0;
                C_M_AXI_WUSER_WIDTH	: integer	:= 0;
                C_M_AXI_RUSER_WIDTH	: integer	:= 0;
                C_M_AXI_BUSER_WIDTH	: integer	:= 0
            );
    port (
        -- Users to add ports here

        -- User ports ends
        -- Do not modify the ports beyond this line
             out_data : out std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
             out_valid : out std_logic;
             out_last : out std_logic;
             out_ready : in std_logic := '0';

             in_data : in std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0) := (others => '0');
             in_valid : in std_logic := '0';
             in_last : in std_logic := '0';
             in_ready : out std_logic;

             r_addr	: in std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0) := (others => '0');
             r_len	: in std_logic_vector(LEN_WIDTH-1 downto 0) := (others => '0');
             r_valid : in std_logic := '0';
             r_ready : out std_logic;
             r_compl : out std_logic;

             w_addr	: in std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0) := (others => '0');
             w_len	: in std_logic_vector(LEN_WIDTH-1 downto 0) := (others => '0');
             w_valid : in std_logic := '0';
             w_ready : out std_logic;
             w_compl : out std_logic;

             rst : in std_logic;


        -- Ports of Axi Master Bus Interface M_AXI

             m_axi_aclk	: in std_logic;
             m_axi_aresetn	: in std_logic;
             m_axi_awid	: out std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
             m_axi_awaddr	: out std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
             m_axi_awlen	: out std_logic_vector(7 downto 0);
             m_axi_awsize	: out std_logic_vector(2 downto 0);
             m_axi_awburst	: out std_logic_vector(1 downto 0);
             m_axi_awlock	: out std_logic;
             m_axi_awcache	: out std_logic_vector(3 downto 0);
             m_axi_awprot	: out std_logic_vector(2 downto 0);
             m_axi_awqos	: out std_logic_vector(3 downto 0);
             m_axi_awuser	: out std_logic_vector(C_M_AXI_AWUSER_WIDTH-1 downto 0);
             m_axi_awvalid	: out std_logic;
             m_axi_awready	: in std_logic;
             m_axi_wdata	: out std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
             m_axi_wstrb	: out std_logic_vector(C_M_AXI_DATA_WIDTH/8-1 downto 0);
             m_axi_wlast	: out std_logic;
             m_axi_wuser	: out std_logic_vector(C_M_AXI_WUSER_WIDTH-1 downto 0);
             m_axi_wvalid	: out std_logic;
             m_axi_wready	: in std_logic;
             m_axi_bid	: in std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
             m_axi_bresp	: in std_logic_vector(1 downto 0);
             m_axi_buser	: in std_logic_vector(C_M_AXI_BUSER_WIDTH-1 downto 0) := (others => '0');
             m_axi_bvalid	: in std_logic;
             m_axi_bready	: out std_logic;
             m_axi_arid	: out std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
             m_axi_araddr	: out std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
             m_axi_arlen	: out std_logic_vector(7 downto 0);
             m_axi_arsize	: out std_logic_vector(2 downto 0);
             m_axi_arburst	: out std_logic_vector(1 downto 0);
             m_axi_arlock	: out std_logic;
             m_axi_arcache	: out std_logic_vector(3 downto 0);
             m_axi_arprot	: out std_logic_vector(2 downto 0);
             m_axi_arqos	: out std_logic_vector(3 downto 0);
             m_axi_aruser	: out std_logic_vector(C_M_AXI_ARUSER_WIDTH-1 downto 0);
             m_axi_arvalid	: out std_logic;
             m_axi_arready	: in std_logic;
             m_axi_rid	: in std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
             m_axi_rdata	: in std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
             m_axi_rresp	: in std_logic_vector(1 downto 0);
             m_axi_rlast	: in std_logic;
             m_axi_ruser	: in std_logic_vector(C_M_AXI_RUSER_WIDTH-1 downto 0);
             m_axi_rvalid	: in std_logic;
             m_axi_rready	: out std_logic
         );
end MINIMAL_DMA_v1_0;

architecture arch_imp of MINIMAL_DMA_v1_0 is



begin

-- Instantiation of Axi Bus Interface M_AXI
    MINIMAL_DMA_v1_0_M_AXI_inst : entity xil_defaultlib.MINIMAL_DMA_v1_0_M_AXI
    generic map (
                    LEN_WIDTH => LEN_WIDTH,
                    ISSUE_DEPTH => ISSUE_DEPTH,
                    C_M_AXI_BURST_LEN	=> C_M_AXI_BURST_LEN,
                    C_M_AXI_ID_WIDTH	=> C_M_AXI_ID_WIDTH,
                    C_M_AXI_ADDR_WIDTH	=> C_M_AXI_ADDR_WIDTH,
                    C_M_AXI_DATA_WIDTH	=> C_M_AXI_DATA_WIDTH,
                    C_M_AXI_AWUSER_WIDTH	=> C_M_AXI_AWUSER_WIDTH,
                    C_M_AXI_ARUSER_WIDTH	=> C_M_AXI_ARUSER_WIDTH,
                    C_M_AXI_WUSER_WIDTH	=> C_M_AXI_WUSER_WIDTH,
                    C_M_AXI_RUSER_WIDTH	=> C_M_AXI_RUSER_WIDTH,
                    C_M_AXI_BUSER_WIDTH	=> C_M_AXI_BUSER_WIDTH
                )
    port map (
                 out_data => out_data,
                 out_valid => out_valid,
                 out_last => out_last,
                 out_ready => out_ready,

                 in_data => in_data,
                 in_valid => in_valid,
                 in_last => in_last,
                 in_ready => in_ready,

                 r_addr => r_addr,
                 r_len => r_len,
                 r_valid => r_valid,
                 r_ready => r_ready,
                 r_compl => r_compl,

                 w_addr => w_addr,
                 w_len => w_len,
                 w_valid => w_valid,
                 w_ready => w_ready,
                 w_compl => w_compl,

                 rst => rst,

                 M_AXI_ACLK	=> m_axi_aclk,
                 M_AXI_ARESETN	=> m_axi_aresetn,
                 M_AXI_AWID	=> m_axi_awid,
                 M_AXI_AWADDR	=> m_axi_awaddr,
                 M_AXI_AWLEN	=> m_axi_awlen,
                 M_AXI_AWSIZE	=> m_axi_awsize,
                 M_AXI_AWBURST	=> m_axi_awburst,
                 M_AXI_AWLOCK	=> m_axi_awlock,
                 M_AXI_AWCACHE	=> m_axi_awcache,
                 M_AXI_AWPROT	=> m_axi_awprot,
                 M_AXI_AWQOS	=> m_axi_awqos,
                 M_AXI_AWUSER	=> m_axi_awuser,
                 M_AXI_AWVALID	=> m_axi_awvalid,
                 M_AXI_AWREADY	=> m_axi_awready,
                 M_AXI_WDATA	=> m_axi_wdata,
                 M_AXI_WSTRB	=> m_axi_wstrb,
                 M_AXI_WLAST	=> m_axi_wlast,
                 M_AXI_WUSER	=> m_axi_wuser,
                 M_AXI_WVALID	=> m_axi_wvalid,
                 M_AXI_WREADY	=> m_axi_wready,
                 M_AXI_BID	=> m_axi_bid,
                 M_AXI_BRESP	=> m_axi_bresp,
                 M_AXI_BUSER	=> m_axi_buser,
                 M_AXI_BVALID	=> m_axi_bvalid,
                 M_AXI_BREADY	=> m_axi_bready,
                 M_AXI_ARID	=> m_axi_arid,
                 M_AXI_ARADDR	=> m_axi_araddr,
                 M_AXI_ARLEN	=> m_axi_arlen,
                 M_AXI_ARSIZE	=> m_axi_arsize,
                 M_AXI_ARBURST	=> m_axi_arburst,
                 M_AXI_ARLOCK	=> m_axi_arlock,
                 M_AXI_ARCACHE	=> m_axi_arcache,
                 M_AXI_ARPROT	=> m_axi_arprot,
                 M_AXI_ARQOS	=> m_axi_arqos,
                 M_AXI_ARUSER	=> m_axi_aruser,
                 M_AXI_ARVALID	=> m_axi_arvalid,
                 M_AXI_ARREADY	=> m_axi_arready,
                 M_AXI_RID	=> m_axi_rid,
                 M_AXI_RDATA	=> m_axi_rdata,
                 M_AXI_RRESP	=> m_axi_rresp,
                 M_AXI_RLAST	=> m_axi_rlast,
                 M_AXI_RUSER	=> m_axi_ruser,
                 M_AXI_RVALID	=> m_axi_rvalid,
                 M_AXI_RREADY	=> m_axi_rready
             );

-- Add user logic here

-- User logic ends

end arch_imp;
