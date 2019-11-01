#! /usr/bin/env python3
# Python script to read DSMR v.5.0 P1 telegrams and store telegrams in redis

import re
import serial
import crcmod.predefined
from serial import Serial
from datetime import datetime

p1 = serial.Serial()

p1.baudrate = 115200
p1.bytesize = serial.EIGHTBITS
p1.parity = serial.PARITY_NONE
p1.stopbits = serial.STOPBITS_ONE
p1.xonxoff = 1
p1.rtscts = 0
p1.timeout = 12
p1.port = "/dev/ttyUSB0"
p1.close()

# End of telegram, CR/LF followed by exclamation mark
telegramPattern = re.compile(b'\r\n(?=!)')
# check telegram with crc16; crc16-ibm (x16 + x15 + x2 + 1)reversed (0xA001)
crc16 = crcmod.predefined.mkPredefinedCrcFun('crc16')

telegram = ''
checksumFound = False
checksumCorrect = False


while True:
    try:
        try:
            # Open serial port
            p1.open()
            checksumFound = False
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__), ex.args
            print(message)
            sys.exit("Error on opening %s. Aborted." % p1.name)

        while not checksumFound:
            # construct telegram from lines
            telegramLine = p1.readline()
            if re.match(b'(?=!)', telegramLine):
                telegram = telegram + telegramLine
                checksumFound = True
            else:
                telegram = telegram + telegramLine

                #line 51 raises exception: TypeError: can only concatenate str (not "bytes") to str

    except Exception as ex:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__), ex.args
        print(message)
        print("Problem %s, continuing ...") % ex

    # Close serial port
    try:
        p1.close()
    except:
        sys.exit("Serial port made a booboo. %s. Aborted." % p1.name)

    # Complete telegram received. Check telegram and store in redis
    for m in telegramPattern.finditer(telegram):
        # extract checksum and integerize... :)
        checksumExtracted = int('0x' + telegram[m.end() + 1:].decode('ascii'), 16)
        # calculate checksum over telegram including exclamation maek
        checksumCalculated = crc16(telegram[:m.end() + 1])
        if checksumExtracted == checksumCalculated:
            checksumCorrect = True

    if checksumCorrect:
        print("Telegram valid!")

    # while not checksumFound: #Read separate lines from telegram
    #     telegramLine = p1.readline()
    #     print(telegramLine.decode('ascii').strip())
    #     if re.match(b'(?=1-0:1.7.0)',telegramLine):
    #
    #         kw = telegramLine[10:-6]
    #         watt_pos = float(kw) * 1000
    #         watt_pos = int(watt_pos)
    #
    #     if re.match(b'(?=1-0:2.7.0)',telegramLine):
    #
    #         kw = telegramLine[10:-6]
    #         watt_neg = float(kw) * 1000
    #         watt_neg = int(watt_neg)
    #
    #     # Check for end of telegram (exlamation mark)
    #     if re.match(b'(?=!)', telegramLine):
    #         timeStamp = datetime.now() # timestamp complete telegram received
    #         print(timeStamp)
    #         print(watt_pos)
    #         print(watt_neg)
    #         checksumFound = True
    #
    # p1.close()
