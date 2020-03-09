#!/usr/bin/env python2
# Python script to retrieve and parse a DSMR telegram from a P1 port
# Stores output in redis streams

from __future__ import print_function
from __future__ import unicode_literals

#from builtins import map
#from builtins import str

import re
import sys
import serial
import crcmod.predefined
from datetime import datetime, timedelta
import redis
import configparser

# load settings file
configFile = configparser.ConfigParser()
configFile.read('settings.conf')

# Debugging settings
production = configFile.getboolean('environment','production')
debugging = configFile['environment']['debugging']   # Show extra output

# redis server settings
redisHost = configFile['redisServer']['host']
redisPort = configFile['redisServer']['port']
redisDb = configFile['redisServer']['db']
redisConn = redis.Redis(host=redisHost, port=redisPort, db=redisDb)
redisStream = configFile['redisServer']['streamName']

# DSMR interesting codes
gasMeter = configFile['p1Device']['gasMeter']
interestingCodes = {
    '0-0:1.0.0': 'timestampTelegramUtc',
    '1-0:1.8.1': 'positiveActiveEnergyTariffT1',
    '1-0:1.8.2': 'positiveActiveEnergyTariffT2',
    '1-0:2.8.1': 'negativeActiveEnergyTariffT1',
    '1-0:2.8.2': 'negativeActiveEnergyTariffT2',
    '0-0:96.14.0': 'tariffIndicator',
    '1-0:1.7.0': 'positiveActivePower',
    '1-0:2.7.0': 'negativeActivePower',
#    '0-0:17.0.0': 'The actual threshold electricity in kW',
#    '0-0:96.3.10': 'Switch position electricity',
#    '0-0:96.7.21': 'Number of power failures in any phase',
#    '0-0:96.7.9': 'Number of long power failures in any phase',
#    '1-0:32.32.0': 'Number of voltage sags in phase L1',
#    '1-0:52.32.0': 'Number of voltage sags in phase L2',
#    '1-0:72:32.0': 'Number of voltage sags in phase L3',
#    '1-0:32.36.0': 'Number of voltage swells in phase L1',
#    '1-0:52.36.0': 'Number of voltage swells in phase L2',
#    '1-0:72.36.0': 'Number of voltage swells in phase L3',
    '1-0:31.7.0': 'instantaneousCurrentPhaseL1',
    '1-0:32.7.0': 'instantaneousVoltagePhaseL1',
    '1-0:21.7.0': 'instantaneousPositiveActivePowerPhaseL1',
    '1-0:22.7.0': 'instantaneousNegativeActivePowerPhaseL1',
    '1-0:51.7.0': 'instantaneousCurrentPhaseL2',
    '1-0:52.7.0': 'instantaneousVoltagePhaseL2',
    '1-0:41.7.0': 'instantaneousPositiveActivePowerPhaseL2',
    '1-0:42.7.0': 'instantaneousNegativeActivePowerPhaseL2',
    '1-0:71.7.0': 'instantaneousCurrentPhaseL3',
    '1-0:72.7.0': 'instantaneousVoltagePhaseL3',
    '1-0:61.7.0': 'instantaneousPositiveActivePowerPhaseL3',
    '1-0:62.7.0': 'instantaneousNegativeActivePowerPhaseL3',
#    '0-'+gasMeter+':24.2.1': 'lastValueTemperatureCorrectedGas'
}

# descibe what maxLen does
maxLen = max(list(map(len,list(interestingCodes.values()))))

# Program variables
# The true telegram ends with an exclamation mark after a CR/LF
pattern = re.compile(b'\r\n(?=!)')
# According to the DSMR spec, we need to check a CRC16
crc16 = crcmod.predefined.mkPredefinedCrcFun('crc16')
# Create an empty telegram
telegram = ''
checksumFound = False
goodChecksum = False

if production:
    #Serial port configuration
    p1 = serial.Serial()
    p1.baudrate = configFile['p1Device']['baudrate']
    p1.bytesize = serial.EIGHTBITS
    p1.parity = serial.PARITY_NONE
    p1.stopbits = serial.STOPBITS_ONE
    p1.xonxoff = configFile['p1Device']['xonxoff']
    p1.rtscts = configFile['p1Device']['rtscts']
    p1.timeout = 12
    p1.port = configFile['p1Device']['port']
