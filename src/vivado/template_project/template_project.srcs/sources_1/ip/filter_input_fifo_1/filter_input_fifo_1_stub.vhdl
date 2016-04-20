-- Copyright 1986-2015 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2015.2 (lin64) Build 1266856 Fri Jun 26 16:35:25 MDT 2015
-- Date        : Wed Apr 20 11:47:44 2016
-- Host        : philipp-ThinkPad-X250 running 64-bit Ubuntu 15.04
-- Command     : write_vhdl -force -mode synth_stub
--               /home/philipp/University/M4/Masterthesis/src/vhdl-sejits/src/vivado/template_project/template_project.srcs/sources_1/ip/filter_input_fifo_1/filter_input_fifo_1_stub.vhdl
-- Design      : filter_input_fifo_1
-- Purpose     : Stub declaration of top-level module interface
-- Device      : xc7z020clg484-1
-- --------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity filter_input_fifo_1 is
  Port ( 
    clk : in STD_LOGIC;
    rst : in STD_LOGIC;
    din : in STD_LOGIC_VECTOR ( 7 downto 0 );
    wr_en : in STD_LOGIC;
    rd_en : in STD_LOGIC;
    dout : out STD_LOGIC_VECTOR ( 7 downto 0 );
    full : out STD_LOGIC;
    empty : out STD_LOGIC;
    data_count : out STD_LOGIC_VECTOR ( 11 downto 0 )
  );

end filter_input_fifo_1;

architecture stub of filter_input_fifo_1 is
attribute syn_black_box : boolean;
attribute black_box_pad_pin : string;
attribute syn_black_box of stub : architecture is true;
attribute black_box_pad_pin of stub : architecture is "clk,rst,din[7:0],wr_en,rd_en,dout[7:0],full,empty,data_count[11:0]";
attribute x_core_info : string;
attribute x_core_info of stub : architecture is "fifo_generator_v12_0,Vivado 2015.2";
begin
end;
