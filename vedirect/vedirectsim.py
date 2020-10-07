#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time
import os
import argparse
from vedirect.serconnect import SerialConnection
from vedirect.core.utils import Utils as U

logging.basicConfig()
logger = logging.getLogger("vedirect")

class Vedirectsim(SerialConnection):

    def __init__(self, **kwargs):
        SerialConnection.__init__(self, **kwargs)
        self.dataInput = {}
        self.dict = {}

    def convert(self, datadict):
        """ Convert dict data to vedirect data format """
        result = list()
        for key in self.dict:
            result.append(ord('\r'))
            result.append(ord('\n'))
            result.extend([ord(i) for i in key])
            result.append(ord('\t'))
            result.extend([ord(i) for i in datadict[key]])
        # checksum
        result.append(ord('\r'))
        result.append(ord('\n'))
        result.extend([ord(i) for i in 'Checksum'])
        result.append(ord('\t'))
        result.append((256 - (sum(result) % 256)) % 256)
        return result

    def send_packet(self):
        """ Send packet on serial port """
        logger.debug("Sending packet to serial: %s"%(self.dict))
        try:
            packet = self.convert(self.dict)
        except Exception as ex:
            logger.debug("Fatal Error : Data conversion error at : %s - tim : %s"%(Utils.timeToString(time.time()), time.time()))
            return False

        for k in packet:
            try:               
                self.ser.write(bytes(k))
                
            except Exception as ex:
                logger.debug("Fatal Error : Serial write error in k %s sum : %s at : %s - tim : %s"%(k, sum(packet), Utils.timeToString(time.time()), time.time()), lsr)
                return False
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple VE.Direct simulator')
    parser.add_argument('--port', help='Serial port')
    args = parser.parse_args()
    ve = Vedirectsim(**{args.port})
    while True:
        ve.send_packet()
        time.sleep(1)
        

