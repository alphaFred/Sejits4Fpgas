#!/bin/sh -f
xv_path="/scratch-local/opt/Xilinx/Vivado/2014.4"
ExecStep()
{
"$@"
RETVAL=$?
if [ $RETVAL -ne 0 ]
then
exit $RETVAL
fi
}
ExecStep $xv_path/bin/xsim tb_minimal_dma_behav -key {Behavioral:sim_1:Functional:tb_minimal_dma} -tclbatch tb_minimal_dma.tcl -log simulate.log
