#!/bin/sh -f
xv_path="/home/philipp/Xilinx/Vivado/2015.2"
ExecStep()
{
"$@"
RETVAL=$?
if [ $RETVAL -ne 0 ]
then
exit $RETVAL
fi
}
ExecStep $xv_path/bin/xelab -wto feff3a5fdbc14a3c8ac87760cb7d13f9 -m64 --debug typical --relax --mt 8 --include "../../../template_project.srcs/sources_1/bd/template_design/ip/template_design_processing_system7_0_0" --include "../../../template_project.srcs/sources_1/ipshared/xilinx.com/axi_infrastructure_v1_1/cf21a66f/hdl/verilog" --include "../../../template_project.srcs/sources_1/ipshared/xilinx.com/axis_infrastructure_v1_1/3897bfff/hdl/verilog" --include "../../../template_project.srcs/sources_1/ipshared/xilinx.com/processing_system7_bfm_v2_0/adcdcea3/hdl" -L xil_defaultlib -L lib_cdc_v1_0 -L proc_sys_reset_v5_0 -L axis_infrastructure_v1_1 -L axis_data_fifo_v1_1 -L fifo_generator_v12_0 -L util_vector_logic_v2_0 -L xbip_utils_v3_0 -L c_reg_fd_v12_0 -L xbip_dsp48_wrapper_v3_0 -L xbip_pipe_v3_0 -L xbip_dsp48_addsub_v3_0 -L xbip_addsub_v3_0 -L c_addsub_v12_0 -L axis_register_slice_v1_1 -L generic_baseblocks_v2_1 -L axi_data_fifo_v2_1 -L axi_infrastructure_v1_1 -L axi_register_slice_v2_1 -L axi_protocol_converter_v2_1 -L unisims_ver -L unimacro_ver -L secureip --snapshot top_behav xil_defaultlib.top xil_defaultlib.glbl -log elaborate.log
