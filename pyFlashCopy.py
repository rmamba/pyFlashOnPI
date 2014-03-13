#!/usr/bin python
# Filename: pyFlashCopy.py

'''
Created on 13 Mar 2014

@author: rmamba@gmail.com
'''

import sys, os.path

if __name__ == '__main__':
	size = None
	targetOffset = 0
	sourceOffset = 0
	bAppend = False
	fileIn = None
	fileOut = None
	sections = None
	routerParams = None
	
	try:
		if len(sys.argv) < 3:
			print "Not enough parameters!"
			raise SystemExit
		
		fileIn = sys.argv[1]
		if not os.path.isfile(fileIn):
			print "File does not exist!"
			raise SystemExit		
		fileOut = sys.argv[2]
		
		for arg in sys.argv:
			if (arg == '--append') or (arg == '-a'):
				bAppend = True
			if arg.startswith('--size=') or arg.startswith('-si='):
				tmp = arg.split('=')
				size = int(tmp[1])
			if arg.startswith('--sourceOffset=') or arg.startswith('-so='):
				tmp = arg.split('=')
				sourceOffset = tmp
			if arg.startswith('--targetOffset=') or arg.startswith('-to='):
				tmp = arg.split('=')
				targetOffset = tmp
			if arg.startswith('--router=') or arg.startswith('-r='):
				#-r=WR741ND:v43:uboot,rootfs
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
				routerSection = tmp2[2].split(",")
			
		fIn = file.open(fileIn, "rb")
		if size == None:
			fIn.seek(0, 2)
			size = fIn.tell() - sourceOffset
		fIn.seek(sourceOffset)
		
		if bAppend:
			if not os.path.isfile(fileOut):
				print "File does not exist!"
				raise SystemExit
			
			fOut = file.open(fileOut, "ab")
			fOut.seek(0, 2)
			readData = 0
			
			while readData < size:
				data = fIn.read(1024)
				fOut.write(data)
				readData = readData + 1024
			
			fout.close()
		else:
			if not os.path.isfile(fileOut):
				print "File does not exist!"
				raise SystemExit
			if routerSection == None:
				if targetOffset > 0:
					#inject data
					fOut = file.open(fileOut, "r+b")
					fOut.seek(targetOffset)
				else:
					fOut = file.open(fileOut, "wb")
				
				readData = 0
				chunk = 4096
				while readData < size:
					data = fIn.read(chunk)
					fOut.write(data)
					readData = readData + chunk
					if size-readData<chunk:
						chunk = size-readData
			else:
				for sec in routerSection:
					fIn.seek(int(routerParams[sec]["offset"]))
					fOut = file.open(fileOut, "r+b")
					fOut.seek(int(routerParams[sec]["offset"]))
					size = int(routerParams[sec]["size"])
					
					readData = 0
					chunk = 4096
					while readData < size:
						data = fIn.read(chunk)
						fOut.write(data)
						readData = readData + chunk
						if size-readData<chunk:
							chunk = size-readData
			fOut.close()
		fIn.close()
			
	except Exception,e:
		print "Error: " + str(e)

	finally:
		if f != None:
			f.close()
