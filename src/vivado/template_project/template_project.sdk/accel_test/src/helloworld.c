/******************************************************************************
 *
 * Copyright (C) 2009 - 2014 Xilinx, Inc.  All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * Use of the Software is limited solely to applications:
 * (a) running on a Xilinx device, or
 * (b) that interact with a Xilinx device through a bus or interconnect.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * XILINX  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
 * OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Except as contained in this notice, the name of the Xilinx shall not be used
 * in advertising or otherwise to promote the sale, use or other dealings in
 * this Software without prior written authorization from Xilinx.
 *
 ******************************************************************************/

/*
 * helloworld.c: simple test application
 *
 * This application configures UART 16550 to baud rate 9600.
 * PS7 UART (Zynq) is not initialized by this application, since
 * bootrom/bsp configures it to baud rate 115200
 *
 * ------------------------------------------------
 * | UART TYPE   BAUD RATE                        |
 * ------------------------------------------------
 *   uartns550   9600
 *   uartlite    Configurable only in HW design
 *   ps7_uart    115200 (configured by bootrom/bsp)
 */

#include <stdio.h>
#include "platform.h"
#include "xparameters.h"
#include "MINIMAL_DMA_CONTROL.h"
#include "stdlib.h"
#include "xil_cache.h"


void rst_dma(struct dma_control *dev) { dev->global_control |= RST;}

int main()
{
	init_platform();

	// printf("Start Accelerator Test ...\n");

	int32_t *synthetic_image_in = malloc(sizeof(int32_t) * 100);
	int32_t *synthetic_image_out = malloc(sizeof(int32_t) * 100);
	struct dma_control *dma = (struct dma_control *) XPAR_MINIMAL_DMA_CONTROL_0_S_AXI_BASEADDR;
	int i;

	//Xil_DCacheDisable();

	for(i=0; i< 10 ;++i){
		synthetic_image_in[i] = i;
		synthetic_image_out[i] = 0;}

	while(1){
	rst_dma(dma);

	start_dma_to_dev(synthetic_image_in, 40, dma);
	wait_end_dma_to_dev(dma);

	start_dma_from_dev(synthetic_image_out, 40, dma);
	wait_end_dma_from_dev(synthetic_image_out, 40, dma);

	//    printf("Accelerator Results ... \n");
	//    int i = 0;
	//    for (i=0; i<10; ++i) {
	//		printf("%d: %d\n", i, (int)synthetic_image[i]);
	//	}
}
	cleanup_platform();
	return 0;
}