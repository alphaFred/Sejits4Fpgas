#include <fstream>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <cstdio>
#include <cerrno>

#include <stdlib.h>
#include <unistd.h>
#include <time.h>

extern "C" void process1d(unsigned int* img, unsigned int len){
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }
    // process image
    printf("write 1d: %d\n", write(device_fd, img, len * sizeof(unsigned int)));
    printf("read 1d: %d\n", read(device_fd, img, len * sizeof(unsigned int)));
    // clean up
    ::close(device_fd);
}

/*
extern "C" void process_img(unsigned int* input, unsigned int len){
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    unsigned int input_data_width = 64;

    if (len <= input_data_width) {
        write(device_fd, input, len * sizeof(unsigned int));
        read(device_fd, input, len * sizeof(unsigned int));
    } else {
        // process image
        unsigned int idx = 0;
        unsigned int diff = len%input_data_width;
        for (idx=0; idx<len-diff; idx+=input_data_width){
            write(device_fd, input + idx, input_data_width * sizeof(unsigned int));
        }
        if (diff != 0){
            write(device_fd, input + idx, diff * sizeof(unsigned int));
        }
        //
        for (idx=0; idx<len-diff; idx+=input_data_width){
            read(device_fd, input + idx, input_data_width * sizeof(unsigned int));
        }
        if (diff != 0){
            read(device_fd, input + idx, diff * sizeof(unsigned int));
        }
    }
    // clean up
    ::close(device_fd);
}

extern "C" void process_img(unsigned int* input, unsigned int len, unsigned int width, unsigned int input_width){
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    unsigned int img_width = width;
    unsigned int input_data_width = input_width;

    if (len <= input_data_width) {
        write(device_fd, input, len * sizeof(unsigned int));
        read(device_fd, input, len * sizeof(unsigned int));
    } else {
        // process image
        unsigned int idx = 0;
        unsigned int read_idx = 0;
        unsigned int diff = len%input_data_width;
        for (idx=0; idx<len-diff; idx+=input_data_width){
            write(device_fd, input + idx, input_data_width * sizeof(unsigned int));
            if (idx >= 2*img_width) {
            	read(device_fd, input + read_idx, input_data_width * sizeof(unsigned int));
            	read_idx+=input_data_width;
            }
        }
        //
        read(device_fd, input + read_idx, input_data_width * sizeof(unsigned int));
        //
        if (diff != 0){
            write(device_fd, input + idx, diff * sizeof(unsigned int));
	    read(device_fd, input + idx, diff * sizeof(unsigned int));
        }
    }
    // clean up
    ::close(device_fd);
}
*/

extern "C" void write_img(unsigned int* input, unsigned int len, unsigned int write_nbit) {
    // get device
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    unsigned int write_cnt = 0;
    unsigned int diff = len%write_nbit;

    for (write_cnt=0; write_cnt<len-diff; write_cnt += write_nbit) {
        write(device_fd, input + write_cnt, write_nbit * sizeof(unsigned int));
    }

    if (diff!=0) {
        write(device_fd, input + write_cnt, diff * sizeof(unsigned int));
    }
    ::close(device_fd);
}

extern "C" void read_img(unsigned int* output, unsigned int len, unsigned int read_nbit) {
    // get device
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    unsigned int read_cnt = 0;
    unsigned int diff = len%read_nbit;

    for (read_cnt=0; read_cnt<len-diff; read_cnt += read_nbit) {
        read(device_fd, output + read_cnt, read_nbit * sizeof(unsigned int));
    }

    if (diff!=0) {
        read(device_fd, output + read_cnt, diff * sizeof(unsigned int));
    }
    ::close(device_fd);
}

#define IDLE 0
#define WRITE 1
#define WRITE_FINISHED 2

#define READ 1
#define READ_FINISHED 2


extern "C" void process_img(unsigned int* input, unsigned int len, unsigned int width, unsigned int input_width){
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    unsigned int write_cnt = 0;
    unsigned int read_cnt = 0;
    unsigned int input_data_width = input_width;

    unsigned int write_state = IDLE;
    unsigned int read_state = IDLE;

    unsigned int processing = 1;
    unsigned int diff = len%input_data_width;

    while(processing){
        switch(write_state){
            case IDLE:
                write_state = WRITE;
                write_cnt = 0;
                break;
            case WRITE:
                if (write_cnt < len-diff) {
                    write(device_fd, input + write_cnt, input_data_width * sizeof(unsigned int));
                    write_cnt += input_data_width;
                } else {
                    if (diff != 0) {
                        write(device_fd, input + write_cnt, diff * sizeof(unsigned int));
                    }
                    write_state = WRITE_FINISHED;
                }
                break;
            case WRITE_FINISHED:
                write_state = WRITE_FINISHED;
                break;
            default:
                break;
        }
        switch(read_state){
            case IDLE:
                if (write_cnt < (8*width)) {
                    read_state = IDLE;
                } else {
                    read_state = READ;
                }
                read_cnt = 0;
                break;
            case READ:
                if (read_cnt < len-diff) {
                    read(device_fd, input + read_cnt, input_data_width * sizeof(unsigned int));
                    read_cnt += input_data_width;
                } else {
                    if (diff != 0) {
                        read(device_fd, input + read_cnt, diff * sizeof(unsigned int));
                    }
                    read_state = READ_FINISHED;
                }
                break;
            case READ_FINISHED:
                processing = 0;
                read_state = READ_FINISHED;
                break;
            default:
                break;
        }
    }
    // clean up
    ::close(device_fd);
}


extern "C" void process1d_img(unsigned int* img, unsigned int len){
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    unsigned int input_data_width = 16;

    if (len <= input_data_width) {
        write(device_fd, img, len * sizeof(unsigned int));
        read(device_fd, img, len * sizeof(unsigned int));
    } else {
        // process image
        unsigned int idx = 0;
        unsigned int diff = len%input_data_width;
        for (idx=0; idx<len-diff; idx+=input_data_width){
            write(device_fd, img + idx, input_data_width * sizeof(unsigned int));
            read(device_fd, img + idx, input_data_width * sizeof(unsigned int));
        }
        if (diff != 0){
            write(device_fd, img + idx, diff * sizeof(unsigned int));
            read(device_fd, img + idx, diff * sizeof(unsigned int));
        }
    }
    // clean up
    ::close(device_fd);
}