else:
    print("Running in test mode")#import datetime
    # Testing
    p1 = open(configFile['environment']['testFile'], 'rb')

while True:
    try:
        # Read in all the lines until we find the checksum (line starting with an exclamation mark)
        if production:
            #Open serial port
            try:
                p1.open()
                telegram = ''
                checksumFound = False
            except Exception as ex:
                template = "An exception of type {0} occured. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                sys.exit("Error on opening %s. Program aborted." % p1.name)
        else:
            telegram = ''
            checksumFound = False
        while not checksumFound:
            # Read in a line
            telegramLine = p1.readline()
            if debugging == 2:
                print(telegramLine.decode('ascii').strip())
            # Check if it matches the checksum line (! at start)
            if re.match(b'(?=!)', telegramLine):
                telegram = telegram + telegramLine
                if debugging == 1:
                    print('Found checksum!')
                checksumFound = True
            else:
                telegram = telegram + telegramLine

    except Exception as ex:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        print(("There was a problem %s, continuing...") % ex)
    #Close serial port
    if production:
        try:
            p1.close()
        except Exception as exs:
            sys.exit("Oops %s. Program aborted." % p1.name)
    # We have a complete telegram, now we can process it.
    # Look for the checksum in the telegram
    for m in pattern.finditer(telegram):
        # Remove the exclamation mark from the checksum,
        # and make an integer out of it.
        givenChecksum = int('0x' + telegram[m.end() + 1:].decode('ascii'), 16)
        # The exclamation mark is also part of the text to be CRC16'd
        calculatedChecksum = crc16(telegram[:m.end() + 1])
        if givenChecksum == calculatedChecksum:
            goodChecksum = True
    if goodChecksum:
        if debugging == 1:
            print("Good checksum!")
        # Store the vaules in a dictionary
        telegramValues = dict()
        # Split the telegram into lines and iterate over them
        for telegramLine in telegram.split(b'\r\n'):
            # Split the OBIS code from the value
            # The lines with a OBIS code start with a number
            if re.match(b'\d', telegramLine):
                if debugging == 3:
                    print(telegramLine)
                # The values are enclosed with parenthesis
                # Find the location of the first opening parenthesis,
                # and store all split lines
                if debugging == 2:
                    print(telegramLine)
                if debugging == 3:
                    print(re.split(b'(\()', telegramLine))
                # You can't put a list in a dict TODO better solution
                code = ''.join(re.split(b'(\()', telegramLine)[:1])
                value = ''.join(re.split(b'(\()', telegramLine)[1:])
                telegramValues[code] = value

        # Print the lines to screen
        telegramRedis = {}
        for code, value in sorted(telegramValues.items()):
            if code in interestingCodes:
                # Cleanup value
                # strip timestamp of S or W
                if code == '0-0:1.0.0':
                    # value = int(value.lstrip(b'\(').rstrip(b'\)*SW'))
                    # convert to UTC
                    # 191119225041W = %y%m%d%H%M%S + S = SUMMER / W = WINTER
                    # S = UTC + 2; W = UTC + 1
                    value = str(value.lstrip(b'\(').rstrip(b'\)*'))
                    if 'S' in value:
                        value = str(value.rstrip(b'*S'))
                        value = datetime.strptime(value, '%y%m%d%H%M%S')
                        value = value - timedelta(hours = 2)
                        telegramRedis[str(code)] = str(value)
                    else:
                        value = str(value.rstrip(b'*W'))
                        value = datetime.strptime(value, '%y%m%d%H%M%S')
                        value = value - timedelta(hours = 1)
                        telegramRedis[str(code)] = str(value)

                # Gas needs another way to cleanup
#                if 'm3' in value:
#                        (time,value) = re.findall('\((.*?)\)',value)
#                        value = float(value.lstrip(b'\(').rstrip(b'\)*m3'))
                else:
                        value = float(value.lstrip(b'\(').rstrip(b'\)*kWhAV'))
                        telegramRedis[str(code)] = value

        if production:
            redisConn.xadd(redisStream, telegramRedis, id='*', maxlen=3600, approximate=True)
        else:
            print(telegramRedis)
            break
#        print('Values added to Redis')
