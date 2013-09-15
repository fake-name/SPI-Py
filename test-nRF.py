#!/usr/bin/python


import sys

import time
import spi
import RPi.GPIO as GPIO

# This is a very simple script that uses the rPi SPI port to read out the various registers in a nRF24L01+ device
# connected to the rPI SPI port 0
# It should be pretty self-explanitory
#
# C. Wolf, ImaginaryIndustries.com
#

CE	= 17
IRQ	= 18


#CE	= 24
#IRQ	= 25

nRF_CONFIG		= 0x00
nRF_EN_AA		= 0x01
nRF_EN_RXADDR	= 0x02
nRF_SETUP_AW	= 0x03
nRF_SETUP_RETR	= 0x04
nRF_RF_CH		= 0x05
nRF_RF_SETUP	= 0x06
nRF_STATUS		= 0x07
nRF_OBSERVE_TX	= 0x08
nRF_CD			= 0x09
nRF_RPD			= 0x09
nRF_RX_ADDR_P0	= 0x0A
nRF_RX_ADDR_P1	= 0x0B
nRF_RX_ADDR_P2	= 0x0C
nRF_RX_ADDR_P3	= 0x0D
nRF_RX_ADDR_P4	= 0x0E
nRF_RX_ADDR_P5	= 0x0F
nRF_TX_ADDR		= 0x10
nRF_RX_PW_P0	= 0x11
nRF_RX_PW_P1	= 0x12
nRF_RX_PW_P2	= 0x13
nRF_RX_PW_P3	= 0x14
nRF_RX_PW_P4	= 0x15
nRF_RX_PW_P5	= 0x16
nRF_FIFO_STATUS	= 0x17
nRF_DYNPD		= 0x1C
nRF_FEATURE		= 0x1D


def bv(inVal):
	return (1 << inVal)

import regDecode

class nRF:

	def __init__(self):
		self.spi = spi 			# Eventually, I'm going to make the SPI library properly OO
						# by treating it as OO now, It shouldn't take much work to swap in the future.

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(CE, GPIO.OUT)
		GPIO.output(CE, GPIO.LOW)
		GPIO.setup(IRQ, GPIO.IN)
		status = self.spi.openSPI(speed=1000000, device="/dev/spidev0.0")


		print "SPI configuration = ", status

	# -----------------------------------------------------------------------------------------------------------------------------------------------------
	# low-level register stuff:


	def readRegisters(self):

		print "Reading nRF24L01 status registers:"

		for x in range(0x1E):
			if x == 0x0A or x == 0x0B or x == 0x10:		# pipe addresses
				data = (0, 0, 0, 0, 0)
				dat = self.registerOperation(address=x, data=data)
			else:
				data = (0,)
				dat = self.registerOperation(address=x, data=data)

			regDecode.regDecode(x, dat)



	def triggerTxCycle(self):
		GPIO.output(CE, GPIO.HIGH)

		nop = "nop"			# we need to ensure that CE is high for atleast 10 uS.
		nop += "nop"			# Unfortunately, come in just under that. As such, we need to simply spinwait
		nop += "nop"			# for a bit. Yes, this apparently actually works.
		nop += "nop"
		nop += "nop"
		nop += "nop"

		GPIO.output(CE, GPIO.LOW)

	def setCE(self):
		GPIO.output(CE, GPIO.HIGH)

	def clearCE(self):
		GPIO.output(CE, GPIO.LOW)



	def registerOperation(self, write=False, address=0, data=0):		# with no arguments, returns the status
		# 000A AAAA - Read Operation
		# 001A AAAA - Write Operation
		# A AAAA is the address

		if address < 0 or address >= 2**5:
			raise ValueError("Address exceeds possible range")

		if write:			# Bit 6 in the command word dictates if this is a write or read. 0 = read, 1 = write
			address |= 32		# if we're writing, set bit 6

		if type(data) == int:		# If the contents of data is a number, we need to build an empty tuple of data + 1 (len of address) to
						# pass to the SPI hardware, to make it transfer the correct number of bytes
			command = (address,) + (0,) * data

		else:				# Otherwise, the contents of data are probably a list, or something
			data = tuple(data) 	# try to cast to a tuple. If this fails, the user did something wrong.

			command = (address, ) + data

		ret = self.spi.transfer(command)

		return ret

	def readRxContents(self, readLen=32):			# read from the RX FIFO. The nRF has three 32 byte registers in the RX and
								# TX FIFOs. By default, we read the entire 32 bytes.
								# Command: 0110 0001 = 97 as an int
		command = (0x61,) + (0, ) * readLen
		return self.spi.transfer(command)

	def readRxContentLength(self):				# read the length of the payload in the top of the RX FIFO
		return self.spi.transfer((0x60, 0))		# command: 0110 0000 = 96.
								# REQUIRES that toggleActivation has been called previously

	def writeTxContents(self, data):			# Write to the TX FIFO. The nRF has three 32 byte registers in the RX and
								# TX FIFOs. len(data) cannot exceed 32, as a result
								# Command: 1010 0000 = 160 as an int
		if len(data) > 32:
			raise ValueError("Data too long for TX register")

		command = (0xA0,) + tuple(data)
		return self.spi.transfer(command)

	def writeTxContentsNoAck(self, data):			# Write to the TX FIFO without an Ack
								# Command: 1011 0000 = 176 as an int
		if len(data) > 32:
			raise ValueError("Data too long for TX register")

		command = (0xB0,) + tuple(data)
		return self.spi.transfer(command)

	def writeAckPayload(self, data, pipe=0):		# Write to the TX FIFO. PIPE is a 3-bit number, so it's limited to
								# 0-7.
								# Command: 1010 1PPP = 168 as an int, where PPP is the pipe number
		if len(data) > 32:
			raise ValueError("Data too long for TX register")
		if pipe < 0 or pipe >= 2**3:
			raise ValueError("Invalid TX PIPE")

		command = 0xA8 | pipe
		command = (command,) + tuple(data)
		return self.spi.transfer(command)

	def getFifoStatus(self):
		return self.registerOperation(address=0x17, data=1)[1]


	def getCarrierDetect(self):
		return self.registerOperation(address=0x09, data=1)[1]

	def flushTxFifo(self):					# flush the TX FIFO
		return self.spi.transfer((0xE1, ))		# 225 = 1110 0001. Additional byte may not be needed

	def flushRxFifo(self):					# flush the RX FIFO
		return self.spi.transfer((0xE2, ))		# 226 = 1110 0010. Additional byte may not be needed

	def txPayloadReuse(self):				# Continually retransmit the contents in the TX buffer
		return self.spi.transfer((0xE3, 0))		# as long as CE is held high. 227 = 1110 0011

	def toggleActivation(self):				# Toggle the activation state of the nRF device
		return self.spi.transfer((80, 0x73))		# 80 = 0101 0000. the 0x73 constant is from the nRF datasheet
								# I don't know if there is a way to know if you're activationg or deactivating
								# the device without reading the corresponding status registers.


	def getStatus(self):					# Get the status, and do nothing else.
		return self.spi.transfer((0xFF,))[0]			# effectively a NOP

	def statusDecode(self):
		status = self.getStatus()

		if status & 0x01:
			print "TX FIFO Full"
		if status & 0x0E and (status & 0x0E) != 0x0E:
			print "Data in RX FIFO"
		if status & 0x10:
			print "TX retransmit attemps exceeded"
			print "Clearing Interrupt flag"

			self.registerOperation(address=nRF_STATUS, write=True, data=(bv(4),))

		if status & 0x20:
			print "Data Sent Interrupt"
		if status & 0x40:
			print "Data Received Interrupt"

		fifo = self.getFifoStatus()
		if (fifo & 0x20):
			print "TX FIFO Full"
		if (fifo & 0x10) != 0x10:
			print "TX FIFO not empty"

		if (fifo & 0x02):
			print "RX FIFO Full"

		if (fifo & 0x01) != 1:
			print "RX FIFO not Empty"
		print "0x07", bin(status), "0x17", bin(fifo)

	# -----------------------------------------------------------------------------------------------------------------------------------------------------
	# API:

	def close(self):

		spi.closeSPI()
		GPIO.cleanup()





