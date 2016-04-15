
################################################################
# This is a generated script based on design: template_design
#
# Though there are limitations about the generated script,
# the main purpose of this utility is to make learning
# IP Integrator Tcl commands easier.
################################################################

################################################################
# Check if script is running in correct Vivado version.
################################################################
set scripts_vivado_version 2015.2
set current_vivado_version [version -short]

if { [string first $scripts_vivado_version $current_vivado_version] == -1 } {
   puts ""
   puts "ERROR: This script was generated using Vivado <$scripts_vivado_version> and is being run in <$current_vivado_version> of Vivado. Please run the script in Vivado <$scripts_vivado_version> then open the design in Vivado <$current_vivado_version>. Upgrade the design by running \"Tools => Report => Report IP Status...\", then run write_bd_tcl to create an updated script."

   return 1
}

################################################################
# START
################################################################

# To test this script, run the following commands from Vivado Tcl console:
# source template_design_script.tcl

# If you do not already have a project created,
# you can create a project using the following command:
#    create_project project_1 myproj -part xc7z020clg484-1
#    set_property BOARD_PART em.avnet.com:zed:part0:1.3 [current_project]

# CHECKING IF PROJECT EXISTS
if { [get_projects -quiet] eq "" } {
   puts "ERROR: Please open or create a project!"
   return 1
}



# CHANGE DESIGN NAME HERE
set design_name template_design

# This script was generated for a remote BD.
set str_bd_folder /home/philipp/University/M4/Masterthesis/src/vhdl-sejits/src/vivado/template_project/template_project.srcs/sources_1/bd
set str_bd_filepath ${str_bd_folder}/${design_name}/${design_name}.bd

# Check if remote design exists on disk
if { [file exists $str_bd_filepath ] == 1 } {
   puts "ERROR: The remote BD file path <$str_bd_filepath> already exists!"
   return 1
}

# Check if design exists in memory
set list_existing_designs [get_bd_designs -quiet $design_name]
if { $list_existing_designs ne "" } {
   puts "ERROR: The design <$design_name> already exists in this project!"
   puts "ERROR: Will not create the remote BD <$design_name> at the folder <$str_bd_folder>."

   return 1
}

# Check if design exists on disk within project
set list_existing_designs [get_files */${design_name}.bd]
if { $list_existing_designs ne "" } {
   puts "ERROR: The design <$design_name> already exists in this project at location:"
   puts "   $list_existing_designs"
   puts "ERROR: Will not create the remote BD <$design_name> at the folder <$str_bd_folder>."

   return 1
}

# Now can create the remote BD
create_bd_design -dir $str_bd_folder $design_name
current_bd_design $design_name

##################################################################
# DESIGN PROCs
##################################################################



