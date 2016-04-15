library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library xil_defaultlib;
use xil_defaultlib.all;

entity MINIMAL_DMA_CONTROL_v1_0 is
	generic (
		-- Users to add parameters here
        DMA_ADDR_WIDTH : integer := 32;
        DMA_LEN_WIDTH : integer := 8;
        
        IO_DATA_WIDTH : integer := 32;
        
        GEN_DONE : boolean := true;
		-- User parameters ends
		-- Do not modify the parameters beyond this line


		-- Parameters of Axi Slave Bus Interface S_AXI
		C_S_AXI_DATA_WIDTH	: integer	:= 32;
		C_S_AXI_ADDR_WIDTH	: integer	:= 5
	);
	port (
		-- Users to add ports here

		-- User ports ends
		-- Do not modify the ports beyond this line


         
        r_addr    : out std_logic_vector(DMA_ADDR_WIDTH-1 downto 0);
        r_len    : out std_logic_vector(DMA_LEN_WIDTH-1 downto 0);
        r_valid : out std_logic;
        r_ready : in std_logic;
        
        w_addr    : out std_logic_vector(DMA_ADDR_WIDTH-1 downto 0);
        w_len    : out std_logic_vector(DMA_LEN_WIDTH-1 downto 0);
        w_valid : out std_logic;
        w_ready : in  std_logic;
        
        rst : out std_logic;
        
        axis_rst : out std_logic;
        
        interrupt : out std_logic;
        

        out_data : out std_logic_vector(IO_DATA_WIDTH-1 downto 0);
        out_valid : out std_logic;
        out_last : out std_logic := '0';
        out_ready : in std_logic;
        
        in_data : in std_logic_vector(IO_DATA_WIDTH-1 downto 0);
        in_valid : in std_logic;
        in_last : in std_logic;
        in_ready : out std_logic;
        
        
        m_axis_data : out std_logic_vector(IO_DATA_WIDTH-1 downto 0);
        m_axis_valid : out std_logic;
        m_axis_last : out std_logic;
        m_axis_ready : in std_logic;
        
        s_axis_data : in std_logic_vector(IO_DATA_WIDTH-1 downto 0);
        s_axis_valid : in std_logic;
        s_axis_last : in std_logic;
        s_axis_ready : out std_logic;
        
         
		-- Ports of Axi Slave Bus Interface S_AXI
		s_axi_aclk	: in std_logic;
		s_axi_aresetn	: in std_logic;
		s_axi_awaddr	: in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
		s_axi_awprot	: in std_logic_vector(2 downto 0);
		s_axi_awvalid	: in std_logic;
		s_axi_awready	: out std_logic;
		s_axi_wdata	: in std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
		s_axi_wstrb	: in std_logic_vector((C_S_AXI_DATA_WIDTH/8)-1 downto 0);
		s_axi_wvalid	: in std_logic;
		s_axi_wready	: out std_logic;
		s_axi_bresp	: out std_logic_vector(1 downto 0);
		s_axi_bvalid	: out std_logic;
		s_axi_bready	: in std_logic;
		s_axi_araddr	: in std_logic_vector(C_S_AXI_ADDR_WIDTH-1 downto 0);
		s_axi_arprot	: in std_logic_vector(2 downto 0);
		s_axi_arvalid	: in std_logic;
		s_axi_arready	: out std_logic;
		s_axi_rdata	: out std_logic_vector(C_S_AXI_DATA_WIDTH-1 downto 0);
		s_axi_rresp	: out std_logic_vector(1 downto 0);
		s_axi_rvalid	: out std_logic;
		s_axi_rready	: in std_logic
	);
end MINIMAL_DMA_CONTROL_v1_0;

architecture arch_imp of MINIMAL_DMA_CONTROL_v1_0 is

     signal read_last_beat : std_logic;
     signal write_last_beat : std_logic;
     signal s_rst : std_logic;
     
     signal s_w_valid : std_logic;
     
     signal s_w_len : std_logic_vector(DMA_LEN_WIDTH-1 downto 0);
     signal suppress_r_last : std_logic;
     
     
     signal last_cnt : unsigned(DMA_LEN_WIDTH-1 downto 0);
     

