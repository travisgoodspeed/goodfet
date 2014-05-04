//! \file fetextract.c

/*
MSP430 FET Firmware Extractor
by Travis Goodspeed

This extracts the MSP430 FET UIF firmware from MSP430.dll.
Please note that the resulting file is (C) Texas Instruments,
and they might object to its distribution.
*/

//mmap() for input and output.
#include <sys/mman.h>
#define INPUT "MSP430.dll"
#define INPUTLEN 225280
#define OUTPUT "MSP430FET.bin"
#define OUTPUTLEN 0x10000

#include <assert.h>

//memcpy
#include <string.h>

//getpagesize()
#include <unistd.h>
//printf
#include <stdio.h>

//open
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define inbytes (((char*)input))
#define outbytes (((char*)output))
#define inwords (((short*)input))
#define outwords (((short*)output))


void *input, *output;


//! Populates the output file with an entry.
//  Returns the next entry.
unsigned long tabpopulate(long at){
  unsigned short 
    adr=inwords[at>>1],
    len=inwords[at+2>>1];
  printf("adr=%x, len=%x\n",adr,len);
  memcpy(outbytes+adr,//out+begin,
	 inbytes+at+4,//+begin+offset,
	 len<<1);
  adr=inwords[at+4+(len<<1)>>1];
  printf("adr=%x next\n",adr);
  if(adr<0x200) return 0;
  return at+4+(len<<1);
}

//! Simple as can be.
int main(){
  int inputfd=open(INPUT,O_RDONLY), outputfd=open(OUTPUT,O_CREAT|O_RDWR,0666);
  long i, j,k;
  unsigned long at;
  
  assert(inputfd!=-1);
  assert(outputfd!=-1);
  
  //mmap(void *start, size_t length, int prot , int flags, int fd, off_t offset);
  input=mmap(0,//don't care
	     INPUTLEN,//file length
	     PROT_READ|PROT_WRITE,
	     MAP_PRIVATE,
	     inputfd,
	     0);
  assert(input && input!=MAP_FAILED);
  assert( *((char*)input) == 0x4d);//File begins with M
  
  //Blank the output file.
  for(i=0;i<OUTPUTLEN;i++)
    write(outputfd,"\xFF",1);
  
  output=mmap(0,
	      0x10000,//file length
	      PROT_READ|PROT_WRITE,
	      MAP_SHARED,//shared= pages write back, private do not
	      outputfd,
	      0);
  assert(output && output!=MAP_FAILED);
  
  
  //Populate by tables.
  at=0x21036;
  while(at=tabpopulate(at));
  
  //Ensure that nothing is lost.
  msync(output,OUTPUTLEN,MS_SYNC);
  munmap(output,OUTPUTLEN);
  fsync(outputfd);
  close(outputfd);
  munmap(input,INPUTLEN);
  close(inputfd);
}
