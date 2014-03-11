#!/usr/bin python
# Filename: pyFlasher.py

'''
Created on 03 Mar 2014

@author: rmamba@gmail.com
'''

import sys, time, json, os.path
import spidev

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
CHIP_ERASE = 0x60
CHIP_ERASE2 = 0xC7
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
	return spi.xfer2([READ_STATUS_REGISTER])
	
def read_device_id():
	ret = spi.xfer2([DEVICE_ID, 0x00, 0x00, 0x00, 0x00, 0x00])
	return ret[4:]
	
def read_identification():
	cmd = [READ_IDENTIFICATION]
	cmd.extend([0x00] * 81)
	ret = spi.xfer2(cmd)
	return ret[1:]

def read_flash_memory():
	spi.writebytes([READ_DATA, 0x00, 0x00, 0x00])
	return spi.readbytes(FLASH_SIZE_BYTES)
		
def read_data_sector(sector):
	address = sector * FLASH_SECTOR_BYTES
	ret = []
	cmd = [READ_DATA, address >> 16 & 0xff, address >> 8 & 0xff, address & 0xff]
	tmp = FLASH_SECTOR_BYTES
	ext = 1024
	while tmp>0:
		if tmp<1024:
		    ext = tmp
		cmd.extend([0x00] * ext)
		tmp = tmp - ext
		ret2 = spi.xfer2(cmd)
		ret.extends(ret2[4:])
	return ret

def read_data_page(page):
	address = page * FLASH_PAGE_BYTES
	cmd = [READ_DATA, address >> 16 & 0xff, address >> 8 & 0xff, address & 0xff]
	cmd.extend([0x00] * 256)
	ret = spi.xfer2(cmd)
	return ret[4:]

def chip_erase(bPrint=False):
	spi.xfer2([WRITE_ENABLE, CHIP_ERASE])
	reg = 0xff
	while reg & 0x01 == 0x01:
		time.sleep(.5)
		reg = read_status_register()
		if bPrint:
			sys.stdout.write(".")
			sys.stdout.flush()
			
def page_erase(pa):
	cmd = [WRITE_ENABLE]
	spi.xfer2()
	reg = 0xff
	while reg[0] & 0x01 == 0x01:
		time.sleep(.5)
		reg = read_status_register()
		if bPrint:
			sys.stdout.write(".")
			sys.stdout.flush()
			
def page_write(pa, data):
	address = pa * FLASH_PAGE_BYTES
	page = [PAGE_PROGRAM, address >> 16 & 0xff, address >> 8 & 0xff, address & 0xff]
	page.extend(data)
	spi.writebytes(page)
	
def enable_write():
	spi.xfer2([WRITE_ENABLE])

def disable_write():
	spi.xfer2([WRITE_DISABLE])

if __name__ == '__main__':
	routerParams = None
	routerSection = None
	bWrite = False
	bDeviceId = False
	bTest = False
	f = None
	file = None
	device = "EN25F32"
	try:
		spi.open(0,0)
		for arg in sys.argv:
			if arg.startswith('--type='):
				tmp = arg.split('=')
				type = tmp[1]
			if (arg.startswith('--file=')) or (arg.startswith('-f=')):
				tmp = arg.split('=')
				file = tmp[1]
			if arg.startswith('--speed='):
				tmp = arg.split('=')
				speed = float(tmp[1])
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
				else:
					spi.max_speed_hz = 1000000					#default
#			if (arg == '--write') or (arg == '-w'):
#				bWrite = true
			if (arg == '--deviceid') or (arg == '-id'):
				bDeviceId = True
			if arg.startswith('--testspi'):
				bTest = True
			if arg.startswith('--flash=') or arg.startswith('-f='):
				tmp = arg.split('=')
				if tmp[1] == "EN25F32":
					set_flash_parameters([8, 32, 16384, 1024, 64])
				elif tmp[1] == "S25FL032P":
					set_flash_parameters([8, 32, 16384, 1024, 64])
				else:
					print "Unknown device!"
					raise SystemExit
			if arg.startswith('--router=') or arg.startswith('-r='):
				tmp = arg.split('=')
				tmp2 = tmp[1].split(":")
				if len(tmp2) != 3:
					print "Invalid router parameter!"
					raise SystemExit
				
				j = file.open('romlayouts.json', 'r')
				jsn = j.read()
				j.close()				
				jsn = json.loads(jsn)
				if not tmp2[0] in jsn:
					print "Unknown router!"
					raise SystemExit
				jsn = jsn[tmp2[0]]
				if not tmp2[1] in jsn:
					print "Unknown router version!"
					raise SystemExit
				jsn = jsn[tmp2[1]]
				if not tmp2[2] in jsn:
					print "Unknown router section!"
					raise SystemExit
				routerParams = jsn
				routerSection = tmp2[2]
		if bTest:
			print "Testing SPI..."
			print spi.xfer2( range(0, 256) )
			print "Done!"
		elif bDeviceId:
			print "Device ID bytes: "
			print read_identification(), read_device_id()
			print "\r\n"
		elif file == None:
			print "No file specified!"
		elif bWrite:
			if not os.path.isfile(file):
				print "File does not exist!"
				raise SystemExit
			if (routerParams != None) and (routerSection!=None):
				addr = int(routerParams[routerSection]["offset"])
				end = int(routerParams[routerSection]["end"])				
				f = open(file, "rb")
				f.seek( addr )
				while addr<end:
					data = f.read(256)
					#page_erase_page(addr)
					#page_write(addr, data)
					addr = addr + 256
				f.close()				
			else:
				#enable_write()											#enable changes to flash
				print "Erasing flash ."
				#chip_erase(true)										#Erase chip, prepare for programming
				print "\r\nProgramming chip ."
				try:
					f = open(file, "rb")								#open program file
					p = 0			
					while p<FLASH_PAGES:
						data = f.read(FLASH_PAGE_BYTES)					#read one page from file
						page_program(p, data)							#program page
						p=p+1
				except Exception,e:
					print "\r\nError: " + str(e)
				finally:
					f.close()
				#disable_write()											#disable changes to flash
				print "\r\nDone!\r\n"
		else:
			s = 0
			f = open(file, "wb")
			print "Reading chip ."
			while s<FLASH_PAGES:
				bytes = read_data_page(s)
				byteArray = bytearray(bytes)
				f.write(byteArray)
				sys.stdout.write(".")
				sys.stdout.flush()
				s=s+1
			f.close()
			print "\r\nDone!\r\n"
		spi.close()
		
	except Exception,e:
		print "Error: " + str(e)

	finally:
		spi.close()
		if f != None:
			f.close()
