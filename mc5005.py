""" mc5005.py

A python module to control Faulhaber motors via the MC5005 Motion Controller and serial interface.

- Setup your motor with Motion Manager first. 
- Install pyserial from PyPI

Now you can use this module to control the motor via serial interface.

Copyright (2020) Benno Meier
Licence: MIT
"""


import serial
import struct
import time

STATUS = 0x6041                   # status word
CONTROL = 0x6040                  # control word
TARGET_POS = 0x607A               # target position
OPERATION_MODE = 0x6060           # operation mode
OPERATION_MODE_DISP = 0x6061      # operation mode display


def dump(x):
    return ''.join([type(x).__name__, "('",
                    *['\\x'+'{:02x}'.format(i) for i in x], "')"])


class Motor(object):
    """This class is an interface to a Faulhaber Motor via a 
    MC5005 Motion Controller, using the serial port."""

    def __init__(self, port, baudrate = 115200, timeout = 2):
        """Initialize the interface to the motion controller

        port : Serial port, i.e. "COM4"
        baudrate : Optional keyword argument, preset to 115200
        timeout : Optional keyword argument, preset to 2
        """
        self.ser = serial.Serial(port, baudrate, timeout = timeout)
        self.S = b'\x53'
        self.E = b'\x45'
        self.GET = b'\x01'
        self.SET = b'\x02'

    def close(self):
        self.ser.close()

    def CRC(self, msg):
        """Calculate Cyclic Redundancy Check for message msg.

        msg is the entire command without SOF and EOF."""
        poly = 0xd5
        crc = 0xff
        for byte in msg:
            crc = crc ^ byte
            for _ in range(8):
                if crc & 0x01:
                    crc = ((crc >> 1) ^ poly) 
                else:
                    crc >>= 1
            
        return struct.pack("B", crc)

    def write(self, command):
        """Write command. The length of the command is 
        length of the argument  + 1 for the length byte + 1 for the CRC byte"""
        command = struct.pack("B", len(command) + 2) + command
        command = self.S + command + self.CRC(command) + self.E
        
        #time.sleep(0.2)
        self.ser.flushOutput()
        self.ser.flushInput()

        time.sleep(0.2)
        self.ser.write(command)
        time.sleep(0.2)
        #print(dump(command))
        return self.read()

    def read(self):
        """First read the start bit and the length,
        then read the rest of the transmission."""
        ans = self.ser.read(2)        
        
        try:
            length = ans[1]
        except:
            print("Error:  Ans: ", ans)

        ansAll = ans + self.ser.read(length)
        #print(dump(ansAll))

        #check CRC is correct
        assert self.CRC(ansAll[1:-2]) == struct.pack("B", ansAll[-2])
        
        # ansAll includes self.S, so data starts at position 7
        return ansAll[7:-2]
        
    def readRegister(self, address, node = b'\x01', subindex = 0, debug = False):
        """Read Register 
        address: address of register to be read
        node = b'\x01' optional node
        sudindex = 0 optional subindex
        """    
        command = node + self.GET + int.to_bytes(address, 2, 'little') + int.to_bytes(subindex, 1, 'little')
        if debug: print(dump(command))
        
        return self.write(command)

    def setRegister(self, address, value, length, node = b'\x01', subindex = 0):
        """set register

        address: two byte address of the register, i.e. 0x6040
        value: value of the register
        length: length of the register, in bytes"""
        
        command = ( node + self.SET
                    + int.to_bytes(address, 2, 'little')
                    + int.to_bytes(subindex, 1, 'little')
                    + int.to_bytes(value, length, 'little'))
        self.write(command)

    def getPosition(self, node = b'\x01'):
        answer = self.readRegister(0x6064, node = node, debug = False)
        position = int.from_bytes(answer, byteorder='little', signed = True)
        return position

    def setControlWord(self, word, node = b'\x01'):
        self.setRegister(0x6040, word, 2)

    def setTarget(self, value, node = b'\x01'):
        self.setRegister(0x607a, value, 4)

    def getTargetPositionSource(self):
        return self.readRegister(0x2331, subindex = 4)

    def setPositionMode(self, node = b'\x01'):
        #self.setRegister(0x6060, 1, 1)
        command = node + b'\x02' + b'\x60\x60\x00' + b'\x01'
        self.write(command)

    def getCastedRegister(self, address, subindex = 0):
        return hex(int.from_bytes(M.readRegister(address, subindex = subindex), byteorder='little'))

    def printStatus(self):
        print("Status: ", self.getCastedRegister(STATUS))

    def shutDown(self):
        self.setControlWord(0x0006)

    def switchOn(self):
        self.setControlWord(0x0007)

    def enable(self):
        self.setControlWord(0x000f)

    def positionAbsolute(self, value):
        """set absolute position. Make sure the device is in position mode prior to using this function."""
        M.setTarget(value)
        M.setControlWord(0x0f)
        M.setControlWord(0x3f)

    def positionRelative(self, value):
        """set relative position. Make sure the device is in position mode prior to using this function."""
        M.setTarget(value)
        M.setControlWord(0x0f)
        M.setControlWord(0x7f)
        
if __name__ == "__main__":
    M = Motor("/dev/cu.usbserial-FTYO2YC9")
    print("Device Type: ", M.getCastedRegister(0x1000))
    print("Serial Number: ", M.getCastedRegister(0x1018, subindex = 4))
    print("Status: ", M.getCastedRegister(0x6041))
    print("Modes of Operation: ", M.getCastedRegister(0x6060))
    print("Modes of Operation Display: ", M.getCastedRegister(0x6061))
    print("Producer Heartbeat Time: ", M.getCastedRegister(0x1017))
    print("Actual Program Position: ", M.getCastedRegister(0x3001, subindex = 3))
    print("Actual Program State: ", M.getCastedRegister(0x3001, subindex = 4))
    print("Error State: ", M.getCastedRegister(0x3001, subindex = 8))
    print("Error code: ", M.getCastedRegister(0x3001, subindex = 9))
    print("Motor Type: ", M.getCastedRegister(0x2329, subindex = 0x0b))
    print("Encoder Increments: ", M.getCastedRegister(0x608f, subindex = 1))
    print("Serial Number: ", M.getCastedRegister(0x1018, subindex = 4))
    print("Feed Constant: ", M.getCastedRegister(0x6092, subindex = 1))
    M.printStatus()
    print("\n\nPreparing Device.\n" + "="*20)
    M.setPositionMode()
    M.printStatus()

    print("Restarting Device.")
    M.shutDown()
    M.switchOn()
    M.enable()
    print("Restart Complete.")
    M.printStatus()
    print("")
    # move by 360 degrees in 60 steps:
    for i in range(60):
        pos = round(i*0x4000/60)
        M.positionAbsolute(pos)
        time.sleep(0.3)
        print("Set Position: ", pos, " Read position: ", M.getPosition())
    
    M.close()
    
