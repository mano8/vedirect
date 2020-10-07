# -*- coding: utf-8 -*-

import logging
import time
from vedirect.serconnect import SerialConnection
from vedirect.core.utils import Utils as U

logging.basicConfig()
logger = logging.getLogger("vedirect")

class Vedirect(SerialConnection):

    def __init__(self, **kwargs):
        SerialConnection.__init__(self, **kwargs)
        self.connect()
        self.header1 = ord('\r')
        self.header2 = ord('\n')
        self.hexmarker = ord(':')
        self.delimiter = ord('\t')
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}

    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    def input(self, byte):
        try:
            nbyte = ord(byte)
            if byte == self.hexmarker and self.state != self.IN_CHECKSUM:
                self.state = self.HEX
            if self.state == self.WAIT_HEADER:
                self.bytes_sum += nbyte
                if nbyte == self.header1:
                    self.state = self.WAIT_HEADER
                elif nbyte == self.header2:
                    self.state = self.IN_KEY
                return None
            elif self.state == self.IN_KEY:
                self.bytes_sum += nbyte
                if nbyte == self.delimiter:
                    if (self.key == 'Checksum'):
                        self.state = self.IN_CHECKSUM
                    else:
                        self.state = self.IN_VALUE
                else:
                    self.key += byte.decode('ascii')
                return None
            elif self.state == self.IN_VALUE:
                self.bytes_sum += nbyte
                if nbyte == self.header1:
                    self.state = self.WAIT_HEADER
                    self.dict[self.key] = self.value
                    self.key = ''
                    self.value = ''
                else:
                    self.value += byte.decode('ascii')
                return None
            elif self.state == self.IN_CHECKSUM:
                self.bytes_sum += nbyte
                self.key = ''
                self.value = ''
                self.state = self.WAIT_HEADER
                if (self.bytes_sum % 256 == 0):
                    self.bytes_sum = 0
                    return self.dict
                else:
                    self.bytes_sum = 0
            elif self.state == self.HEX:
                self.bytes_sum = 0
                if nbyte == self.header2:
                    self.state = self.WAIT_HEADER
            else:
                raise AssertionError()
        except Exception as ex:
            logger.debug("Serial input read error %s "%(ex))
            

    def read_data_single(self, timeout = 60):
        """ Read on serial and return single vedirect data """
        bc, now = True, time.time()
        while bc:
            if self.is_serial_ready():
                data = self.ser.read()
                for single_byte in data:
                    packet = self.input(single_byte)
                    if packet != None:
                        return packet
                if time.time()-now > timeout:
                    U.print_danger('[VeDirect] Unable to read serial data. Timeout error - data : %s'% packet)
                    bc = False
            else:
                U.print_danger('[VeDirect] Unable to read serial data. Not connected to serial port...')
                bc = False
        
        return None
            

    def read_data_callback(self, callbackFunction):
        """ Read on serial and return vedirect data on callback function """
        bc, now = True, time.time()
        while bc:
            if self.is_serial_ready():
                byte = self.ser.read()
                packet = self.input(byte)
                if packet != None:
                    callbackFunction(packet)
                # timout serial read
                if time.time()-now > 60:
                    U.print_danger('[VeDirect] Unable to read serial data. Timeout error - data : %s'% packet)
                    bc = False
            else:
                U.print_danger('[VeDirect] Unable to read serial data. Not connected to serial port...')
                bc = False
        
        callbackFunction(None)


    

