

/***************************** Include Files *******************************/
#include "MINIMAL_DMA_CONTROL.h"
#include "xil_cache.h"


/************************** Function Definitions ***************************/


int start_dma_transfer(struct dma_channel * chan) {

	while (chan->ctrl_reg & START) {
		;
	}

	chan->ctrl_reg |= START;
	return 0;
}

int wait_end_dma_transfer(struct dma_channel * chan) {
	while (!(chan->ctrl_reg & DONE)) {
		;
	}
	return chan->ctrl_reg & (DONE | READY);
}

int start_dma_to_dev(void * buffer, u32 len, struct dma_control * dev) {
	len = (len + 3) & ~3;

	Xil_DCacheFlushRange((u32) buffer, len);

	dev->read.addr = buffer;
	dev->read.len = len / 4 - 1;

	return start_dma_transfer(&dev->read);
}

int wait_end_dma_to_dev(struct dma_control * dev) {
	return wait_end_dma_transfer(&dev->read);
}

int start_dma_from_dev(void * buffer, u32 len, struct dma_control * dev) {
	int returnval = 0;
	len = (len + 3) & ~3;

	dev->write.addr = buffer;
	dev->write.len = len / 4 - 1;

	return  start_dma_transfer(&dev->write);
}

int wait_end_dma_from_dev(void * buffer, u32 len, struct dma_control * dev) {
	int returnval = wait_end_dma_transfer(&dev->write);
	Xil_DCacheInvalidateRange((u32) buffer, len);
	return returnval;
}