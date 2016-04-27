----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 02/19/2015 10:31:08 AM
-- Design Name: 
-- Module Name: tb_minimal_dma - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;


library xil_defaultlib;
use xil_defaultlib.MINIMAL_DMA_v1_0_M_AXI;


-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity tb_minimal_dma is
--  Port ( );
end tb_minimal_dma;

architecture Behavioral of tb_minimal_dma is

constant clk_period : time := 10ns;

constant		LEN_WIDTH : integer := 13;
constant		C_M_AXI_BURST_LEN	: integer	:= 16; --256
constant		C_M_AXI_ID_WIDTH	: integer	:= 1;
constant		C_M_AXI_ADDR_WIDTH	: integer	:= 32;
constant		C_M_AXI_DATA_WIDTH	: integer	:= 32;
constant		C_M_AXI_AWUSER_WIDTH	: integer	:= 0;
constant		C_M_AXI_ARUSER_WIDTH	: integer	:= 0;
constant		C_M_AXI_WUSER_WIDTH	: integer	:= 0;
constant		C_M_AXI_RUSER_WIDTH	: integer	:= 0;
constant		C_M_AXI_BUSER_WIDTH	: integer	:= 0;
		
		
signal		out_data :  std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
signal        out_valid :  std_logic;
signal        in_ready :  std_logic;
signal        r_ready :  std_logic;
signal        w_ready :  std_logic;
		
signal		M_AXI_AWID	:  std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
signal		M_AXI_AWADDR	:  std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
signal		M_AXI_AWLEN	:  std_logic_vector(7 downto 0);
signal		M_AXI_AWSIZE	:  std_logic_vector(2 downto 0);
signal		M_AXI_AWBURST	:  std_logic_vector(1 downto 0);
signal		M_AXI_AWLOCK	:  std_logic;
signal		M_AXI_AWCACHE	:  std_logic_vector(3 downto 0);
signal		M_AXI_AWPROT	:  std_logic_vector(2 downto 0);
signal		M_AXI_AWQOS	:  std_logic_vector(3 downto 0);
signal		M_AXI_AWUSER	:  std_logic_vector(C_M_AXI_AWUSER_WIDTH-1 downto 0);
signal		M_AXI_AWVALID	:  std_logic;

signal		M_AXI_WDATA	:  std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
signal		M_AXI_WSTRB	:  std_logic_vector(C_M_AXI_DATA_WIDTH/8-1 downto 0);
signal		M_AXI_WLAST	:  std_logic;
signal		M_AXI_WUSER	:  std_logic_vector(C_M_AXI_WUSER_WIDTH-1 downto 0);
signal		M_AXI_WVALID	:  std_logic;
signal		M_AXI_BREADY	:  std_logic;
signal		M_AXI_ARID	:  std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
signal		M_AXI_ARADDR	:  std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
signal		M_AXI_ARLEN	:  std_logic_vector(7 downto 0);
signal		M_AXI_ARSIZE	:  std_logic_vector(2 downto 0);
signal		M_AXI_ARBURST	:  std_logic_vector(1 downto 0);
signal		M_AXI_ARLOCK	:  std_logic;
signal		M_AXI_ARCACHE	:  std_logic_vector(3 downto 0);
signal		M_AXI_ARPROT	:  std_logic_vector(2 downto 0);
signal		M_AXI_ARQOS	:  std_logic_vector(3 downto 0);
signal		M_AXI_ARUSER	:  std_logic_vector(C_M_AXI_ARUSER_WIDTH-1 downto 0);
signal		M_AXI_ARVALID	:  std_logic;
signal		M_AXI_RREADY	:  std_logic;



-- inputs:

signal      out_ready :  std_logic := '0';
signal      w_addr    :  std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0) := (others => '0');
signal      w_len    :  std_logic_vector(LEN_WIDTH-1 downto 0) := (others => '0');
signal      w_valid :  std_logic := '0';  
signal      in_data :  std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0) := (others => '0');
signal      in_valid :  std_logic := '0';      
signal      r_addr    :  std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0) := (others => '0');
signal      r_len    :  std_logic_vector(LEN_WIDTH-1 downto 0) := (others => '0');
signal      r_valid :  std_logic := '0';
signal      rst :  std_logic := '0';
		
signal		M_AXI_ACLK	:  std_logic := '0';
signal		M_AXI_ARESETN	:  std_logic := '0';

signal		M_AXI_WREADY	:  std_logic := '0';
signal		M_AXI_BID	:  std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0) := (others => '0');

signal		M_AXI_BUSER	:  std_logic_vector(C_M_AXI_BUSER_WIDTH-1 downto 0) := (others => '0');
signal		M_AXI_BVALID	:  std_logic := '0';
signal		M_AXI_ARREADY	:  std_logic := '0';
signal		M_AXI_RID	:  std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0) := (others => '0');
signal		M_AXI_RDATA	:  std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0) := (others => '0');

