#include <fstream>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <cstdio>
#include <cerrno>

#include <error.h>

#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>

/*
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
*/



void writeToFpga(int fd, const void *buf, size_t count)
{
    if (write(fd, buf, count) == -1)
    {
        int errsv = errno;

        switch(errsv)
        {
            case EAGAIN:
                perror("fd refers to a file other than a socket is blocking");
                exit(EXIT_FAILURE);
                break;
            case EBADF:
                perror("fd is not a valid file descriptor or is not open for writing");
                exit(EXIT_FAILURE);
                break;
            case EDESTADDRREQ:
                perror("fd refers to a datagram socket for which a peer address has not been set using connect");
                exit(EXIT_FAILURE);
                break;
            case EDQUOT:
                perror("The user's quota of disk blocks on the filesystem containing the file referred to by fd has been exhausted");
                exit(EXIT_FAILURE);
                break;
            case EFAULT:
                perror("buf is outside your accessible address space");
                exit(EXIT_FAILURE);
                break;
            case EFBIG:
                perror("An attempt was made to write a file that exceeds the implementation-defined maximum file size");
                exit(EXIT_FAILURE);
                break;
            case EINTR:
                perror("The call was interrupted by a signal before any data was written");
                exit(EXIT_FAILURE);
                break;
            case EINVAL:
                perror("fd is attached to an object which is unsuitable for writing");
                exit(EXIT_FAILURE);
                break;
            case EIO:
                perror("A low-level I/O error occurred while modifying the inode");
                exit(EXIT_FAILURE);
                break;
            case ENOSPC:
                perror("The device containing the file referred to by fd has no room for the data");
                exit(EXIT_FAILURE);
                break;
            case EPERM:
                perror("The operation was prevented by a file seal");
                exit(EXIT_FAILURE);
                break;
            case EPIPE:
                perror("fd is connected to a pipe or socket whose reading end is closed");
                exit(EXIT_FAILURE);
                break;
            default:
                perror("Unkown error occured while writing to fpga");
                exit(EXIT_FAILURE);
                break;
        }
    }
}

void readFromFpga(int fd, void *buf, size_t count)
{
    if (read(fd, buf, count) == -1)
    {
        int errsv = errno;

        switch(errsv)
        {
            case EAGAIN:
                perror("fd refers to a file other than a socket is blocking");
                exit(EXIT_FAILURE);
                break;
            case EBADF:
                perror("fd is not a valid file descriptor or is not open for writing");
                exit(EXIT_FAILURE);
                break;
            case EDESTADDRREQ:
                perror("fd refers to a datagram socket for which a peer address has not been set using connect");
                exit(EXIT_FAILURE);
                break;
            case EFAULT:
                perror("buf is outside your accessible address space");
                exit(EXIT_FAILURE);
                break;
            case EINTR:
                perror("The call was interrupted by a signal before any data was written");
                exit(EXIT_FAILURE);
                break;
            case EINVAL:
                perror("fd is attached to an object which is unsuitable for writing");
                exit(EXIT_FAILURE);
                break;
            case EIO:
                perror("A low-level I/O error occurred while modifying the inode");
                exit(EXIT_FAILURE);
                break;
            case EISDIR:
                perror("fd refers to a directory");
                exit(EXIT_FAILURE);
                break;
            default:
                perror("Unkown error occured while reading from fpga");
                exit(EXIT_FAILURE);
                break;
        }
    }
}

enum process_control_t
{
   DISABLE=0,
    ENABLE=1, 
};

enum process_state_t
{
    IDLE=10,
    WRITE=20,
    WRITE_FINISHED=25,
    READ=30,
    READ_FINISHED=35
};

// extern "C" void process_img(void* input, uint32_t len, /*uint32_t inptWidth,*/ uint32_t elemSizeInByte)
// {
//     int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
//     // check device_fd
//     if(device_fd == -1)
//     {
//         perror("Error opening iobar for writing");
//         exit(EXIT_FAILURE);
//     }

//     if (elemSizeInByte > sizeof(uint32_t))
//     {
//         perror("Size of input element must not exceed 4 byte!");
//         exit(EXIT_FAILURE);
//     }

//     uint32_t writeOffset = 0;
//     uint32_t readOffset = 0;

//     /*uint32_t inptWidthInByte = inptWidth * elemSizeInByte;*/

//     process_state_t write_state = IDLE;
//     process_state_t read_state = IDLE;

//     process_control_t processing = ENABLE;

//     uint32_t chunkSize = (uint32_t)((float) 128/(float) elemSizeInByte);

//     uint32_t diff = (len * elemSizeInByte) % chunkSize;

//     uint64_t cycleCounter = 0;
//     uint32_t img_diff = len-diff;

//     while(processing)
//     {
//         switch(write_state)
//         {
//             case IDLE:
//                 writeOffset = 0;
//                 write_state = WRITE;
//                 break;
//             case WRITE:
//                 if (writeOffset < img_diff)
//                 {
//                     writeToFpga(device_fd, (uint8_t*)input + writeOffset, chunkSize * sizeof(uint32_t));
//                     writeOffset += chunkSize;
//                 }
//                 else
//                 {
//                     if (diff != 0) {
//                         writeToFpga(device_fd, (uint8_t*)input + writeOffset, diff * sizeof(uint32_t));
//                     }
//                     write_state = WRITE_FINISHED;
//                 }
//                 break;
//             case WRITE_FINISHED:
//                 break;
//             default:
//                 break;
//         }

