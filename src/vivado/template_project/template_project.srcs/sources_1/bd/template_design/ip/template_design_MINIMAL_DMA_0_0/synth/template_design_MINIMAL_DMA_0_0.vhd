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

-- IP VLNV: fau.de:user:MINIMAL_DMA:1.0
-- IP Revision: 18

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

ENTITY template_design_MINIMAL_DMA_0_0 IS
  PORT (
    out_data : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    out_valid : OUT STD_LOGIC;
    out_last : OUT STD_LOGIC;
    out_ready : IN STD_LOGIC;
    in_data : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    in_valid : IN STD_LOGIC;
    in_last : IN STD_LOGIC;
    in_ready : OUT STD_LOGIC;
    r_addr : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    r_len : IN STD_LOGIC_VECTOR(25 DOWNTO 0);
    r_valid : IN STD_LOGIC;
    r_ready : OUT STD_LOGIC;
    r_compl : OUT STD_LOGIC;
    w_addr : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    w_len : IN STD_LOGIC_VECTOR(25 DOWNTO 0);
    w_valid : IN STD_LOGIC;
    w_ready : OUT STD_LOGIC;
    w_compl : OUT STD_LOGIC;
    rst : IN STD_LOGIC;
    m_axi_aclk : IN STD_LOGIC;
    m_axi_aresetn : IN STD_LOGIC;
    m_axi_awid : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_awaddr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    m_axi_awlen : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    m_axi_awsize : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    m_axi_awburst : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    m_axi_awlock : OUT STD_LOGIC;
    m_axi_awcache : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
    m_axi_awprot : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    m_axi_awqos : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
    m_axi_awuser : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_awvalid : OUT STD_LOGIC;
    m_axi_awready : IN STD_LOGIC;
    m_axi_wdata : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    m_axi_wstrb : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
    m_axi_wlast : OUT STD_LOGIC;
    m_axi_wuser : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_wvalid : OUT STD_LOGIC;
    m_axi_wready : IN STD_LOGIC;
    m_axi_bid : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_bresp : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
    m_axi_buser : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_bvalid : IN STD_LOGIC;
    m_axi_bready : OUT STD_LOGIC;
    m_axi_arid : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_araddr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    m_axi_arlen : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    m_axi_arsize : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    m_axi_arburst : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    m_axi_arlock : OUT STD_LOGIC;
    m_axi_arcache : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
    m_axi_arprot : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    m_axi_arqos : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
    m_axi_aruser : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_arvalid : OUT STD_LOGIC;
    m_axi_arready : IN STD_LOGIC;
    m_axi_rid : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_rdata : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    m_axi_rresp : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
    m_axi_rlast : IN STD_LOGIC;
    m_axi_ruser : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    m_axi_rvalid : IN STD_LOGIC;
    m_axi_rready : OUT STD_LOGIC
  );
END template_design_MINIMAL_DMA_0_0;

