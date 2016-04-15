--Copyright 1986-2015 Xilinx, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2015.2 (lin64) Build 1266856 Fri Jun 26 16:35:25 MDT 2015
--Date        : Tue Jan 26 13:58:53 2016
--Host        : philipp-ThinkPad-X250 running 64-bit Ubuntu 15.04
--Command     : generate_target template_design_wrapper.bd
--Design      : template_design_wrapper
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;

entity top is
  port (
    DDR_addr  : inout STD_LOGIC_VECTOR ( 14 downto 0 );
    DDR_ba    : inout STD_LOGIC_VECTOR ( 2 downto 0 );
    DDR_cas_n : inout STD_LOGIC;
    DDR_ck_n  : inout STD_LOGIC;
    DDR_ck_p  : inout STD_LOGIC;
    DDR_cke   : inout STD_LOGIC;
    DDR_cs_n  : inout STD_LOGIC;
    DDR_dm    : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_dq    : inout STD_LOGIC_VECTOR ( 31 downto 0 );
    DDR_dqs_n : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_dqs_p : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_odt   : inout STD_LOGIC;
    DDR_ras_n : inout STD_LOGIC;
    DDR_reset_n : inout STD_LOGIC;
    DDR_we_n  : inout STD_LOGIC;
    --
    FIXED_IO_ddr_vrn  : inout STD_LOGIC;
    FIXED_IO_ddr_vrp  : inout STD_LOGIC;
    FIXED_IO_mio      : inout STD_LOGIC_VECTOR ( 53 downto 0 );
    FIXED_IO_ps_clk   : inout STD_LOGIC;
    FIXED_IO_ps_porb  : inout STD_LOGIC;
    FIXED_IO_ps_srstb : inout STD_LOGIC
  );
end top;

architecture STRUCTURE of top is
  component template_design_wrapper is
  port (
    DDR_cas_n : inout STD_LOGIC;
    DDR_cke : inout STD_LOGIC;
    DDR_ck_n : inout STD_LOGIC;
    DDR_ck_p : inout STD_LOGIC;
    DDR_cs_n : inout STD_LOGIC;
    DDR_reset_n : inout STD_LOGIC;
    DDR_odt : inout STD_LOGIC;
    DDR_ras_n : inout STD_LOGIC;
    DDR_we_n : inout STD_LOGIC;
    DDR_ba : inout STD_LOGIC_VECTOR ( 2 downto 0 );
    DDR_addr : inout STD_LOGIC_VECTOR ( 14 downto 0 );
    DDR_dm : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_dq : inout STD_LOGIC_VECTOR ( 31 downto 0 );
    DDR_dqs_n : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    DDR_dqs_p : inout STD_LOGIC_VECTOR ( 3 downto 0 );
    FIXED_IO_mio : inout STD_LOGIC_VECTOR ( 53 downto 0 );
    FIXED_IO_ddr_vrn : inout STD_LOGIC;
    FIXED_IO_ddr_vrp : inout STD_LOGIC;
    FIXED_IO_ps_srstb : inout STD_LOGIC;
    FIXED_IO_ps_clk : inout STD_LOGIC;
    FIXED_IO_ps_porb : inout STD_LOGIC;
    m_axis_tdata : out STD_LOGIC_VECTOR ( 31 downto 0 );
    m_axis_tlast : out STD_LOGIC;
    m_axis_tready : in STD_LOGIC;
    m_axis_tvalid : out STD_LOGIC;
    s_axis_tdata : in STD_LOGIC_VECTOR ( 31 downto 0 );
    s_axis_tlast : in STD_LOGIC;
    s_axis_tready : out STD_LOGIC;
    s_axis_tvalid : in STD_LOGIC;
    CLK : out std_logic;
    RST : out std_logic
  );
  end component template_design_wrapper;
   
  signal CLK : std_logic;
  signal RST : std_logic;

  signal m_axis_tdata  :  STD_LOGIC_VECTOR ( 31 downto 0 );
  signal m_axis_tkeep  :  STD_LOGIC_VECTOR ( 3 downto 0 ) :=(others => '0');
  signal m_axis_tlast  :  STD_LOGIC;
  signal m_axis_tready :  STD_LOGIC;
  signal m_axis_tvalid :  STD_LOGIC;
  --
  signal s_axis_tdata  :  STD_LOGIC_VECTOR ( 31 downto 0 );
  signal s_axis_tkeep  :  STD_LOGIC_VECTOR ( 3 downto 0 ):=(others => '0');
  signal s_axis_tlast  :  STD_LOGIC;
  signal s_axis_tready :  STD_LOGIC;
  signal s_axis_tvalid :  STD_LOGIC;



