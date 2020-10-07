import logging
import serial
import os
import re
from vedirect.core.utils import Utils as U

logging.basicConfig()
logger = logging.getLogger("vedirect")

class SerialConnection:
    
    def __init__(self, **kwargs):
        """ """
        self._status = False
        self._settings = dict()
        self._ser = None
        self._patterns = {
            'unix': re.compile(r'^(\/\w+\/)+((?:(?:tty(?:USB|ACM|S))|(?:vmodem))(?:\d{1,5}))$'),
            'win': re.compile(r'^(COM\d{1,5})$')
        }
        self._op_sys = U.get_operating_system_type()
        self._dev_paths = ['/dev/', '/tmp/', '']
        if self.init_data(**kwargs):
            self._status = True

    def is_ready(self):
        """ Test if is ready """
        return self._status and self.is_serial_ready()

    def is_serial_ready(self):
        return isinstance(self._ser, serial.Serial) and self._ser.isOpen()

    def is_settings(self):
        """ Test if is valid kwargs """
        return U.isDict(self._settings) and self.is_serialport(self._settings.get('serialport')) and self.is_baud(self._settings.get('baud')) and self.is_timeout(self._settings.get('timeout'))

    def is_kwargs(self, data):
        """ Test if is valid kwargs """
        return U.isDict(data) and ('serialport' in data or 'serialpath' in data)

    def is_serialport(self, data):
        """ Test if is valid serial port """
        return U.isStr(data)

    def is_serialpath(self, data):
        """ Test if is valid serial path """
        return U.isStr(data)
    
    def is_baud(self, data):
        """ Test if is valid baud """
        return U.isInt(data) and data in [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
    
    def is_timeout(self, data):
        """ Test if is valid timeout """
        return U.isInt(data) and data > 0
    
    @staticmethod
    def _get_absolute_serial_path(dev, tty):
        """
        Get absolute serial port
        """
        return str(dev) + os.sep + str(tty)

    @classmethod
    def _is_valid_tty_path(cls, dev, tty):
        """
        Test if valid serial port path
        """
        return os.path.exists(cls._get_absolute_unix_serial_path(dev,tty))

    def _is_valid_tty(self, dev, tty, sys_type='unix'):
        """
        Test if valid unix serial port
        """
        tst = self._patterns.get(sys_type)
        if tst is not None and tst.findall(tty) and self._is_valid_tty_path(dev, tty):
            return True
        return False

    def init_setings(self):
        """ Initialise default settings """
        self._settings = {
                'serialport': None,
                'serialpath': None,
                'baud': 19200,
                'timeout': 10,
            }

    def init_data(self, **kwargs):
        """ Initialise settings from kwargs """
        tst = False
        if self.is_kwargs(kwargs):
            
            self.init_setings()
            
            if self.is_serialport(kwargs.get('serialport')):
                self._settings['serialport'] = kwargs.get('serialport')
                tst = True
            
            if self.is_serialpath(kwargs.get('serialpath')):
                self._settings['serialpath'] = kwargs.get('serialpath')
            
            if self.is_baud(kwargs.get('baud')):
                self._settings['baud'] = kwargs.get('baud')

            if self.is_timeout(kwargs.get('timeout')):
                self._settings['timeout'] = kwargs.get('timeout')

        return tst 
    
    def connect(self, **kwargs):
        """ start serial connection from kwargs parameters or from settings """
        logger.info('[VeDirect] Attemping serial connection...')
        logger.debug('[VeDirect] settings : %s'%self._settings)
        if (self.is_kwargs(kwargs) and self.init_data(**kwargs)) or self.is_settings():
            d = U.get_keys_from_dict(self._settings, ['serialport', 'baud', 'timeout'])
            serialport, baud, timeout = d.get('serialport'), d.get('baud'), d.get('timeout')
            try:
                self._ser = serial.Serial(serialport, baud, timeout=timeout)
                if self._ser.isOpen():
                    U.print_success('[VeDirect] Serial connection to %s oppened...'% serialport)
                    return True
                else:
                    logger.debug('[VeDirect] Unable to open serial connection to %s'% serialport)
            except (serial.SerialException, serial.SerialTimeoutException) as ex:
                logger.error('[VeDirect] Exception when attemping to open serial connection to %s. ex : %s'% (serialport, ex))    
        else:
            logger.debug('[VeDirect] Unable to open serial connection. Invalid settings : %s'% self._settings)
        
        return False
        
    def __get_list_tty_ports_from_path(self, path, badTty = None):
        """ Get list of serial ports from path on linux operating system """
        ttys = list()
        if U.isStr(path) and os.path.exists(path):
            if U.isTuple(self._op_sys) and self._op_sys[1] == 'Linux':
                try:
                    # get list files from path
                    lstP = os.listdir(path)
                    if U.isList(lstP) and lstP:
                        for f in lstP:
                            if badTty != f and self._is_valid_tty(path, f, self._op_sys):
                                ttys.append(f)
                except OSError as ex:
                    logger.error("[VeDirect] Error on get list tty on path '%s' - err : '%s'"% (path, ex))
        return ttys
