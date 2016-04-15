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
ExecStep $xv_path/bin/xelab -wto a99397119088487385e9730224509bf8 -m64 --debug typical --relax -L xil_defaultlib -L secureip --snapshot tb_minimal_dma_behav xil_defaultlib.tb_minimal_dma -log elaborate.log