//         switch(read_state){
//             case IDLE:
//                 // if (writeOffset < (2*inptWidthInByte) || cycleCounter < (2*inptWidthInByte))
//                 // {
//                 //     read_state = IDLE;
//                 // }
//                 // else
//                 // {
//                     readOffset = 0;
//                     read_state = READ;
//                 // }
//                 break;
//             case READ:
//                 if (readOffset < img_diff)
//                 {
//                     readFromFpga(device_fd, (uint8_t*)input + readOffset, chunkSize * sizeof(unsigned int));
//                     readOffset += chunkSize;
//                 }
//                 else
//                 {
//                     if (diff != 0)
//                     {
//                         readFromFpga(device_fd, (uint8_t*)input + readOffset, diff * sizeof(unsigned int));
//                     }
//                     read_state = READ_FINISHED;
//                 }
//                 break;
//             case READ_FINISHED:
//                 processing = DISABLE;
//                 break;
//             default:
//                 break;
//         }
//         ++cycleCounter;
//     }
//     // clean up
//     ::close(device_fd);
// }

extern "C" void process_img(void* input, unsigned int len, unsigned int img_width, unsigned int chunckSize){
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    uint32_t* image_pointer = (uint32_t*) input;
    unsigned int write_cnt = 0;
    unsigned int read_cnt = 0;

    // delay reading until write counter reaches:
    unsigned long read_delay = 2 * img_width;

    process_state_t write_state = IDLE;
    process_state_t read_state = IDLE;
    process_control_t processing = ENABLE;

    unsigned int diff = len%chunckSize;
    unsigned int process_len = len - diff;

    while(processing){
        switch(write_state){
            case IDLE:
                write_state = WRITE;
                write_cnt = 0;
                break;
            case WRITE:
                if (write_cnt < process_len) {
                    write(device_fd, image_pointer + write_cnt, chunckSize * sizeof(unsigned int));
                    write_cnt += chunckSize;
                } else {
                    if (diff != 0) {
                        write(device_fd, image_pointer + write_cnt, diff * sizeof(unsigned int));
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
                if (write_cnt < read_delay) {
                    read_state = IDLE;
                } else {
                    read_state = READ;
                }
                read_cnt = 0;
                break;
            case READ:
                if (read_cnt < process_len) {
                    read(device_fd, image_pointer + read_cnt, chunckSize * sizeof(unsigned int));
                    read_cnt += chunckSize;
                } else {
                    if (diff != 0) {
                        read(device_fd, image_pointer + read_cnt, diff * sizeof(unsigned int));
                    }
                    read_state = READ_FINISHED;
                }
                break;
            case READ_FINISHED:
                processing = DISABLE;
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
        writeToFpga(device_fd, img, len * sizeof(unsigned int));
        readFromFpga(device_fd, img, len * sizeof(unsigned int));
    } else {
        // process image
        unsigned int idx = 0;
        unsigned int diff = len%input_data_width;
        for (idx=0; idx<len-diff; idx+=input_data_width){
            writeToFpga(device_fd, img + idx, input_data_width * sizeof(unsigned int));
            readFromFpga(device_fd, img + idx, input_data_width * sizeof(unsigned int));
        }
        if (diff != 0){
            writeToFpga(device_fd, img + idx, diff * sizeof(unsigned int));
            readFromFpga(device_fd, img + idx, diff * sizeof(unsigned int));
        }
    }
    // clean up
    ::close(device_fd);
}

extern "C" void process3d_img(void* img, uint32_t len, uint32_t elemSizeInByte){
    // Note: correct len for elemSizeInBytes
    int device_fd = ::open("/dev/simple_dma0", O_RDWR, (mode_t) 0600);
    // check device_fd
    if(device_fd == -1) {
        perror("Error opening iobar for writing");
        exit(EXIT_FAILURE);
    }

    // width of fpga interface in byte
    uint8_t byteWidthFpgaIntfc = 4;

    uint32_t chunkSize = 1024;//(uint32_t)((float) 64/(float) elemSizeInByte);

    if (len <= chunkSize) {
        writeToFpga(device_fd, img, len * byteWidthFpgaIntfc);
        readFromFpga(device_fd, img, len * byteWidthFpgaIntfc);
    } else {
        // process image
        uint32_t offsetPtr = 0;
        uint32_t diff = (len * elemSizeInByte) % chunkSize;
        for (offsetPtr=0; offsetPtr<len-diff; offsetPtr+=chunkSize){
            writeToFpga(device_fd, (uint8_t*)img + offsetPtr, 1024 * byteWidthFpgaIntfc);
            readFromFpga(device_fd, (uint8_t*)img + offsetPtr, 1024 * byteWidthFpgaIntfc);
        }
        if (diff != 0){
            writeToFpga(device_fd, (uint8_t*)img + offsetPtr, diff * byteWidthFpgaIntfc);
            readFromFpga(device_fd, (uint8_t*)img + offsetPtr, diff * byteWidthFpgaIntfc);
        }
    }
    // clean up
    ::close(device_fd);
}
