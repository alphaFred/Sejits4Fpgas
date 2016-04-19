
#ifndef MINIMAL_DMA_CONTROL_H
#define MINIMAL_DMA_CONTROL_H


/****************** Include Files ********************/
#include "xil_types.h"

enum dma_ctrl {
	START = 1,
	SUPPRESS_LAST = 2,
	READY = (1 << 8),
	DONE = (1 << 9),
	INT_EN = (1 << 16),
	CLEAR = 0xf0000
};

struct dma_channel {
	volatile u32* addr;
	volatile u32 len;
	volatile enum dma_ctrl ctrl_reg;
};

struct dma_control {
	struct dma_channel read;
	u32 dummy;
	struct dma_channel write;
	volatile enum int_ctrl {
		GLOBAL_INT_EN = 1,
		INT_TEST = (1 << 24),
		RST = (1 << 8),
		GCLEAR = 0xf0000
	} global_control;
};





int start_dma_transfer(struct dma_channel * chan);
int wait_end_dma_transfer(struct dma_channel * chan);

int start_dma_to_dev(void * buffer, u32 len, struct dma_control * dev);
int wait_end_dma_to_dev(struct dma_control * dev);

int start_dma_from_dev(void * buffer, u32 len, struct dma_control * dev);
int wait_end_dma_from_dev(void * buffer, u32 len, struct dma_control * dev);

int rst_dma(struct dma_control *dev);

#endif // MINIMAL_DMA_CONTROL_H
