# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  set C_S_AXI_DATA_WIDTH [ipgui::add_param $IPINST -name "C_S_AXI_DATA_WIDTH" -parent ${Page_0} -widget comboBox]
  set_property tooltip {Width of S_AXI data bus} ${C_S_AXI_DATA_WIDTH}
  set C_S_AXI_ADDR_WIDTH [ipgui::add_param $IPINST -name "C_S_AXI_ADDR_WIDTH" -parent ${Page_0}]
  set_property tooltip {Width of S_AXI address bus} ${C_S_AXI_ADDR_WIDTH}
  ipgui::add_param $IPINST -name "C_S_AXI_BASEADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S_AXI_HIGHADDR" -parent ${Page_0}

  ipgui::add_param $IPINST -name "DMA_ADDR_WIDTH" -widget comboBox
  ipgui::add_param $IPINST -name "IO_DATA_WIDTH" -widget comboBox
  ipgui::add_param $IPINST -name "DMA_LEN_WIDTH"
  set GEN_DONE [ipgui::add_param $IPINST -name "GEN_DONE"]
  set_property tooltip {Generates a DONE signal even without having seen the last from s_axis} ${GEN_DONE}

}

proc update_PARAM_VALUE.DMA_ADDR_WIDTH { PARAM_VALUE.DMA_ADDR_WIDTH } {
	# Procedure called to update DMA_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.DMA_ADDR_WIDTH { PARAM_VALUE.DMA_ADDR_WIDTH } {
	# Procedure called to validate DMA_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.DMA_LEN_WIDTH { PARAM_VALUE.DMA_LEN_WIDTH } {
	# Procedure called to update DMA_LEN_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.DMA_LEN_WIDTH { PARAM_VALUE.DMA_LEN_WIDTH } {
	# Procedure called to validate DMA_LEN_WIDTH
	return true
}

proc update_PARAM_VALUE.GEN_DONE { PARAM_VALUE.GEN_DONE } {
	# Procedure called to update GEN_DONE when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.GEN_DONE { PARAM_VALUE.GEN_DONE } {
	# Procedure called to validate GEN_DONE
	return true
}

proc update_PARAM_VALUE.IO_DATA_WIDTH { PARAM_VALUE.IO_DATA_WIDTH } {
	# Procedure called to update IO_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.IO_DATA_WIDTH { PARAM_VALUE.IO_DATA_WIDTH } {
	# Procedure called to validate IO_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S_AXI_DATA_WIDTH { PARAM_VALUE.C_S_AXI_DATA_WIDTH } {
	# Procedure called to update C_S_AXI_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S_AXI_DATA_WIDTH { PARAM_VALUE.C_S_AXI_DATA_WIDTH } {
	# Procedure called to validate C_S_AXI_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S_AXI_ADDR_WIDTH { PARAM_VALUE.C_S_AXI_ADDR_WIDTH } {
	# Procedure called to update C_S_AXI_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S_AXI_ADDR_WIDTH { PARAM_VALUE.C_S_AXI_ADDR_WIDTH } {
	# Procedure called to validate C_S_AXI_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S_AXI_BASEADDR { PARAM_VALUE.C_S_AXI_BASEADDR } {
	# Procedure called to update C_S_AXI_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S_AXI_BASEADDR { PARAM_VALUE.C_S_AXI_BASEADDR } {
	# Procedure called to validate C_S_AXI_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_S_AXI_HIGHADDR { PARAM_VALUE.C_S_AXI_HIGHADDR } {
	# Procedure called to update C_S_AXI_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S_AXI_HIGHADDR { PARAM_VALUE.C_S_AXI_HIGHADDR } {
	# Procedure called to validate C_S_AXI_HIGHADDR
	return true
}


proc update_MODELPARAM_VALUE.C_S_AXI_DATA_WIDTH { MODELPARAM_VALUE.C_S_AXI_DATA_WIDTH PARAM_VALUE.C_S_AXI_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S_AXI_DATA_WIDTH}] ${MODELPARAM_VALUE.C_S_AXI_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S_AXI_ADDR_WIDTH { MODELPARAM_VALUE.C_S_AXI_ADDR_WIDTH PARAM_VALUE.C_S_AXI_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S_AXI_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_S_AXI_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.DMA_ADDR_WIDTH { MODELPARAM_VALUE.DMA_ADDR_WIDTH PARAM_VALUE.DMA_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.DMA_ADDR_WIDTH}] ${MODELPARAM_VALUE.DMA_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.DMA_LEN_WIDTH { MODELPARAM_VALUE.DMA_LEN_WIDTH PARAM_VALUE.DMA_LEN_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.DMA_LEN_WIDTH}] ${MODELPARAM_VALUE.DMA_LEN_WIDTH}
}

proc update_MODELPARAM_VALUE.IO_DATA_WIDTH { MODELPARAM_VALUE.IO_DATA_WIDTH PARAM_VALUE.IO_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.IO_DATA_WIDTH}] ${MODELPARAM_VALUE.IO_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.GEN_DONE { MODELPARAM_VALUE.GEN_DONE PARAM_VALUE.GEN_DONE } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.GEN_DONE}] ${MODELPARAM_VALUE.GEN_DONE}
}

