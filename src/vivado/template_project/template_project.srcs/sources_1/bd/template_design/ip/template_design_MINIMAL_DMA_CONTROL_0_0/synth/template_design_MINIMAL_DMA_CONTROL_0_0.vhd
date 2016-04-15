-- (c) Copyright 1995-2016 Xilinx, Inc. All rights reserved.
-- 
-- This file contains confidential and proprietary information
-- of Xilinx, Inc. and is protected under U.S. and
-- international copyright and other intellectual property
-- laws.
-- 
-- DISCLAIMER
-- This disclaimer is not a license and does not grant any
-- rights to the materials distributed herewith. Except as
-- otherwise provided in a valid license issued to you by
-- Xilinx, and to the maximum extent permitted by applicable
-- law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
-- WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
-- AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
-- BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
-- INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
-- (2) Xilinx shall not be liable (whether in contract or tort,
-- including negligence, or under any other theory of
-- liability) for any loss or damage of any kind or nature
-- related to, arising under or in connection with these
-- materials, including for any direct, or any indirect,
-- special, incidental, or consequential loss or damage
-- (including loss of data, profits, goodwill, or any type of
-- loss or damage suffered as a result of any action brought
-- by a third party) even if such damage or loss was
-- reasonably foreseeable or Xilinx had been advised of the
-- possibility of the same.
-- 
-- CRITICAL APPLICATIONS
-- Xilinx products are not designed or intended to be fail-
-- safe, or for use in any application requiring fail-safe
-- performance, such as life-support or safety devices or
-- systems, Class III medical devices, nuclear facilities,
-- applications related to the deployment of airbags, or any
-- other applications that could lead to death, personal
-- injury, or severe property or environmental damage
-- (individually and collectively, "Critical
-- Applications"). Customer assumes the sole risk and
-- liability of any use of Xilinx products in Critical
-- Applications, subject only to applicable laws and
-- regulations governing limitations on product liability.
-- 
-- THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
-- PART OF THIS FILE AT ALL TIMES.
-- 
-- DO NOT MODIFY THIS FILE.

-- IP VLNV: user.org:user:MINIMAL_DMA_CONTROL:1.0
-- IP Revision: 1

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY template_design_MINIMAL_DMA_CONTROL_0_0 IS
  PORT (
    r_addr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    r_len : OUT STD_LOGIC_VECTOR(19 DOWNTO 0);
    r_valid : OUT STD_LOGIC;
    r_ready : IN STD_LOGIC;
    w_addr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    w_len : OUT STD_LOGIC_VECTOR(19 DOWNTO 0);
    w_valid : OUT STD_LOGIC;
    w_ready : IN STD_LOGIC;
    rst : OUT STD_LOGIC;
    axis_rst : OUT STD_LOGIC;
    interrupt : OUT STD_LOGIC;
    out_data : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    out_valid : OUT STD_LOGIC;
    out_last : OUT STD_LOGIC;
    out_ready : IN STD_LOGIC;
    in_data : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    in_valid : IN STD_LOGIC;
    in_last : IN STD_LOGIC;
    in_ready : OUT STD_LOGIC;
    m_axis_data : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    m_axis_valid : OUT STD_LOGIC;
    m_axis_last : OUT STD_LOGIC;
    m_axis_ready : IN STD_LOGIC;
    s_axis_data : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    s_axis_valid : IN STD_LOGIC;
    s_axis_last : IN STD_LOGIC;
    s_axis_ready : OUT STD_LOGIC;
    s_axi_awaddr : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
    s_axi_awprot : IN STD_LOGIC_VECTOR(2 DOWNTO 0);
    s_axi_awvalid : IN STD_LOGIC;
    s_axi_awready : OUT STD_LOGIC;
    s_axi_wdata : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    s_axi_wstrb : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
    s_axi_wvalid : IN STD_LOGIC;
    s_axi_wready : OUT STD_LOGIC;
    s_axi_bresp : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    s_axi_bvalid : OUT STD_LOGIC;
    s_axi_bready : IN STD_LOGIC;
    s_axi_araddr : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
    s_axi_arprot : IN STD_LOGIC_VECTOR(2 DOWNTO 0);
    s_axi_arvalid : IN STD_LOGIC;
    s_axi_arready : OUT STD_LOGIC;
    s_axi_rdata : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    s_axi_rresp : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    s_axi_rvalid : OUT STD_LOGIC;
    s_axi_rready : IN STD_LOGIC;
    s_axi_aclk : IN STD_LOGIC;
    s_axi_aresetn : IN STD_LOGIC
  );
END template_design_MINIMAL_DMA_CONTROL_0_0;

ARCHITECTURE template_design_MINIMAL_DMA_CONTROL_0_0_arch OF template_design_MINIMAL_DMA_CONTROL_0_0 IS
  ATTRIBUTE DowngradeIPIdentifiedWarnings : string;
  ATTRIBUTE DowngradeIPIdentifiedWarnings OF template_design_MINIMAL_DMA_CONTROL_0_0_arch: ARCHITECTURE IS "yes";

  COMPONENT MINIMAL_DMA_CONTROL_v1_0 IS
    GENERIC (
      C_S_AXI_DATA_WIDTH : INTEGER; -- Width of S_AXI data bus
      C_S_AXI_ADDR_WIDTH : INTEGER; -- Width of S_AXI address bus
      DMA_ADDR_WIDTH : INTEGER;
      DMA_LEN_WIDTH : INTEGER;
      IO_DATA_WIDTH : INTEGER;
      GEN_DONE : BOOLEAN
    );
    PORT (
      r_addr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      r_len : OUT STD_LOGIC_VECTOR(19 DOWNTO 0);
      r_valid : OUT STD_LOGIC;
      r_ready : IN STD_LOGIC;
      w_addr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      w_len : OUT STD_LOGIC_VECTOR(19 DOWNTO 0);
      w_valid : OUT STD_LOGIC;
      w_ready : IN STD_LOGIC;
      rst : OUT STD_LOGIC;
      axis_rst : OUT STD_LOGIC;
      interrupt : OUT STD_LOGIC;
      out_data : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      out_valid : OUT STD_LOGIC;
      out_last : OUT STD_LOGIC;
      out_ready : IN STD_LOGIC;
      in_data : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      in_valid : IN STD_LOGIC;
      in_last : IN STD_LOGIC;
      in_ready : OUT STD_LOGIC;
      m_axis_data : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      m_axis_valid : OUT STD_LOGIC;
      m_axis_last : OUT STD_LOGIC;
      m_axis_ready : IN STD_LOGIC;
      s_axis_data : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      s_axis_valid : IN STD_LOGIC;
      s_axis_last : IN STD_LOGIC;
      s_axis_ready : OUT STD_LOGIC;
      s_axi_awaddr : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
      s_axi_awprot : IN STD_LOGIC_VECTOR(2 DOWNTO 0);
      s_axi_awvalid : IN STD_LOGIC;
      s_axi_awready : OUT STD_LOGIC;
      s_axi_wdata : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      s_axi_wstrb : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
      s_axi_wvalid : IN STD_LOGIC;
      s_axi_wready : OUT STD_LOGIC;
      s_axi_bresp : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
      s_axi_bvalid : OUT STD_LOGIC;
      s_axi_bready : IN STD_LOGIC;
      s_axi_araddr : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
      s_axi_arprot : IN STD_LOGIC_VECTOR(2 DOWNTO 0);
      s_axi_arvalid : IN STD_LOGIC;
      s_axi_arready : OUT STD_LOGIC;
      s_axi_rdata : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      s_axi_rresp : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
      s_axi_rvalid : OUT STD_LOGIC;
      s_axi_rready : IN STD_LOGIC;
      s_axi_aclk : IN STD_LOGIC;
      s_axi_aresetn : IN STD_LOGIC
    );
  END COMPONENT MINIMAL_DMA_CONTROL_v1_0;
  ATTRIBUTE X_CORE_INFO : STRING;
  ATTRIBUTE X_CORE_INFO OF template_design_MINIMAL_DMA_CONTROL_0_0_arch: ARCHITECTURE IS "MINIMAL_DMA_CONTROL_v1_0,Vivado 2015.2";
  ATTRIBUTE CHECK_LICENSE_TYPE : STRING;
  ATTRIBUTE CHECK_LICENSE_TYPE OF template_design_MINIMAL_DMA_CONTROL_0_0_arch : ARCHITECTURE IS "template_design_MINIMAL_DMA_CONTROL_0_0,MINIMAL_DMA_CONTROL_v1_0,{}";
  ATTRIBUTE X_INTERFACE_INFO : STRING;
  ATTRIBUTE X_INTERFACE_INFO OF r_addr: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_addr";
  ATTRIBUTE X_INTERFACE_INFO OF r_len: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_len";
  ATTRIBUTE X_INTERFACE_INFO OF r_valid: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_valid";
  ATTRIBUTE X_INTERFACE_INFO OF r_ready: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_ready";
  ATTRIBUTE X_INTERFACE_INFO OF w_addr: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_addr";
  ATTRIBUTE X_INTERFACE_INFO OF w_len: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_len";
  ATTRIBUTE X_INTERFACE_INFO OF w_valid: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_valid";
  ATTRIBUTE X_INTERFACE_INFO OF w_ready: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_ready";
  ATTRIBUTE X_INTERFACE_INFO OF rst: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control rst";
  ATTRIBUTE X_INTERFACE_INFO OF axis_rst: SIGNAL IS "xilinx.com:signal:reset:1.0 axis_rst RST";
  ATTRIBUTE X_INTERFACE_INFO OF interrupt: SIGNAL IS "xilinx.com:signal:interrupt:1.0 int INTERRUPT";
  ATTRIBUTE X_INTERFACE_INFO OF out_data: SIGNAL IS "fau.de:user:my_data_stream:1.0 out_data data";
  ATTRIBUTE X_INTERFACE_INFO OF out_valid: SIGNAL IS "fau.de:user:my_data_stream:1.0 out_data valid";
  ATTRIBUTE X_INTERFACE_INFO OF out_last: SIGNAL IS "fau.de:user:my_data_stream:1.0 out_data last";
  ATTRIBUTE X_INTERFACE_INFO OF out_ready: SIGNAL IS "fau.de:user:my_data_stream:1.0 out_data ready";
  ATTRIBUTE X_INTERFACE_INFO OF in_data: SIGNAL IS "fau.de:user:my_data_stream:1.0 in_data data";
  ATTRIBUTE X_INTERFACE_INFO OF in_valid: SIGNAL IS "fau.de:user:my_data_stream:1.0 in_data valid";
  ATTRIBUTE X_INTERFACE_INFO OF in_last: SIGNAL IS "fau.de:user:my_data_stream:1.0 in_data last";
  ATTRIBUTE X_INTERFACE_INFO OF in_ready: SIGNAL IS "fau.de:user:my_data_stream:1.0 in_data ready";
  ATTRIBUTE X_INTERFACE_INFO OF m_axis_data: SIGNAL IS "xilinx.com:interface:axis:1.0 m_axis TDATA";
  ATTRIBUTE X_INTERFACE_INFO OF m_axis_valid: SIGNAL IS "xilinx.com:interface:axis:1.0 m_axis TVALID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axis_last: SIGNAL IS "xilinx.com:interface:axis:1.0 m_axis TLAST";
  ATTRIBUTE X_INTERFACE_INFO OF m_axis_ready: SIGNAL IS "xilinx.com:interface:axis:1.0 m_axis TREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axis_data: SIGNAL IS "xilinx.com:interface:axis:1.0 s_axis TDATA";
  ATTRIBUTE X_INTERFACE_INFO OF s_axis_valid: SIGNAL IS "xilinx.com:interface:axis:1.0 s_axis TVALID";
  ATTRIBUTE X_INTERFACE_INFO OF s_axis_last: SIGNAL IS "xilinx.com:interface:axis:1.0 s_axis TLAST";
  ATTRIBUTE X_INTERFACE_INFO OF s_axis_ready: SIGNAL IS "xilinx.com:interface:axis:1.0 s_axis TREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_awaddr: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI AWADDR";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_awprot: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI AWPROT";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_awvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI AWVALID";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_awready: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI AWREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_wdata: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI WDATA";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_wstrb: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI WSTRB";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_wvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI WVALID";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_wready: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI WREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_bresp: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI BRESP";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_bvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI BVALID";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_bready: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI BREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_araddr: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI ARADDR";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_arprot: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI ARPROT";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_arvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI ARVALID";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_arready: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI ARREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_rdata: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI RDATA";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_rresp: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI RRESP";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_rvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI RVALID";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_rready: SIGNAL IS "xilinx.com:interface:aximm:1.0 S_AXI RREADY";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_aclk: SIGNAL IS "xilinx.com:signal:clock:1.0 S_AXI_CLK CLK";
  ATTRIBUTE X_INTERFACE_INFO OF s_axi_aresetn: SIGNAL IS "xilinx.com:signal:reset:1.0 S_AXI_RST RST";
BEGIN
  U0 : MINIMAL_DMA_CONTROL_v1_0
    GENERIC MAP (
      C_S_AXI_DATA_WIDTH => 32,
      C_S_AXI_ADDR_WIDTH => 5,
      DMA_ADDR_WIDTH => 32,
      DMA_LEN_WIDTH => 20,
      IO_DATA_WIDTH => 32,
      GEN_DONE => true
    )
    PORT MAP (
      r_addr => r_addr,
      r_len => r_len,
      r_valid => r_valid,
      r_ready => r_ready,
      w_addr => w_addr,
      w_len => w_len,
      w_valid => w_valid,
      w_ready => w_ready,
      rst => rst,
      axis_rst => axis_rst,
      interrupt => interrupt,
      out_data => out_data,
      out_valid => out_valid,
      out_last => out_last,
      out_ready => out_ready,
      in_data => in_data,
      in_valid => in_valid,
      in_last => in_last,
      in_ready => in_ready,
      m_axis_data => m_axis_data,
      m_axis_valid => m_axis_valid,
      m_axis_last => m_axis_last,
      m_axis_ready => m_axis_ready,
      s_axis_data => s_axis_data,
      s_axis_valid => s_axis_valid,
      s_axis_last => s_axis_last,
      s_axis_ready => s_axis_ready,
      s_axi_awaddr => s_axi_awaddr,
      s_axi_awprot => s_axi_awprot,
      s_axi_awvalid => s_axi_awvalid,
      s_axi_awready => s_axi_awready,
      s_axi_wdata => s_axi_wdata,
      s_axi_wstrb => s_axi_wstrb,
      s_axi_wvalid => s_axi_wvalid,
      s_axi_wready => s_axi_wready,
      s_axi_bresp => s_axi_bresp,
      s_axi_bvalid => s_axi_bvalid,
      s_axi_bready => s_axi_bready,
      s_axi_araddr => s_axi_araddr,
      s_axi_arprot => s_axi_arprot,
      s_axi_arvalid => s_axi_arvalid,
      s_axi_arready => s_axi_arready,
      s_axi_rdata => s_axi_rdata,
      s_axi_rresp => s_axi_rresp,
      s_axi_rvalid => s_axi_rvalid,
      s_axi_rready => s_axi_rready,
      s_axi_aclk => s_axi_aclk,
      s_axi_aresetn => s_axi_aresetn
    );
END template_design_MINIMAL_DMA_CONTROL_0_0_arch;