begin
template_design_wrapper_i: component template_design_wrapper
     port map (
      DDR_addr(14 downto 0) => DDR_addr(14 downto 0),
      DDR_ba(2 downto 0) => DDR_ba(2 downto 0),
      DDR_cas_n => DDR_cas_n,
      DDR_ck_n => DDR_ck_n,
      DDR_ck_p => DDR_ck_p,
      DDR_cke => DDR_cke,
      DDR_cs_n => DDR_cs_n,
      DDR_dm(3 downto 0) => DDR_dm(3 downto 0),
      DDR_dq(31 downto 0) => DDR_dq(31 downto 0),
      DDR_dqs_n(3 downto 0) => DDR_dqs_n(3 downto 0),
      DDR_dqs_p(3 downto 0) => DDR_dqs_p(3 downto 0),
      DDR_odt => DDR_odt,
      DDR_ras_n => DDR_ras_n,
      DDR_reset_n => DDR_reset_n,
      DDR_we_n => DDR_we_n,
      FIXED_IO_ddr_vrn => FIXED_IO_ddr_vrn,
      FIXED_IO_ddr_vrp => FIXED_IO_ddr_vrp,
      FIXED_IO_mio(53 downto 0) => FIXED_IO_mio(53 downto 0),
      FIXED_IO_ps_clk => FIXED_IO_ps_clk,
      FIXED_IO_ps_porb => FIXED_IO_ps_porb,
      FIXED_IO_ps_srstb => FIXED_IO_ps_srstb,
      m_axis_tdata(31 downto 0) => m_axis_tdata(31 downto 0),
  --    m_axis_tkeep(3 downto 0) => m_axis_tkeep(3 downto 0),
      m_axis_tlast => m_axis_tlast,
      m_axis_tready => m_axis_tready,
      m_axis_tvalid => m_axis_tvalid,
      s_axis_tdata(31 downto 0) => s_axis_tdata(31 downto 0),
  --    s_axis_tkeep(3 downto 0) => s_axis_tkeep(3 downto 0),
      s_axis_tlast => s_axis_tlast,
      s_axis_tready => s_axis_tready,
      s_axis_tvalid => s_axis_tvalid,
      CLK => CLK,
      RST => RST
    );

accel_wrapper :  entity work.accel_wrapper
    port map(
      CLK                             => CLK,
      RST                             => RST,
      VALID_IN                        => m_axis_tvalid,
      M_AXIS_MM2S_tdata(31 downto 0)  => m_axis_tdata(31 downto 0),
      M_AXIS_MM2S_tkeep(3 downto 0)   => m_axis_tkeep(3 downto 0),
      M_AXIS_MM2S_tlast               => m_axis_tlast,
      M_AXIS_MM2S_tready              => m_axis_tready,
      VALID_OUT                       => s_axis_tvalid,
      S_AXIS_S2MM_tdata(31 downto 0)  => s_axis_tdata(31 downto 0),
      S_AXIS_S2MM_tkeep(3 downto 0)   => s_axis_tkeep(3 downto 0),
      S_AXIS_S2MM_tlast               => s_axis_tlast,
      S_AXIS_S2MM_tready              => s_axis_tready
    );
end STRUCTURE;
