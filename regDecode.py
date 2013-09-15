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


def regDecode(regNum, contents):


	print "nRF Register 0x%X:" % (regNum),
	for val in contents[1:]:
		print "%X" % (val), bin(val),
	print

	dat = contents[1]

	if regNum == 0x00:		# CONFIG 0
		print "	Configuration Register"
		if dat & bv(7):
			print "	Invalid Register settings!"
		else:
			pass

		if dat & bv(6):
			print "		RX Interrupt Masked"
		else:
			print "		RX Interrupt not Masked"
		
		if dat & bv(5):
			print "		TX Complete Interrupt Masked"
		else:
			print "		TX Complete Interrupt not Masked"
		
		if dat & bv(4):
			print "		Max resend attempt exceeded interrupt masked"
		else:
			print "		Max resend attempt exceeded interrupt not masked"
		
		if dat & bv(3):
			print "		CRC Enabled"
		else:
			print "		CRC disabled"
		
		if dat & bv(2):
			print "		2 byte CRC setting"
		else:
			print "		1 byte CRC setting"
		
		if dat & bv(1):
			print "		Powered up"
		else:
			print "		Powered down"

		if dat & bv(0):
			print "		RX Mode"
		else:
			print "		TX Mode"

	if regNum == 0x01:		# EN_AA Enhanced ShockBurst 1
		print "	Enable 'Auto Acknowledgment' Function register"

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		Auto Ack for pipe 5 Enabled"
		else:
			print "		Auto Ack for pipe 5 Disabled"
		
		if dat & bv(4):
			print "		Auto Ack for pipe 4 Enabled"
		else:
			print "		Auto Ack for pipe 4 Disabled"
		
		if dat & bv(3):
			print "		Auto Ack for pipe 3 Enabled"
		else:
			print "		Auto Ack for pipe 3 Disabled"
		
		if dat & bv(2):
			print "		Auto Ack for pipe 2 Enabled"
		else:
			print "		Auto Ack for pipe 2 Disabled"
		
		if dat & bv(1):
			print "		Auto Ack for pipe 1 Enabled"
		else:
			print "		Auto Ack for pipe 1 Disabled"

		if dat & bv(0):
			print "		Auto Ack for pipe 0 Enabled"
		else:
			print "		Auto Ack for pipe 0 Disabled"


	if regNum == 0x02:		# EN_RXADDR 2
		print "	Enabled RX Addresses register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		Pipe 5 Enabled"
		else:
			print "		Pipe 5 Disabled"
		
		if dat & bv(4):
			print "		Pipe 4 Enabled"
		else:
			print "		Pipe 4 Disabled"
		
		if dat & bv(3):
			print "		Pipe 3 Enabled"
		else:
			print "		Pipe 3 Disabled"
		
		if dat & bv(2):
			print "		Pipe 2 Enabled"
		else:
			print "		Pipe 2 Disabled"
		
		if dat & bv(1):
			print "		Pipe 1 Enabled"
		else:
			print "		Pipe 1 Disabled"

		if dat & bv(0):
			print "		Pipe 0 Enabled"
		else:
			print "		Pipe 0 Disabled"



	if regNum == 0x03:		# SETUP_AW 3
		print "	Setup of Address Widths register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		Invalid Register settings!"
		
		if dat & bv(4):
			print "		Invalid Register settings!"
		
		if dat & bv(3):
			print "		Invalid Register settings!"
		
		if dat & bv(2):
			print "		Invalid Register settings!"
		

		tmp = dat & 0x03

		if tmp == 0:
			print "Illegal address field setting"
		elif tmp == 1:
			print "		using 3 byte addresses"
		elif tmp == 2:
			print "		using 4 byte addresses"
		elif tmp == 3:
			print "		using 5 byte addresses"




	if regNum == 0x04:		# SETUP_RETR 4
		print "	Setup of Automatic Retransmission register"
		
		retryDel = (dat & 0xF0) >> 4
		retryCnt = dat & 0x0F

		retryDel = (retryDel + 1) * 250

		print "		retry delay = %d uS, retry count = %d" % (retryDel, retryCnt)


		
	if regNum == 0x05:		# RF_CH 5
		print "	RF Channel register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		tmp = dat & 0x7F

		print "		Using RF channel %d" % tmp



	if regNum == 0x06:		# RF_SETUP 6
		print "	RF Setup Register register"
		

		if dat & bv(7):
			print "		Continuous carrier transmit mode enabled."
		else:
			print "		Continuous carrier transmit mode disabled."

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		RF Data Rate set to 250kbps"
		
		if dat & bv(4):
			print "		Force PLL lock signal enabled"
		else:
			print "		Force PLL lock signal disabled"
		
		if dat & bv(3):
			print "		Data rate = 2 Mbps"
		else:
			print "		Data rate = 1 Mbps"
		
		tmp = (dat & 0x06) >> 1

		if tmp == 0:
			print "		transmit power = -18 dBm"
		elif tmp == 1:
			print "		transmit power = -12 dBm"
		elif tmp == 2:
			print "		transmit power = -6 dBm"
		elif tmp == 3:
			print "		transmit power = 0 dBm"

		if dat & bv(0):
			print "		Invalid Register settings!"




	if regNum == 0x07:		# STATUS 7
		print "	Status Register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Data Ready RX FIFO interrupt"
		
		if dat & bv(5):
			print "		Data Sent TX FIFO interrupt"
		
		if dat & bv(4):
			print "		Maximum number of TX retransmits exceeded"
		
		tmp = (dat & 0x0E) >> 1

		if tmp == 7:
			print "		RX Fifos are empty"
		else:
			print "		data in RX fifo: ", tmp

		if dat & bv(0):
			print "		TX FIFO full flag."




	if regNum == 0x08:		# OBSERVE_TX 8
		print "	Transmit observe register"
		

		plostCnt = (dat & 0xF0) >> 4
		retryCnt = dat & 0x0F


		print "		Lost packets = %d, resent attempts on last tx = %d" % (plostCnt, retryCnt)


	if regNum == 0x09:		# RPD 9
		print "	RPD register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		Invalid Register settings!"
		
		if dat & bv(4):
			print "		Invalid Register settings!"
		
		if dat & bv(3):
			print "		Invalid Register settings!"
		
		if dat & bv(2):
			print "		Invalid Register settings!"
		
		if dat & bv(1):
			print "		Invalid Register settings!"

		if dat & bv(0):
			print "		Received Power Detector triggered"
		else:
			print "		Received Power Detector not triggered"




	if regNum == 0x0a:		# RX_ADDR_P0 10
		print "	Receive address data pipe 0 register"
		pass




	if regNum == 0x0b:		# RX_ADDR_P1 11
		print "	Receive address data pipe 1 register"
		pass




	if regNum == 0x0c:		# RX_ADDR_P2 12
		print "	Receive address data pipe 2 register"
		pass

	if regNum == 0x0d:		# RX_ADDR_P3 13
		print "	Receive address data pipe 3 register"
		pass

	if regNum == 0x0e:		# RX_ADDR_P4 14
		print "	Receive address data pipe 4 register"
		pass

	if regNum == 0x0f:		# RX_ADDR_P5 15
		print "	Receive address data pipe 5 register"
		pass

	if regNum == 0x10:		# TX_ADDR 16
		print "	TX Address register"
		pass


	if regNum == 0x11:		# RX_PW_P0 17
		print "	RX Pipe 0 data size setting register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		tmp = dat & 0x3F
		print "		bytes in RX Payload in pipe 0", tmp



	if regNum == 0x12:		# RX_PW_P1 18
		print "	RX Pipe 1 data size setting register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		tmp = dat & 0x3F
		print "		bytes in RX Payload in pipe 1", tmp


	if regNum == 0x13:		# RX_PW_P2 19
		print "	RX Pipe 2 data size setting register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		tmp = dat & 0x3F
		print "		bytes in RX Payload in pipe 2", tmp




	if regNum == 0x14:		# RX_PW_P3 20
		print "	RX Pipe 3 data size setting register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		tmp = dat & 0x3F
		print "		bytes in RX Payload in pipe 3", tmp


	if regNum == 0x15:		# RX_PW_P4 21
		print "	RX Pipe 4 data size setting register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		tmp = dat & 0x3F
		print "		bytes in RX Payload in pipe 4", tmp


	if regNum == 0x16:		# RX_PW_P5 22
		print "	RX Pipe 5 data size setting register"
		
		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		tmp = dat & 0x3F
		print "		bytes in RX Payload in pipe 5", tmp



	if regNum == 0x17:		# FIFO_STATUS 23
		print "	FIFO Status Register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		TX Reuse Set"
		else:
			print "		TX Reuse not Set"
		
		if dat & bv(5):
			print "		TX FIFO Full"
		
		if dat & bv(4):
			print "		TX Fifo Empty"
		
		if dat & bv(3):
			print "		Invalid Register settings!"
		
		if dat & bv(2):
			print "		Invalid Register settings!"
		
		if dat & bv(1):
			print "		RX FIFO Full"

		if dat & bv(0):
			print "		RX FIFO Empty"




	if regNum == 0x18:		# 24
		pass

	if regNum == 0x19:		# 25
		pass

	if regNum == 0x1a:		# 26
		pass

	if regNum == 0x1b:		# 27
		pass

	if regNum == 0x1C:		# DYNPD 27
		print "	Enable dynamic payload length register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		Dynamic payload length enabled on data pipe 5."
		
		if dat & bv(4):
			print "		Dynamic payload length enabled on data pipe 4."
		
		if dat & bv(3):
			print "		Dynamic payload length enabled on data pipe 3."
		
		if dat & bv(2):
			print "		Dynamic payload length enabled on data pipe 2."
		
		if dat & bv(1):
			print "		Dynamic payload length enabled on data pipe 1."

		if dat & bv(0):
			print "		Dynamic payload length enabled on data pipe 0."

	if regNum == 0x1D:		# DYNPD 27
		print "	Feature Register register"
		

		if dat & bv(7):
			print "		Invalid Register settings!"

		if dat & bv(6):
			print "		Invalid Register settings!"
		
		if dat & bv(5):
			print "		Invalid Register settings!"
		
		if dat & bv(4):
			print "		Invalid Register settings!"
		
		if dat & bv(3):
			print "		Invalid Register settings!"
		
		if dat & bv(2):
			print "		Dynamic Payload length enabled"
		else:
			print "		Dynamic Payload length disabled"
		
		if dat & bv(1):
			print "		Payload with ACK enabled"
		else:
			print "		Payload with ACK disabled"

		if dat & bv(0):
			print "		W_TX_PAYLOAD_NOACK command enabled"
		else:
			print "		W_TX_PAYLOAD_NOACK command disabled"



if __name__ == "__main__":
	registers = [
	[0, 14],
	[1, 1],
	[2, 1],
	[3, 3],
	[4, 105],
	[5, 2],
	[6, 6],
	[7, 15],
	[8, 16],
	[9, 0],
	[10, 231],
	[11, 194],
	[12, 195],
	[13, 196],
	[14, 197],
	[15, 198],
	[16, 231],
	[17, 0],
	[18, 0],
	[19, 0],
	[20, 0],
	[21, 0],
	[22, 0],
	[23, 33],
	[24, 0],
	[25, 0],
	[26, 0],
	[27, 0],
	[28, 1],
	[29, 4]
	]

	for reg in registers:
		regDecode(reg[0], [0, reg[1]])