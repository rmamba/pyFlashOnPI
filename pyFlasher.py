#!/usr/bin/env python
# Filename: pyFlasher.py

'''
Created on 03 Mar 2014

@author: rmamba@gmail.com
'''

import spidev
import time

#Prerequisites
#RaspberryPi: sudo apt-get install python-dev

#module loading
# edit /etc/modprobe.d/raspi-blacklist.conf 
# and add spi-bcm2708
# reboot

#spidev python wrapper
#mkdir python-spi
#cd python-spi
#wget https://raw.github.com/doceme/py-spidev/master/setup.py
#wget https://raw.github.com/doceme/py-spidev/master/spidev_module.c
#sudo python setup.py install

spi = spidev.SpiDev()

WRITE_ENABLE = 0x06
WRITE_DISABLE = 0x04
READ_STATUS_REGISTER = 0x05
WRITE_STATUS_REGISTER = 0x01
READ_DATA = 0x03
FAST_READ = 0x0B
PAGE_PROGRAM = 0x02
SECTOR_ERASE = 0x20
BLOCK_ERASE = 0xD8
BLOCK_ERASE_ = 0x52
CHIP_ERASE = 0xC7
CHIP_ERASE_ = 0x60
DEVICE_ID = 0x90
READ_IDENTIFICATION = 0x9F

#
FLASH_WORD = 8	
FLASH_SIZE_BYTES = 4194304
FLASH_PAGE_BYTES = 256
FLASH_SECTOR_BYTES = 4096
FLASH_BLOCK_BYTES = 65536

FLASH_PAGES = 16384
FLASH_SECTORS = 1024
FLASH_BLOCKS = 64

def read_status_register():
	spi.writebytes([READ_STATUS_REGISTER])
	return spi.readbytes(1)
	
def read_device_id():
	spi.writebytes([DEVICE_ID, 0x00, 0x00, 0x00])
	return spi.readbytes(2)
	
def read_identification():
	spi.writebytes([READ_IDENTIFICATION])
	return spi.readbytes(3)

def read_flash_memory():
	spi.writebytes([READ_DATA, 0x00, 0x00, 0x00])
	return spi.readbytes(FLASH_SIZE_BYTES)
		
def read_data_sector(sector):
	address = sector * FLASH_SECTOR_BYTES
	spi.writebytes([READ_DATA, address >> 16 & 0xff, address >> 8 & 0xff, address & 0xff])
	return spi.readbytes(FLASH_SECTOR_BYTES)

def chip_erase(bPrint=false):
	print "erasing flash."
	spi.xfer2(CHIP_ERASE)
	reg = 0xff
	while reg[0] & 0x01 == 0x01
		time.sleep(.5)
		reg = read_status_register()
		if bPrint:
			print "."

if __name__ == '__main__':	
	bWrite = false
	bDeviceId = false
	file = "out.flash"
	type = "8x4Mbyte"
	speed = 1
	try:
		for arg in sys.argv:
			if arg.startswith('--type='):
				tmp = arg.split('=')
				type = tmp[1]
			if arg.startswith('--file='):
				tmp = arg.split('=')
				file = tmp[1]
			if arg.startswith('--speed='):
				tmp = arg.split('=')
				speed = float.tryParse(tmp[1])
				if speed == None:
					speed = 1
#			if arg.startswith('--write'):
#				bWrite = true
			if arg.startswith('--deviceid'):
				bDeviceId = true
	
		spi.open(0,0)
		if speed == 0.5:
			spi.max_speed_hz = 500000					#0.5MHz
		elif speed == 1:
			spi.max_speed_hz = 1000000					#1MHz
		elif speed == 2:
			spi.max_speed_hz = 2000000					#1MHz
		elif speed == 4:
			spi.max_speed_hz = 4000000					#1MHz
		elif speed == 8:
			spi.max_speed_hz = 8000000					#1MHz
		elif speed == 16:
			spi.max_speed_hz = 16000000					#1MHz
		elif speed == 32:
			spi.max_speed_hz = 32000000					#1MHz
			
		if bDeviceId:		
			print read_device_id()
		elif bWrite:
			#erase chip			
			#read file page at a time
			#program page
		else:
			cnt = 0
			#while cnt<FLASH_SECTORS:
			#	bytes = read_data_sector(cnt)
			#	cnt++
			print read_data_sector(0)
		spi.close()
		
	except Exception,e:
		print "Error: " + str(e)
