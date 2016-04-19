// Copyright 1986-2015 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2015.2 (lin64) Build 1266856 Fri Jun 26 16:35:25 MDT 2015
// Date        : Tue Apr 19 15:16:07 2016
// Host        : codesigns45 running 64-bit Ubuntu 14.04.4 LTS
// Command     : write_verilog -force -mode synth_stub
//               /mnt/studproj/ebensberger/vhdl-sejits/src/vivado/template_project/template_project.srcs/sources_1/ip/fifo_generator_0/fifo_generator_0_stub.v
// Design      : fifo_generator_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7z020clg484-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* x_core_info = "fifo_generator_v12_0,Vivado 2015.2" *)
module fifo_generator_0(clk, rst, din, wr_en, rd_en, dout, full, empty, valid, prog_empty)
/* synthesis syn_black_box black_box_pad_pin="clk,rst,din[8:0],wr_en,rd_en,dout[8:0],full,empty,valid,prog_empty" */;
  input clk;
  input rst;
  input [8:0]din;
  input wr_en;
  input rd_en;
  output [8:0]dout;
  output full;
  output empty;
  output valid;
  output prog_empty;
endmodule