ARCHITECTURE template_design_MINIMAL_DMA_0_0_arch OF template_design_MINIMAL_DMA_0_0 IS
  ATTRIBUTE DowngradeIPIdentifiedWarnings : string;
  ATTRIBUTE DowngradeIPIdentifiedWarnings OF template_design_MINIMAL_DMA_0_0_arch: ARCHITECTURE IS "yes";

  COMPONENT MINIMAL_DMA_v1_0 IS
    GENERIC (
      C_M_AXI_BURST_LEN : INTEGER; -- Burst Length. Supports 1, 2, 4, 8, 16, 32, 64, 128, 256 burst lengths
      C_M_AXI_ID_WIDTH : INTEGER; -- Thread ID Width
      C_M_AXI_ADDR_WIDTH : INTEGER; -- Width of Address Bus
      C_M_AXI_DATA_WIDTH : INTEGER; -- Width of Data Bus
      C_M_AXI_AWUSER_WIDTH : INTEGER; -- Width of User Write Address Bus
      C_M_AXI_ARUSER_WIDTH : INTEGER; -- Width of User Read Address Bus
      C_M_AXI_WUSER_WIDTH : INTEGER; -- Width of User Write Data Bus
      C_M_AXI_RUSER_WIDTH : INTEGER; -- Width of User Read Data Bus
      C_M_AXI_BUSER_WIDTH : INTEGER; -- Width of User Response Bus
      LEN_WIDTH : INTEGER;
      ISSUE_DEPTH : INTEGER
    );
    PORT (
      out_data : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      out_valid : OUT STD_LOGIC;
      out_last : OUT STD_LOGIC;
      out_ready : IN STD_LOGIC;
      in_data : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      in_valid : IN STD_LOGIC;
      in_last : IN STD_LOGIC;
      in_ready : OUT STD_LOGIC;
      r_addr : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      r_len : IN STD_LOGIC_VECTOR(25 DOWNTO 0);
      r_valid : IN STD_LOGIC;
      r_ready : OUT STD_LOGIC;
      r_compl : OUT STD_LOGIC;
      w_addr : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      w_len : IN STD_LOGIC_VECTOR(25 DOWNTO 0);
      w_valid : IN STD_LOGIC;
      w_ready : OUT STD_LOGIC;
      w_compl : OUT STD_LOGIC;
      rst : IN STD_LOGIC;
      m_axi_aclk : IN STD_LOGIC;
      m_axi_aresetn : IN STD_LOGIC;
      m_axi_awid : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_awaddr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      m_axi_awlen : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
      m_axi_awsize : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
      m_axi_awburst : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
      m_axi_awlock : OUT STD_LOGIC;
      m_axi_awcache : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
      m_axi_awprot : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
      m_axi_awqos : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
      m_axi_awuser : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_awvalid : OUT STD_LOGIC;
      m_axi_awready : IN STD_LOGIC;
      m_axi_wdata : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      m_axi_wstrb : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
      m_axi_wlast : OUT STD_LOGIC;
      m_axi_wuser : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_wvalid : OUT STD_LOGIC;
      m_axi_wready : IN STD_LOGIC;
      m_axi_bid : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_bresp : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
      m_axi_buser : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_bvalid : IN STD_LOGIC;
      m_axi_bready : OUT STD_LOGIC;
      m_axi_arid : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_araddr : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
      m_axi_arlen : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
      m_axi_arsize : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
      m_axi_arburst : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
      m_axi_arlock : OUT STD_LOGIC;
      m_axi_arcache : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
      m_axi_arprot : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
      m_axi_arqos : OUT STD_LOGIC_VECTOR(3 DOWNTO 0);
      m_axi_aruser : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_arvalid : OUT STD_LOGIC;
      m_axi_arready : IN STD_LOGIC;
      m_axi_rid : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_rdata : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
      m_axi_rresp : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
      m_axi_rlast : IN STD_LOGIC;
      m_axi_ruser : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
      m_axi_rvalid : IN STD_LOGIC;
      m_axi_rready : OUT STD_LOGIC
    );
  END COMPONENT MINIMAL_DMA_v1_0;
  ATTRIBUTE X_CORE_INFO : STRING;
  ATTRIBUTE X_CORE_INFO OF template_design_MINIMAL_DMA_0_0_arch: ARCHITECTURE IS "MINIMAL_DMA_v1_0,Vivado 2015.2";
  ATTRIBUTE CHECK_LICENSE_TYPE : STRING;
  ATTRIBUTE CHECK_LICENSE_TYPE OF template_design_MINIMAL_DMA_0_0_arch : ARCHITECTURE IS "template_design_MINIMAL_DMA_0_0,MINIMAL_DMA_v1_0,{}";
  ATTRIBUTE X_INTERFACE_INFO : STRING;
  ATTRIBUTE X_INTERFACE_INFO OF out_data: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_out data";
  ATTRIBUTE X_INTERFACE_INFO OF out_valid: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_out valid";
  ATTRIBUTE X_INTERFACE_INFO OF out_last: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_out last";
  ATTRIBUTE X_INTERFACE_INFO OF out_ready: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_out ready";
  ATTRIBUTE X_INTERFACE_INFO OF in_data: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_in data";
  ATTRIBUTE X_INTERFACE_INFO OF in_valid: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_in valid";
  ATTRIBUTE X_INTERFACE_INFO OF in_last: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_in last";
  ATTRIBUTE X_INTERFACE_INFO OF in_ready: SIGNAL IS "fau.de:user:my_data_stream:1.0 data_in ready";
  ATTRIBUTE X_INTERFACE_INFO OF r_addr: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_addr";
  ATTRIBUTE X_INTERFACE_INFO OF r_len: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_len";
  ATTRIBUTE X_INTERFACE_INFO OF r_valid: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_valid";
  ATTRIBUTE X_INTERFACE_INFO OF r_ready: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_ready";
  ATTRIBUTE X_INTERFACE_INFO OF r_compl: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control r_compl";
  ATTRIBUTE X_INTERFACE_INFO OF w_addr: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_addr";
  ATTRIBUTE X_INTERFACE_INFO OF w_len: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_len";
  ATTRIBUTE X_INTERFACE_INFO OF w_valid: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_valid";
  ATTRIBUTE X_INTERFACE_INFO OF w_ready: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_ready";
  ATTRIBUTE X_INTERFACE_INFO OF w_compl: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control w_compl";
  ATTRIBUTE X_INTERFACE_INFO OF rst: SIGNAL IS "fau.de:user:minimal_dma_control:1.0 dma_control rst";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_aclk: SIGNAL IS "xilinx.com:signal:clock:1.0 M_AXI_CLK CLK";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_aresetn: SIGNAL IS "xilinx.com:signal:reset:1.0 M_AXI_RST RST";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awaddr: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWADDR";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awlen: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWLEN";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awsize: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWSIZE";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awburst: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWBURST";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awlock: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWLOCK";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awcache: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWCACHE";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awprot: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWPROT";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awqos: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWQOS";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awuser: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWUSER";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWVALID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_awready: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI AWREADY";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_wdata: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI WDATA";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_wstrb: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI WSTRB";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_wlast: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI WLAST";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_wuser: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI WUSER";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_wvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI WVALID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_wready: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI WREADY";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_bid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI BID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_bresp: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI BRESP";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_buser: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI BUSER";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_bvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI BVALID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_bready: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI BREADY";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_araddr: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARADDR";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arlen: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARLEN";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arsize: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARSIZE";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arburst: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARBURST";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arlock: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARLOCK";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arcache: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARCACHE";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arprot: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARPROT";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arqos: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARQOS";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_aruser: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARUSER";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARVALID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_arready: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI ARREADY";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_rid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_rdata: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RDATA";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_rresp: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RRESP";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_rlast: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RLAST";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_ruser: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RUSER";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_rvalid: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RVALID";
  ATTRIBUTE X_INTERFACE_INFO OF m_axi_rready: SIGNAL IS "xilinx.com:interface:aximm:1.0 M_AXI RREADY";
