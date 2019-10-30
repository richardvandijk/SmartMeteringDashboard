#! /usr/bin/env python
# Python script to read DSMR v.5.0 P1 telegrams

import re
import serial
from serial import Serial
from datetime import datetime

p1 = serial.Serial()

p1.baudrate = 115200
p1.bytesize = serial.EIGHTBITS
p1.parity = serial.PARITY_NONE
p1.stopbits = serial.STOPBITS_ONE
p1.xonxoff = 0
p1.rtscts = 0
p1.timeout = 12
p1.port = "/dev/ttyUSB0"
p1.close()
 
while True:
    p1.open()
    checksumFound = False

    while not checksumFound: #Read separate lines from telegram
        telegramLine = p1.readline()
        print(telegramLine.decode('ascii').strip())
        if re.match(b'(?=1-0:1.7.0)',telegramLine):
            
            kw = telegramLine[10:-6]
            watt_pos = float(kw) * 1000
            watt_pos = int(watt_pos)
            
        if re.match(b'(?=1-0:2.7.0)',telegramLine):
         
            kw = telegramLine[10:-6]
            watt_neg = float(kw) * 1000
            watt_neg = int(watt_neg)            
 
        # Check for end of telegram (exlamation mark)
        if re.match(b'(?=!)', telegramLine):
            timeStamp = datetime.now() # timestamp complete telegram received
            print(timeStamp)
            print(watt_pos)
            print(watt_neg)
            checksumFound = True
    
    p1.close()