# Procedure to create entire design; Provide argument to make
# procedure reusable. If parentCell is "", will use root.
proc create_root_design { parentCell } {

  if { $parentCell eq "" } {
     set parentCell [get_bd_cells /]
  }

  # Get object for parentCell
  set parentObj [get_bd_cells $parentCell]
  if { $parentObj == "" } {
     puts "ERROR: Unable to find parent cell <$parentCell>!"
     return
  }

  # Make sure parentObj is hier blk
  set parentType [get_property TYPE $parentObj]
  if { $parentType ne "hier" } {
     puts "ERROR: Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."
     return
  }

  # Save current instance; Restore later
  set oldCurInst [current_bd_instance .]

  # Set parent object as current
  current_bd_instance $parentObj


  # Create interface ports
  set DDR [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:ddrx_rtl:1.0 DDR ]
  set FIXED_IO [ create_bd_intf_port -mode Master -vlnv xilinx.com:display_processing_system7:fixedio_rtl:1.0 FIXED_IO ]
  set m_axis [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:axis_rtl:1.0 m_axis ]
  set_property -dict [ list CONFIG.CLK_DOMAIN {template_design_processing_system7_0_0_FCLK_CLK0}  ] $m_axis
  set s_axis [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:axis_rtl:1.0 s_axis ]
  set_property -dict [ list CONFIG.CLK_DOMAIN {template_design_processing_system7_0_0_FCLK_CLK0} CONFIG.HAS_TKEEP {0} CONFIG.HAS_TLAST {1} CONFIG.HAS_TREADY {1} CONFIG.HAS_TSTRB {0} CONFIG.LAYERED_METADATA {undef} CONFIG.PHASE {0.000} CONFIG.TDATA_NUM_BYTES {4} CONFIG.TDEST_WIDTH {0} CONFIG.TID_WIDTH {0} CONFIG.TUSER_WIDTH {0}  ] $s_axis

  # Create ports
  set CLK [ create_bd_port -dir O -type clk CLK ]
  set_property -dict [ list CONFIG.ASSOCIATED_BUSIF {s_axis:m_axis}  ] $CLK
  set RST [ create_bd_port -dir O -type rst RST ]

  # Create instance: MINIMAL_DMA_0, and set properties
  set MINIMAL_DMA_0 [ create_bd_cell -type ip -vlnv fau.de:user:MINIMAL_DMA:1.0 MINIMAL_DMA_0 ]
  set_property -dict [ list CONFIG.C_M_AXI_BURST_LEN {64} CONFIG.LEN_WIDTH {20}  ] $MINIMAL_DMA_0

  # Create instance: MINIMAL_DMA_CONTROL_0, and set properties
  set MINIMAL_DMA_CONTROL_0 [ create_bd_cell -type ip -vlnv user.org:user:MINIMAL_DMA_CONTROL:1.0 MINIMAL_DMA_CONTROL_0 ]
  set_property -dict [ list CONFIG.DMA_LEN_WIDTH {20} CONFIG.GEN_DONE {true}  ] $MINIMAL_DMA_CONTROL_0

  # Create instance: axi_mem_intercon, and set properties
  set axi_mem_intercon [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_mem_intercon ]
  set_property -dict [ list CONFIG.NUM_MI {1} CONFIG.NUM_SI {1}  ] $axi_mem_intercon

  # Create instance: processing_system7_0, and set properties
  set processing_system7_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0 ]
  set_property -dict [ list CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {32} CONFIG.PCW_USE_S_AXI_HP0 {1} CONFIG.preset {ZedBoard}  ] $processing_system7_0

  # Create instance: processing_system7_0_axi_periph, and set properties
  set processing_system7_0_axi_periph [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 processing_system7_0_axi_periph ]
  set_property -dict [ list CONFIG.NUM_MI {1}  ] $processing_system7_0_axi_periph

  # Create instance: rst_processing_system7_0_102M, and set properties
  set rst_processing_system7_0_102M [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 rst_processing_system7_0_102M ]

  # Create interface connections
  connect_bd_intf_net -intf_net MINIMAL_DMA_0_M_AXI [get_bd_intf_pins MINIMAL_DMA_0/M_AXI] [get_bd_intf_pins axi_mem_intercon/S00_AXI]
  connect_bd_intf_net -intf_net MINIMAL_DMA_0_data_out [get_bd_intf_pins MINIMAL_DMA_0/data_out] [get_bd_intf_pins MINIMAL_DMA_CONTROL_0/in_data]
  connect_bd_intf_net -intf_net MINIMAL_DMA_CONTROL_0_dma_control [get_bd_intf_pins MINIMAL_DMA_0/dma_control] [get_bd_intf_pins MINIMAL_DMA_CONTROL_0/dma_control]
  connect_bd_intf_net -intf_net MINIMAL_DMA_CONTROL_0_m_axis [get_bd_intf_ports m_axis] [get_bd_intf_pins MINIMAL_DMA_CONTROL_0/m_axis]
  connect_bd_intf_net -intf_net MINIMAL_DMA_CONTROL_0_out_data [get_bd_intf_pins MINIMAL_DMA_0/data_in] [get_bd_intf_pins MINIMAL_DMA_CONTROL_0/out_data]
  connect_bd_intf_net -intf_net axi_mem_intercon_M00_AXI [get_bd_intf_pins axi_mem_intercon/M00_AXI] [get_bd_intf_pins processing_system7_0/S_AXI_HP0]
  connect_bd_intf_net -intf_net processing_system7_0_DDR [get_bd_intf_ports DDR] [get_bd_intf_pins processing_system7_0/DDR]
  connect_bd_intf_net -intf_net processing_system7_0_FIXED_IO [get_bd_intf_ports FIXED_IO] [get_bd_intf_pins processing_system7_0/FIXED_IO]
  connect_bd_intf_net -intf_net processing_system7_0_M_AXI_GP0 [get_bd_intf_pins processing_system7_0/M_AXI_GP0] [get_bd_intf_pins processing_system7_0_axi_periph/S00_AXI]
  connect_bd_intf_net -intf_net processing_system7_0_axi_periph_M00_AXI [get_bd_intf_pins MINIMAL_DMA_CONTROL_0/S_AXI] [get_bd_intf_pins processing_system7_0_axi_periph/M00_AXI]
  connect_bd_intf_net -intf_net s_axis_1 [get_bd_intf_ports s_axis] [get_bd_intf_pins MINIMAL_DMA_CONTROL_0/s_axis]

  # Create port connections
  connect_bd_net -net MINIMAL_DMA_CONTROL_0_axis_rst [get_bd_ports RST] [get_bd_pins MINIMAL_DMA_CONTROL_0/axis_rst]
  connect_bd_net -net processing_system7_0_FCLK_CLK0 [get_bd_ports CLK] [get_bd_pins MINIMAL_DMA_0/m_axi_aclk] [get_bd_pins MINIMAL_DMA_CONTROL_0/s_axi_aclk] [get_bd_pins axi_mem_intercon/ACLK] [get_bd_pins axi_mem_intercon/M00_ACLK] [get_bd_pins axi_mem_intercon/S00_ACLK] [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins processing_system7_0/M_AXI_GP0_ACLK] [get_bd_pins processing_system7_0/S_AXI_HP0_ACLK] [get_bd_pins processing_system7_0_axi_periph/ACLK] [get_bd_pins processing_system7_0_axi_periph/M00_ACLK] [get_bd_pins processing_system7_0_axi_periph/S00_ACLK] [get_bd_pins rst_processing_system7_0_102M/slowest_sync_clk]
  connect_bd_net -net processing_system7_0_FCLK_RESET0_N [get_bd_pins processing_system7_0/FCLK_RESET0_N] [get_bd_pins rst_processing_system7_0_102M/ext_reset_in]
  connect_bd_net -net rst_processing_system7_0_102M_interconnect_aresetn [get_bd_pins axi_mem_intercon/ARESETN] [get_bd_pins processing_system7_0_axi_periph/ARESETN] [get_bd_pins rst_processing_system7_0_102M/interconnect_aresetn]
  connect_bd_net -net rst_processing_system7_0_102M_peripheral_aresetn [get_bd_pins MINIMAL_DMA_0/m_axi_aresetn] [get_bd_pins MINIMAL_DMA_CONTROL_0/s_axi_aresetn] [get_bd_pins axi_mem_intercon/M00_ARESETN] [get_bd_pins axi_mem_intercon/S00_ARESETN] [get_bd_pins processing_system7_0_axi_periph/M00_ARESETN] [get_bd_pins processing_system7_0_axi_periph/S00_ARESETN] [get_bd_pins rst_processing_system7_0_102M/peripheral_aresetn]

  # Create address segments
  create_bd_addr_seg -range 0x20000000 -offset 0x0 [get_bd_addr_spaces MINIMAL_DMA_0/M_AXI] [get_bd_addr_segs processing_system7_0/S_AXI_HP0/HP0_DDR_LOWOCM] SEG_processing_system7_0_HP0_DDR_LOWOCM
  create_bd_addr_seg -range 0x10000 -offset 0x43C00000 [get_bd_addr_spaces processing_system7_0/Data] [get_bd_addr_segs MINIMAL_DMA_CONTROL_0/S_AXI/S_AXI_reg] SEG_MINIMAL_DMA_CONTROL_0_S_AXI_reg
  

  # Restore current instance
  current_bd_instance $oldCurInst

  save_bd_design
}
# End of create_root_design()


##################################################################
# MAIN FLOW
##################################################################

create_root_design ""