begin

out_data <= s_axis_data;
out_valid <= s_axis_valid;
out_last <= s_axis_last;
s_axis_ready <= out_ready;


m_axis_data <= in_data;
m_axis_valid <= in_valid;
m_axis_last <= in_last and not suppress_r_last;
in_ready <= m_axis_ready;

read_last_beat <= in_valid and in_last and m_axis_ready;



axis_rst <= s_rst;
rst <= s_rst;

w_len <= s_w_len;
w_valid <= s_w_valid;

IF_GEN_LAST : if GEN_DONE = true generate

process
begin
wait until rising_edge(s_axi_aclk);
    if(s_axi_aresetn = '0' or s_rst = '1') then
        last_cnt <= (last_cnt'range => '1');
    else
        if(s_w_valid = '1' and w_ready = '1') then
            last_cnt <= unsigned(s_w_len);
        else
            if(s_axis_valid = '1' and out_ready = '1') then
                last_cnt <= last_cnt -1;
            end if;
        end if;
    end if;
end process;

write_last_beat <= s_axis_valid and out_ready when last_cnt = to_unsigned(0,last_cnt'length) else '0';

end generate;

IFN_GEN_LAST : if GEN_DONE = false generate
    write_last_beat <= s_axis_valid and s_axis_last and out_ready;
end generate;


-- Instantiation of Axi Bus Interface S_AXI
MINIMAL_DMA_CONTROL_v1_0_S_AXI_inst : entity xil_defaultlib.MINIMAL_DMA_CONTROL_v1_0_S_AXI
	generic map (
	DMA_ADDR_WIDTH => DMA_ADDR_WIDTH,
	DMA_LEN_WIDTH => DMA_LEN_WIDTH,
	
		C_S_AXI_DATA_WIDTH	=> C_S_AXI_DATA_WIDTH,
		C_S_AXI_ADDR_WIDTH	=> C_S_AXI_ADDR_WIDTH
	)
	port map (
	r_addr => r_addr,
    r_len => r_len,
    r_valid => r_valid,
    r_ready => r_ready,
    
    w_addr => w_addr,
    w_len => s_w_len,
    w_valid => s_w_valid,
    w_ready => w_ready,
    
    read_last_beat => read_last_beat,
    write_last_beat => write_last_beat,
    
    rst => s_rst,
    interrupt => interrupt,
    suppress_r_last => suppress_r_last,
	
		S_AXI_ACLK	=> s_axi_aclk,
		S_AXI_ARESETN	=> s_axi_aresetn,
		S_AXI_AWADDR	=> s_axi_awaddr,
		S_AXI_AWPROT	=> s_axi_awprot,
		S_AXI_AWVALID	=> s_axi_awvalid,
		S_AXI_AWREADY	=> s_axi_awready,
		S_AXI_WDATA	=> s_axi_wdata,
		S_AXI_WSTRB	=> s_axi_wstrb,
		S_AXI_WVALID	=> s_axi_wvalid,
		S_AXI_WREADY	=> s_axi_wready,
		S_AXI_BRESP	=> s_axi_bresp,
		S_AXI_BVALID	=> s_axi_bvalid,
		S_AXI_BREADY	=> s_axi_bready,
		S_AXI_ARADDR	=> s_axi_araddr,
		S_AXI_ARPROT	=> s_axi_arprot,
		S_AXI_ARVALID	=> s_axi_arvalid,
		S_AXI_ARREADY	=> s_axi_arready,
		S_AXI_RDATA	=> s_axi_rdata,
		S_AXI_RRESP	=> s_axi_rresp,
		S_AXI_RVALID	=> s_axi_rvalid,
		S_AXI_RREADY	=> s_axi_rready
	);

	-- Add user logic here

	-- User logic ends

end arch_imp;