signal		M_AXI_RLAST	:  std_logic := '0';
signal		M_AXI_RUSER	:  std_logic_vector(C_M_AXI_RUSER_WIDTH-1 downto 0) := (others => '0');
signal		M_AXI_RVALID	:  std_logic := '0';
signal		M_AXI_AWREADY	:  std_logic := '0';

signal		M_AXI_BRESP	:  std_logic_vector(1 downto 0) := "01";
signal		M_AXI_RRESP	:  std_logic_vector(1 downto 0) := "01";


signal out_error : std_logic := '0';

type rom_t is array (0 to 600) of std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
shared variable ROM : rom_t := (others => (others => '0'));

begin


M_AXI_BVALID <= (M_AXI_WLAST or (M_AXI_BVALID and (not M_AXI_BREADY))) when rising_edge(M_AXI_ACLK);


error_check: process
variable old : unsigned(C_M_AXI_DATA_WIDTH-1 downto 0) := to_unsigned(0,C_M_AXI_DATA_WIDTH);
begin

while ( rst = '0' ) loop

wait until rising_edge(M_AXI_ACLK);

if( out_valid = '1') then
    if (unsigned(out_data) = old) then
        out_error <= '0';
    else
        out_error <= '1';
    end if;
    old := old +1;
end if;


end loop;

    

end process;


clk_proc: process
begin
    wait for clk_period/2;
    M_AXI_ACLK <= not M_AXI_ACLK;
end process;


data_gen:process
begin

wait until rising_edge(M_AXI_ACLK);

if(in_ready = '1') then
    in_data <= std_logic_vector(unsigned(in_data) +1);
end if;

end process;

in_valid <= '1' after (clk_period*10);


stim_proc: process
begin
m_axi_aresetn <= '0';
wait for clk_period*10;
wait until rising_edge(M_AXI_ACLK);
m_axi_aresetn <= '1';
wait until rising_edge(M_AXI_ACLK);
wait until rising_edge(M_AXI_ACLK);