def setupNRF(devH, transmit=True, mLen=6):

	configByte = 0x7C | 0x02	

	if not transmit:
		configByte = configByte | bv(0) # Set PRIM_RX
		print "TX Mode"
		
	devH.registerOperation(address=nRF_CONFIG, write=True, data=(configByte,))

	devH.registerOperation(address=nRF_STATUS, write=True, data=(0x70,))

	#devH.registerOperation(address=0x01, write=True, data=(0x00,))		# disable auto-ack, RX mode
	#devH.registerOperation(address=0x02, write=True, data=(0x3F,))		# enable all receive pipes

	devH.registerOperation(address=nRF_EN_AA,		write=True, data=(0x0F,))		# enable auto-ack, RX mode
	devH.registerOperation(address=nRF_EN_RXADDR,	write=True, data=(0x0F,))		# enable all receive pipes


	# devH.registerOperation(address=0x03, write=True, data=(0x03,))		# address width = 5
	devH.registerOperation(address=nRF_SETUP_AW,	write=True, data=(0x03,))		# address width = 5

	#devH.registerOperation(address=0x04, write=True, data=(0x00,))		# auto retransmit off
	#devH.registerOperation(address=0x05, write=True, data=(0x02,))		# set channel 2, this is default but we did it anyway.
	#devH.registerOperation(address=0x06, write=True, data=(0x07,))		# data rate = 1MB, output power = 0dBm

	devH.registerOperation(address=nRF_SETUP_RETR,	write=True, data=(0x69,))		# 1500 us retransmit delay (6 * 250), 9 retransmit attempts
	devH.registerOperation(address=nRF_RF_CH,		write=True, data=(0x02,))		# set channel 2, this is default but we did it anyway.
	devH.registerOperation(address=nRF_RF_SETUP,	write=True, data=(0x06,))		# data rate = 2MB/s, output power = 0dBm



	#devH.registerOperation(address=0x0A, write=True, data=(0xE7, 0xE7, 0xE7, 0xE7, 0xE7))		# set TX address E7E7E7E7E7, also default.
	#devH.registerOperation(address=0x10, write=True, data=(0xE7, 0xE7, 0xE7, 0xE7, 0xE7))		# set RX pipe 0 address E7E7E7E7E7, also default.
	#devH.registerOperation(address=0x11, write=True, data=(16, ))					# 6 byte payload


	
	devH.registerOperation(address=nRF_RX_ADDR_P0,	write=True, data=(0xE7, 0xE7, 0xE7, 0xE7, 0xE7))		# set RX address E7E7E7E7E7
	#devH.registerOperation(address=nRF_RX_ADDR_P1,	write=True, data=(0x57, 0x57, 0x57, 0xE8, 0xE8))		# set RX address E7E7E7E7E7
	devH.registerOperation(address=nRF_TX_ADDR,	write=True, data=(0xE7, 0xE7, 0xE7, 0xE7, 0xE7))		# set TX pipe 0 address E7E7E7E7E7

	devH.registerOperation(address=nRF_RX_PW_P0,	write=True, data=(0, ))
	devH.registerOperation(address=nRF_RX_PW_P1,	write=True, data=(0, ))
	devH.registerOperation(address=nRF_RX_PW_P2,	write=True, data=(0, ))

	devH.registerOperation(address=nRF_DYNPD,	write=True, data=(bv(5)|bv(4)|bv(3)|bv(2)|bv(1)|bv(0) , ))
	devH.registerOperation(address=nRF_FEATURE,	write=True, data=(bv(2) | bv(0), )) # bv(2)|bv(1)|bv(0), ))

	
	#configByte = configByte | 0x02		# Set the power-up byte.
	#devH.registerOperation(address=0x00, write=True, data=(configByte,))

	'''
	activated = devH.registerOperation(address=0x1D, data=1)		# read ACTIVATE status
	if not activated:
		print "Activating nRF"
		devH.toggleActivation()
		devH.registerOperation(address=0x1D, write=True, data=0x07)
	else:
		print "Already Activated"
	'''

	#data = data | bv(1)			# PTX # Finally, Power up the nRF
	#devH.registerOperation(address=0x00, write=True, data=(data, ))