BEGIN
  U0 : MINIMAL_DMA_v1_0
    GENERIC MAP (
      C_M_AXI_BURST_LEN => 16,
      C_M_AXI_ID_WIDTH => 1,
      C_M_AXI_ADDR_WIDTH => 32,
      C_M_AXI_DATA_WIDTH => 32,
      C_M_AXI_AWUSER_WIDTH => 1,
      C_M_AXI_ARUSER_WIDTH => 1,
      C_M_AXI_WUSER_WIDTH => 1,
      C_M_AXI_RUSER_WIDTH => 1,
      C_M_AXI_BUSER_WIDTH => 1,
      LEN_WIDTH => 26,
      ISSUE_DEPTH => 2
    )
    PORT MAP (
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
      m_axi_aclk => m_axi_aclk,
      m_axi_aresetn => m_axi_aresetn,
      m_axi_awid => m_axi_awid,
      m_axi_awaddr => m_axi_awaddr,
      m_axi_awlen => m_axi_awlen,
      m_axi_awsize => m_axi_awsize,
      m_axi_awburst => m_axi_awburst,
      m_axi_awlock => m_axi_awlock,
      m_axi_awcache => m_axi_awcache,
      m_axi_awprot => m_axi_awprot,
      m_axi_awqos => m_axi_awqos,
      m_axi_awuser => m_axi_awuser,
      m_axi_awvalid => m_axi_awvalid,
      m_axi_awready => m_axi_awready,
      m_axi_wdata => m_axi_wdata,
      m_axi_wstrb => m_axi_wstrb,
      m_axi_wlast => m_axi_wlast,
      m_axi_wuser => m_axi_wuser,
      m_axi_wvalid => m_axi_wvalid,
      m_axi_wready => m_axi_wready,
      m_axi_bid => m_axi_bid,
      m_axi_bresp => m_axi_bresp,
      m_axi_buser => m_axi_buser,
      m_axi_bvalid => m_axi_bvalid,
      m_axi_bready => m_axi_bready,
      m_axi_arid => m_axi_arid,
      m_axi_araddr => m_axi_araddr,
      m_axi_arlen => m_axi_arlen,
      m_axi_arsize => m_axi_arsize,
      m_axi_arburst => m_axi_arburst,
      m_axi_arlock => m_axi_arlock,
      m_axi_arcache => m_axi_arcache,
      m_axi_arprot => m_axi_arprot,
      m_axi_arqos => m_axi_arqos,
      m_axi_aruser => m_axi_aruser,
      m_axi_arvalid => m_axi_arvalid,
      m_axi_arready => m_axi_arready,
      m_axi_rid => m_axi_rid,
      m_axi_rdata => m_axi_rdata,
      m_axi_rresp => m_axi_rresp,
      m_axi_rlast => m_axi_rlast,
      m_axi_ruser => m_axi_ruser,
      m_axi_rvalid => m_axi_rvalid,
      m_axi_rready => m_axi_rready
    );
END template_design_MINIMAL_DMA_0_0_arch;
