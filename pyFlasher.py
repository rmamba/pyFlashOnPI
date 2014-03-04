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

#EN25F32 32Mbit flash in SO8 case
#used in TP-Link WR741ND router to hold the firmware
#max SPI speed is 100MHz
FLASH_WORD = 8
FLASH_SIZE_BYTES = 4194304
FLASH_PAGE_BYTES = 256
FLASH_SECTOR_BYTES = 4096
FLASH_BLOCK_BYTES = 65536

FLASH_PAGES = 16384
FLASH_SECTORS = 1024
FLASH_BLOCKS = 64

def set_flash_parameters(param):						#param == [wordbits, Mbits, pages, sectors, blocks]
	FLASH_WORD = param[0]
	FLASH_SIZE_BYTES = param[1] * 1024 * 1024 / FLASH_WORD
	FLASH_PAGES = param[2]
	FLASH_SECTORS = param[3]
	FLASH_BLOCKS = param[4]
	FLASH_PAGE_BYTES = FLASH_SIZE_BYTES / FLASH_PAGES
	FLASH_SECTOR_BYTES = FLASH_SIZE_BYTES / FLASH_SECTORS
	FLASH_BLOCK_BYTES = FLASH_SIZE_BYTES / FLASH_BLOCKS

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
	spi.xfer2(CHIP_ERASE)
	reg = 0xff
	while reg[0] & 0x01 == 0x01
		time.sleep(.5)
		reg = read_status_register()
		if bPrint:
			print "."
			
def page_program(pa, data):
	address = pa * FLASH_PAGE_BYTES
	page = [PAGE_PROGRAM, address >> 16 & 0xff, address >> 8 & 0xff, address & 0xff]
	page.extend(data)
	spi.writebytes(page)
	
def enable_write():
	spi.xfer2([WRITE_ENABLE])

def disable_write():
	spi.xfer2([WRITE_DISABLE])

if __name__ == '__main__':	
	bWrite = false
	bDeviceId = false
	file = "out.flash"
	device = "EN25F32"
	try:
		spi.open(0,0)
	
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
				if speed == 0.5:
					spi.max_speed_hz = 500000					#0.5MHz
				elif speed == 1:
					spi.max_speed_hz = 1000000					#1MHz
				elif speed == 2:
					spi.max_speed_hz = 2000000					#2MHz
				elif speed == 4:
					spi.max_speed_hz = 4000000					#4MHz
				elif speed == 8:
					spi.max_speed_hz = 8000000					#8MHz
				elif speed == 16:
					spi.max_speed_hz = 16000000					#16MHz
				elif speed == 32:
					spi.max_speed_hz = 32000000					#32MHz
				else
					spi.max_speed_hz = 1000000					#default							
#			if arg.startswith('--write'):
#				bWrite = true
			if arg.startswith('--deviceid'):
				bDeviceId = true
			if arg.startswith('--device='):
				tmp = arg.split('=')
				if tmp[1] == "EN25F32":
					set_flash_parameters([8, 32, 16384, 1024, 64])
				else
					print "Unknown device!"
					raise SystemExit
					
		if bDeviceId:
			print "Device ID bytes: "
			print read_device_id()
			print "\r\n"
		elif bWrite:
			enable_write()											#enable changes to flash
			print "Erasing flash ."
			#chip_erase(true)										#Erase chip, prepare for programming
			print "\r\nProgramming chip ."
			try:
				f = open(file, "rb")								#open program file
				p = 0			
				while p<FLASH_PAGES:
					data = f.read(FLASH_PAGE_BYTES)					#read one page from file
					page_program(p, data)							#program page
					p++				
			except Exception,e:
				print "\r\nError: " + str(e)
			finally:
				f.close()
			disable_write()											#disable changes to flash
			print "\r\nDone!\r\n"
		else:
			s = 0
			f = open(file, "wb")
			print "Reading chip ."
			while s<FLASH_SECTORS:
				bytes = read_data_sector(cnt)
				f.write(bytes)
				print "."
				s++
			f.close()
			print "\r\nDone!\r\n"
		spi.close()
		
	except Exception,e:
		print "Error: " + str(e)

	finally:
		spi.close()
		f.close()
