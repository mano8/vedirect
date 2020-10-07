import logging
import os
import sys
import ctypes
import locale
import time
import simplejson as json
from decimal import Decimal

logging.basicConfig()
logger = logging.getLogger("vedirect")

def pipe_print(line):
    line = Utils.encode_text_utf8(line)
    print(line)

class Utils(object):
    color_list = dict(
        PURPLE='\033[95m',
        BLUE='\033[94m',
        GREEN='\033[92m',
        YELLOW='\033[93m',
        RED='\033[91m',
        ENDLINE='\033[0m',
        BOLD='\033[1m',
        UNDERLINE='\033[4m'
    )

    ##################
    #
    # Shell properly displayed
    #
    #########
    @classmethod
    def print_info(cls, text_to_print):
        pipe_print(cls.color_list["BLUE"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_success(cls, text_to_print):
        pipe_print(cls.color_list["GREEN"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_warning(cls, text_to_print):
        pipe_print(cls.color_list["YELLOW"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_danger(cls, text_to_print):
        pipe_print(cls.color_list["RED"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_header(cls, text_to_print):
        pipe_print(cls.color_list["HEADER"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_purple(cls, text_to_print):
        pipe_print(cls.color_list["PURPLE"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_bold(cls, text_to_print):
        pipe_print(cls.color_list["BOLD"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)

    @classmethod
    def print_underline(cls, text_to_print):
        pipe_print(cls.color_list["UNDERLINE"] + text_to_print + cls.color_list["ENDLINE"])
        logger.debug(text_to_print)
    
    ##################
    #
    # Paths management
    #
    #########
    @staticmethod
    def get_current_file_parent_parent_path(current_script_path):
        parent_parent_path = os.path.normpath(current_script_path + os.sep + os.pardir + os.sep + os.pardir)
        return parent_parent_path

    @staticmethod
    def get_current_file_parent_path(current_script_path):
        parent_path = os.path.normpath(current_script_path + os.sep + os.pardir)
        return parent_path
    
    ##################
    #
    # Encoding
    #
    #########
    @staticmethod
    def encode_text_utf8(text):
        if sys.version_info[0] < 3:
            if isinstance(text, unicode):
                text = text.encode("utf-8")
        return text
        
    ##################
    #
    # Tests
    #
    #########

    @staticmethod
    def isStr(s):
        """ Test if value is string """
        return (type(s) is str)
    
    @staticmethod
    def isUnicode(s):
        return (type(s) is unicode)

    @staticmethod
    def isTxt(s):
        return (type(s) is str or type(s) is unicode)

    @staticmethod
    def isBool(s):
        return (type(s) is bool)
    
    @staticmethod
    def isInt(s):
        """
            Test Int Values
        """
        try: 
            int(s)
            return True
        except Exception:
            return False
        return False
    
    @staticmethod
    def isFloat(s):
        try: 
            float(s)
            return True
        except Exception:
            return False
    
    @staticmethod
    def isDecimal(s):
        try: 
            Decimal(s)
            return True
        except Exception:
            return False
    
    @staticmethod
    def isNumeric(s):
        if Utils.isInt(s) or Utils.isFloat(s) or Utils.isDecimal(s):
            return True
        return False
    
    @staticmethod
    def isDict(s):
        return (type(s) is dict)

    @staticmethod
    def isTuple(s):
        return (type(s) is tuple)

    @staticmethod
    def isList(s):
        return (type(s) is list)

    
    @staticmethod
    def getInt(nb, default = 0):
        try:
            return int(nb)
        except Exception:
            return default
        return default
    
    @staticmethod
    def getFloat(nb, default = 0.0):
        try:
            return float(nb)
        except Exception:
            return default
        return default
    
    @staticmethod
    def getDecimal(nb, default = 0.0):
        try:
            return Decimal(nb)
        except Exception:
            return default
        return default
    
    @staticmethod
    def getStr(val, default = None):
        try:
            return str(val)
        except Exception:
            return default
        return default
    
    @staticmethod
    def getElapsedTime(tim, default=-1):
        if Utils.isInt(tim):
            return time.time()-Utils.getInt(tim)
        return default

    @staticmethod
    def formatByType(val, typeData, roundF=None):
        if typeData in ["int", "Int"]:
            return Utils.getInt(val)
        elif typeData in ["float", "Float"]:
            if roundF is not None:
                roundF = Utils.getInt(roundF)
                return round(Utils.getFloat(val), roundF)
            return Utils.getFloat(val)
        elif typeData in ["decimal", "Decimal"]:
            if roundF is not None:
                roundF = Utils.getInt(roundF)
                return round(Utils.getDecimal(val), roundF)
            return Utils.getDecimal(val)
        elif typeData in ["str"]:
            return Utils.getStr(val)
        elif typeData in ["on_off", "OnOff"]:
            return Utils.boolToOnOff(val)
        elif typeData in ["int_bool", "intBool"]:
            return Utils.stringToIntBool(val)
        elif typeData in ["str", "Str"]:
            return Utils.getStr(val)
        return val

    @staticmethod
    def is_valid_format(val, typeData, default = None):
        if typeData in ["int", "Int"]:
            return Utils.isInt(val)
        elif typeData in ["float", "Float"]:
            return Utils.isFloat(val)
        elif typeData in ["decimal", "Decimal"]:
            return Utils.isDecimal(val)
        elif typeData in ["str"]:
            return Utils.isStr(val)
        elif typeData in ["txt"]:
            return Utils.isTxt(val)
        elif typeData in ["dict"]:
            return Utils.isDict(val)
        elif typeData in ["list"]:
            return Utils.isList(val)
        return default

    @staticmethod
    def intToFormattedString(nb):
        if Utils.isInt(nb):
            if nb < 10 and nb >= 0:
                return "0"+str(nb)
            return str(nb)
        return str(0)
    
    @staticmethod
    def timeToString(timeTf):
        """
            Format Timstamp unix to string
        """
        if timeTf and timeTf is not None:
            try:
                timeTf = Decimal(timeTf)
                return time.strftime('%d/%m/%Y %H:%M:%S',time.localtime(timeTf))
            except Exception:
                return None
        
        return None
    
    @staticmethod
    def stringToTime(text, formatF, default=None):
        """
            Format Timstamp unix to string
        """
        if type(text) is str and type(formatF) is str:
            try:
                return time.mktime(time.strptime(text, formatF))

            except Exception:
                return default
        return default

    @staticmethod
    def getTimeSearch(timeB, timeSearch='23:59:59'):
        if Utils.isInt(timeB):
            try:
                sTime = time.gmtime(timeB)
                return time.mktime(time.strptime(str(sTime[2])+'-'+str(sTime[1])+'-'+str(sTime[0])+' '+str(timeSearch), "%d-%m-%Y %H:%M:%S"))
            except Exception:
                return None
        return None
    
    @staticmethod
    def boolToIntText(boolT):
        r = Utils.str_to_bool(boolT)
        if boolT:
            return "1"
        return "0"
    
    @staticmethod
    def boolToOnOff(boolT):
        r = Utils.str_to_bool(boolT)
        if boolT:
            return "On"
        return "Off"

    @staticmethod
    def boolToStrState(boolT):
        r = Utils.str_to_bool(boolT)
        if boolT:
            return "Ok"
        return "Error"

    @staticmethod
    def stringToIntBool(text, default=False):
        r = Utils.str_to_bool(text)
        if r == True:
            return 1
        elif r == False:
            return 0
        return default
    
    @staticmethod
    def stringToFloat(text, default=0.0):
        if type(text) is str:
            try:
                text = text.replace(',', '.')
                return Decimal(text)
            except Exception:
                return default
        return default

    @staticmethod
    def getJsonData(data):
        """
            Load json data from string
                str()  - data  : String to load

                return dict()  : Dict of loaded data or None

        """
        dataR = None
        try:
            dataR = json.loads(data)
        except Exception:
            #print("Exception - getJsonData : "+str(ex))
            dataR = None

        return dataR

    @staticmethod
    def setJsonData(data):
        """
            Dump json data to string
                dict()  - data  : Dict to dump to json sting

                return str()  : String of dumped data or None

        """
        lsr = "dataTools::setJsonData"
        dataR = None
        try:
            dataR = json.dumps(data)
        except Exception:
            return dataR

        return dataR
    
    @staticmethod
    def get_keys_from_dict(data, list_keys):
        res = dict()
        if Utils.isDict(data) and Utils.isList(list_keys):

            for key in list_keys:
                if Utils.isStr(key) and key in data:
                    res[key] = data.get(key)
        return res
    
    @staticmethod
    def del_keys_from_dict(data, list_keys):
        
        if Utils.isDict(data) and Utils.isList(list_keys):

            for key in list_keys:
                if Utils.isTxt(key) and key in data:
                    del data[key]
        return data

    ##################
    #
    # Operating System
    #
    #########
    @staticmethod
    def get_operating_system():
        try:
            platform = sys.platform
            if platform == "linux" or platform == "linux2":
                return "Linux"
            elif platform == "darwin":
                return "MacOs"
            elif platform == "win32":
                return "Windows"
        except Exception as ex:
            return None
        return None
    
    @staticmethod
    def get_operating_system_type():
        try:
            op = Utils.get_operating_system()
            if op == "Linux" or op == "MacOs":
                return ("unix", op)
            elif op == "Windows":
                return ("win32", op)
        except Exception as ex:
            return None
        return None
    
    @staticmethod
    def get_system_language():
        try:
            platform = Utils.get_operating_system()
            if platform == "Linux" or platform == "MacOs":
                lang = os.getenv('LANG')
                return lang
            elif platform == "Windows":
                windll = ctypes.windll.kernel32
                lang = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
                return lang
        except Exception as ex:
            return None
        return None