def strToTuple(string):
	ret = ()
	for char in string:
		ret += (ord(char),)

	return ret

if __name__ == "__main__":

	message = strToTuple("OH HAI FROM RPI!")
	print message
	if len(sys.argv) == 1:
		print "please specify either TX or RX mode"
		sys.exit()

	if sys.argv[1].lower() == "tx":
		print "TX mode"
		transmit = True
	else:
		print "RX Mode"
		transmit = False

	nDev = nRF()

	# print nDev.registerOperation()
	# print nDev.registerOperation()
	#print nDev.writeTxContents([0x48, 0x65, 0x72, 0x70, 0x20, 0x61, 0x20, 0x44, 0x65, 0x72, 0x70])

	print "Flushing Registers"
	nDev.flushRxFifo()
	nDev.flushTxFifo()
	nDev.getStatus()

	setupNRF(nDev, transmit=transmit, mLen=len(message))

	nDev.readRegisters()

	nDev.registerOperation(address=nRF_STATUS,	write=True, data=(0x70, ))
	nDev.registerOperation(address=nRF_TX_ADDR,	write=True, data=(0xE7, 0xE7, 0xE7, 0xE7, 0xE7))

	oldTime = time.time()

	txInterval = 0.001
	txTime = time.time()

	deltTimes = []

	try:
		if transmit:
			while 1:

				if time.time() >= txTime or True:
					txTime += txInterval



					#print "TXing"
					nDev.writeTxContentsNoAck(message)
					#nDev.writeTxContents(message)
					nDev.triggerTxCycle()
					

					while 1:
						fifo = nDev.getFifoStatus()
						if (fifo & bv(4)):
							#print "Sent"
							break
						#sys.stdout.write(".")

					#print "Status: ",
					#nDev.statusDecode()
					#print "TimeDelta", curTime-oldTime
		else:
			nDev.registerOperation(address=nRF_FEATURE,	write=True, data=(bv(2) , )) # bv(2)|bv(1)|bv(0), ))

			nDev.setCE()
				
			while 1:

				status = nDev.getFifoStatus()
				RXEmpty = (status & 0x01)
				if not RXEmpty:
					curTime = time.time()
					deltTime = curTime-oldTime
					deltTimes.append(deltTime)
					#print "Packet!", not RXEmpty, deltTime
					oldTime = curTime
					
					rxLen = nDev.readRxContentLength()
					#print "rxLen = ", rxLen, 
					rxLen = rxLen[1]
					content = nDev.readRxContents(readLen=rxLen)[1:]
					contentStr = ""
					#print len(content),
					for char in content:
						contentStr += chr(char)
					#print contentStr

				#nDev.statusDecode()
				

	except KeyboardInterrupt:
		print "Exiting"




	nDev.close()

	if len(deltTimes) > 5:
		import numpy
		print deltTimes[2:-3]
		meanTime = numpy.mean(deltTimes[2:-3])
		print "Average packet time", meanTime
		print "Packets/second", 1 / meanTime