--while (w_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;

--w_len <= std_logic_vector(to_unsigned(1,r_len'length)); -- 2 beats
--w_addr <= std_logic_vector(to_unsigned(0*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @0
--w_valid <= '1';
--wait until rising_edge(M_AXI_ACLK);
--w_valid <= '0';
--wait until rising_edge(M_AXI_ACLK);




while (w_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
wait until rising_edge(M_AXI_ACLK);
wait for clk_period*10;
wait until rising_edge(M_AXI_ACLK);

w_len <= std_logic_vector(to_unsigned(129,r_len'length)); -- 1 beat
w_addr <= std_logic_vector(to_unsigned(2*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @2
w_valid <= '1';
wait until rising_edge(M_AXI_ACLK);
w_valid <= '0';
wait until rising_edge(M_AXI_ACLK);

while (w_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
wait until rising_edge(M_AXI_ACLK);
w_len <= std_logic_vector(to_unsigned(17*4,r_len'length)); -- 1 beat
w_addr <= std_logic_vector(to_unsigned(2*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @2
w_valid <= '1';
wait until rising_edge(M_AXI_ACLK);
w_valid <= '0';
wait until rising_edge(M_AXI_ACLK);



--wait for clk_period*10;
--wait until rising_edge(M_AXI_ACLK);


--w_len <= std_logic_vector(to_unsigned(23,r_len'length)); -- 23 beats
--w_addr <= std_logic_vector(to_unsigned(3*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @3
--w_valid <= '1';
--wait until rising_edge(M_AXI_ACLK);
--w_valid <= '0';
--wait until rising_edge(M_AXI_ACLK);




--while (w_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
--wait until rising_edge(M_AXI_ACLK);
--wait for clk_period*10;
--wait until rising_edge(M_AXI_ACLK);


--w_len <= std_logic_vector(to_unsigned(C_M_AXI_BURST_LEN*3+1,r_len'length)); -- C_M_AXI_BURST_LEN beats
--w_addr <= std_logic_vector(to_unsigned(0*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @3
--w_valid <= '1';
--wait until rising_edge(M_AXI_ACLK);
--w_valid <= '0';
--wait until rising_edge(M_AXI_ACLK);

wait for clk_period*60;
wait until rising_edge(M_AXI_ACLK);



--while (w_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
--wait until rising_edge(M_AXI_ACLK);

--wait until rising_edge(M_AXI_ACLK);
--wait for clk_period*10;
--wait until rising_edge(M_AXI_ACLK);


r_len <= std_logic_vector(to_unsigned(4*16*3-1,r_len'length)); -- 5 beats
r_addr <= std_logic_vector(to_unsigned(2*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @0
r_valid <= '1';
wait until rising_edge(M_AXI_ACLK);
while (r_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
r_valid <= '0';
wait until rising_edge(M_AXI_ACLK);

out_ready <= '1';

wait until rising_edge(M_AXI_ACLK);

--r_len <= std_logic_vector(to_unsigned(10,r_len'length)); -- 5 beats
--r_addr <= std_logic_vector(to_unsigned(2*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @2
--r_valid <= '1';
--wait until rising_edge(M_AXI_ACLK);
--while (r_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
--r_valid <= '0';
--wait until rising_edge(M_AXI_ACLK);


--while (r_ready = '0') loop wait until rising_edge(M_AXI_ACLK); end loop;
--wait until rising_edge(M_AXI_ACLK);
--wait for clk_period*10;
--wait until rising_edge(M_AXI_ACLK);


--r_len <= std_logic_vector(to_unsigned(C_M_AXI_BURST_LEN,r_len'length)); -- C_M_AXI_BURST_LEN +1 beat
--r_addr <= std_logic_vector(to_unsigned(3*(C_M_AXI_DATA_WIDTH/8),w_addr'length)); -- @3
--r_valid <= '1';
--wait until rising_edge(M_AXI_ACLK);
--r_valid <= '0';
--wait until rising_edge(M_AXI_ACLK);




wait;
assert M_AXI_ACLK = '1'
report "SIMULATION END" 
severity FAILURE;
				

end process;





r_answer_proc: process
begin
m_axi_arready <= '1';
wait until rising_edge(m_axi_arvalid);
wait until rising_edge(M_AXI_ACLK);
m_axi_arready <= '0';

wait until rising_edge(M_AXI_ACLK);
wait until rising_edge(M_AXI_ACLK);
wait until rising_edge(M_AXI_ACLK);
wait until rising_edge(M_AXI_ACLK);
m_axi_arready <= '0';

end process;


r_data_proc: process
variable len : unsigned(M_AXI_ARLEN'high+1 downto 0);
variable a : unsigned(M_AXI_ARADDR'high downto 0);
begin

wait until rising_edge(m_axi_arvalid);
len := unsigned('0' & M_AXI_ARLEN);
a := unsigned(M_AXI_ARADDR)/(C_M_AXI_DATA_WIDTH/8);
wait for clk_period*6;
wait until rising_edge(M_AXI_ACLK);


while (len(len'high) = '0' ) loop

    M_AXI_RDATA <= ROM(to_integer(a));
    M_AXI_rvalid <= '1';
    if (len = to_unsigned(0,len'length)) then
        m_axi_rlast <= '1';
    end if;
    wait until rising_edge(M_AXI_ACLK);
    
    if (m_axi_rready = '1') then
        a := a + 1;
        len := len - 1;
    end if;
   

end loop;
M_AXI_rvalid <= '0';
m_axi_rlast <= '0';
wait until rising_edge(M_AXI_ACLK);

end process;





w_answer_proc: process
begin
m_axi_awready <= '0';
wait until rising_edge(m_axi_awvalid);
m_axi_awready <= '1';
wait until rising_edge(M_AXI_ACLK);
wait until rising_edge(M_AXI_ACLK);
m_axi_awready <= '0';

end process;

w_data_proc: process
variable len : unsigned(M_AXI_AWLEN'high+1 downto 0);
variable a : unsigned(M_AXI_AWADDR'high downto 0);
begin

wait until rising_edge(m_axi_awvalid);
len := resize(unsigned(M_AXI_AWLEN),len'length);
a := unsigned(M_AXI_AWADDR)/(C_M_AXI_DATA_WIDTH/8);
wait for clk_period*2;
wait until rising_edge(M_AXI_ACLK);

while (len(len'high) = '0') loop

    
    if (m_axi_wvalid = '1' and M_AXI_wready = '1') then
        
        ROM(to_integer(a)) := M_AXI_WDATA;
        a := a + 1;
        len := len - 1;
    end if;
    
    wait until rising_edge(M_AXI_ACLK);    
end loop;



end process;


M_AXI_wready <= m_axi_wvalid when rising_edge(M_AXI_ACLK);

uut : entity xil_defaultlib.MINIMAL_DMA_v1_0_M_AXI
	generic map (
	   LEN_WIDTH => LEN_WIDTH,
	
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
        out_ready => out_ready,
    
        in_data => in_data,
        in_valid => in_valid,
        in_ready => in_ready,
    
        r_addr => r_addr,
        r_len => r_len,
        r_valid => r_valid,
        r_ready => r_ready,
    
        w_addr => w_addr,
        w_len => w_len,
        w_valid => w_valid,
        w_ready => w_ready,
	
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

end Behavioral;
