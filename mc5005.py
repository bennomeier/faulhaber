""" mc5005.py
A python module to control Faulhaber motors via the MC5005 Motion Controller and serial interface.
- Setup your motor with Motion Manager first. 
- Install pyserial from PyPI
Now you can use this module to control the motor via serial interface.

Copyright (2020) Benno Meier

Licence: MIT

Adapted by Theodoros Anagnos on 4/7/2021. Now more than 1 motor can be controlled through
the same PORT (@Benno Meier work) and can be be operated in semi-synchronous mode.

"""
import serial
import struct
import time

OPERATION_MODE = 0x6060           # operation mode
OPERATION_MODE_DISP = 0x6061      # operation mode display

def dump(x):
    return ''.join([type(x).__name__, "('",
                    *['\\x'+'{:02x}'.format(i) for i in x], "')"])


class Controller(object):
    """This class represents a Faulhaber MC5005 Motion Controller
    It handles all the communication with the controller, and needs
    to be given to motor objects on initialization.
    """

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

        # time.sleep(0.2)
        self.ser.flushOutput()
        self.ser.flushInput()
        time.sleep(0.)
        self.ser.write(command)
        time.sleep(0.)

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
        if debug: 
            print(dump(command))
        return self.write(command)

    def setRegister(self, address, value, length, node = b'\x01', subindex = 0):
        """set register address: two byte address of the register, i.e. 0x6040
        value: value of the register length: length of the register, in bytes"""

        command = ( node + self.SET
                    + int.to_bytes(address, 2, 'little')
                    + int.to_bytes(subindex, 1, 'little')
                    + int.to_bytes(value, length, 'little'))

        self.write(command)

    def getCastedRegister(self, address, subindex = 0):
        return hex(int.from_bytes(C.readRegister(address, subindex = subindex), byteorder='little'))

    def printStatus(self):
        print("Status: ", self.getCastedRegister(0x6041))

    #--------------------------------------------
    # SetDigOut(PinNr)
    # Will set the digital output 1 or 2 to high. Shutdown hall sensors. 
    #--------------------------------------------  
    def SetDigOut(self, PinNr):
        if PinNr==1:
            self.setRegister(0x2311, 0xfd, 2, node = b'\x01',subindex=4)

        if PinNr==2:
            self.setRegister(0x2311, 0xf7, 2, node = b'\x01',subindex=4)

    #--------------------------------------------
    # ClearDigOut(PinNr)
    # Will clear the digital output 1 or 2 to low. Switch on hall sensors.
    #--------------------------------------------       
    def ClearDigOut(self, PinNr):
        if PinNr==1:
            self.setRegister(0x2311, 0xfc, 2, node = b'\x01',subindex=4)

        if PinNr==2:
            self.setRegister(0x2311, 0xf3, 2, node = b'\x01',subindex=4)


class Motor(Controller):
    """This class is an interface to a Faulhaber Motor. You need to give it a controller
     object upon initialization, and optionally the node to which the motor connects."""

    def __init__(self, controller, node = b'\x01'):
        self.controller = controller
        self.node = node

    def getPosition(self):
        answer = self.controller.readRegister(0x6064, node = self.node, debug = False)
        position = int.from_bytes(answer, byteorder='little', signed = True)
        return position

    def setControlWord(self, word):
        self.controller.setRegister(0x6040, word, 2, node = self.node)

    def setTarget(self, value):
        self.controller.setRegister(0x607a, value, 4, node = self.node)

    def getTargetPositionSource(self):
        return self.controller.readRegister(0x2331, subindex = 4, node = self.node)

    def setPositionMode(self):
        #self.setRegister(0x6060, 1, 1)
        command = self.node + b'\x02' + b'\x60\x60\x00' + b'\x01'
        self.controller.write(command)

    def shutDown(self):
        self.setControlWord(0x06)

    def switchOn(self):
        self.setControlWord(0x07)

    def enable(self):
        self.setControlWord(0x0f)

    def DisableVoltage(self):
        self.setControlWord(0x00)

    def positionAbsolute(self, value):
        """set absolute position. Make sure the device is in position mode prior to using 
        this function."""
        self.setTarget(value)
        self.setControlWord(0x0f)
        self.setControlWord(0x3f)


    def positionRelative(self, value):
        """set relative position. Make sure the device is in position mode prior to using this function."""
        self.setTarget(value)
        self.setControlWord(0x0f)
        self.setControlWord(0x7f)

    """
    --------------------------------------------
     WaitPos()
     can be called directly after either the
     positionAbsolute or the positionRelative functions.
     Will wait for the InPos Bit 0x400 being set
     will NOT check FOR a rising edge! Adapted from FA.
    """
    def TargetReached(self,node):
        stop = 0
        while stop == 0:
            if (int(self.getCastedRegister(0x6041),base=16) & 0x400) == 0x400: #Target Reached set
                stop=1
        return (stop) #flag to continue

    """
    --------------------------------------------
     Enable()
     will start the CiA 402 state machine or re-enable
     the control. Returns only after the OperationEnabled
     state is reached. Adapted from FA.
    --------------------------------------------
    """
    def Enable2(self):
        EnState = 0  #reset the local step counter
        CiAStatusword = int(self.getCastedRegister(0x6041),base=16) #initial check of the status word
        CiAStatusMask = 0x6f
        CiAStatus = CiAStatusword & CiAStatusMask
        CiAStatus_OperationEnabled = 0x27
        CiAStatus_SwitchOnDisabled = 0x40
        CiAStatus_QuickStop = 0x07
        #check for being in stopped mode
        if CiAStatus == CiAStatus_QuickStop:
            self.setControlWord(0x0f)   #Enable Operation
            EnState = 1
        elif CiAStatus == CiAStatus_OperationEnabled:   #drive is already enabled               
            EnState = 2
        elif CiAStatus != CiAStatus_SwitchOnDisabled: # otherwise it's safe to disable first
            # we need to send a shutdown first
            self.setControlWord(0x00)   #Controlword = CiACmdDisableVoltage

        while EnState != 2:
            CiAStatusword = int(self.getCastedRegister(0x6041),base=16)
            CiAStatusMask = 0x6f
            CiAStatus = (CiAStatusword & CiAStatusMask) #cyclically check the status word
            if EnState == 0:
                if CiAStatus == 0x40:
                #send the enable signature
                    self.setControlWord(0x06) #CiACmdShutdown
                    self.setControlWord(0x0f) #CiACmdEnableOperation
                    #now wait for being enabled
                    EnState = 1

            elif EnState == 1:
                #wait for enabled
                if CiAStatus == CiAStatus_OperationEnabled:
                    EnState = 2
    """
    --------------------------------------------
     Disable()
     Will stop the drive and shut the 
     CiA 402 state machine down TO the initial state
     returns only after the initial state (Switch On Disabled)
     is reached. Adapted from FA.
    ---------------------------------------------
    """
    def Disable2(self):
        DiState = 0 #reset the local step counter
        CiAStatusword = int(self.getCastedRegister(0x6041),base=16) #initial check of the status word
        CiAStatusMask = 0x6f
        CiAStatus = CiAStatusword & CiAStatusMask
        CiAStatus_OperationEnabled = 0x27
        if CiAStatus == CiAStatus_OperationEnabled:
            #send a shutdown command first to stop the motor
            self.setControlWord(0x07) #CiACmdDisable
            DiState = 1
        else:
            #otherwise the disable voltage is the next command
            #out of quick-stop or switched on.
            DiState = 2

        while DiState != 4:
            CiAStatusword = int(self.getCastedRegister(0x6041),base=16)
            CiAStatusMask = 0x6f
            CiAStatus = (CiAStatusword & CiAStatusMask) #cyclically check the status
            if DiState == 1:
                if CiAStatus == 0x23:
                    #only now it's safe to send the disable voltage command
                    DiState = 2

            elif DiState == 2:
                #wait for enabled
                self.setControlWord(0x00) #CiACmdDisableVoltage
                DiState = 3

            elif DiState == 3:
                #wait for final state
                if CiAStatus == 0x40:
                    DiState = 4



if __name__ == "__main__":
    C = Controller("COM8") #setup your port here
    # C.ClearDigOut(1)  #I/O port of Faulhaber connected with a relay to power on/off the hall sensors.
    print("Device Type: ", C.getCastedRegister(0x1000))
    print("Serial Number: ", C.getCastedRegister(0x1018, subindex = 4))
    print("Status: ", C.getCastedRegister(0x6041))
    print("Modes of Operation: ", C.getCastedRegister(0x6060))
    print("Modes of Operation Display: ", C.getCastedRegister(0x6061))
    print("Producer Heartbeat Time: ", C.getCastedRegister(0x1017))
    print("Actual Program Position: ", C.getCastedRegister(0x3001, subindex = 3))
    print("Actual Program State: ", C.getCastedRegister(0x3001, subindex = 4))
    print("Error State: ", C.getCastedRegister(0x3001, subindex = 8))
    print("Error code: ", C.getCastedRegister(0x3001, subindex = 9))
    print("Motor Type: ", C.getCastedRegister(0x2329, subindex = 0x0b))
    print("Encoder Increments: ", C.getCastedRegister(0x608f, subindex = 1))
    print("Serial Number: ", C.getCastedRegister(0x1018, subindex = 4))
    print("Feed Constant: ", C.getCastedRegister(0x6092, subindex = 1))
    
    C.printStatus()

    print("\n\nPreparing Device.\n" + "="*20)

    X1 = Motor(C, node = b'\x01')
    Y1 = Motor(C, node = b'\x02')

    X1.setPositionMode()
    Y1.setPositionMode()
    C.printStatus()

    X1.Disable2()
    Y1.Disable2()
    print("Disable Complete.")
    print("Restarting Device.")
    X1.shutDown()
    X1.switchOn()
    X1.enable()
    Y1.shutDown()
    Y1.switchOn()
    Y1.enable()
    print("Restart Complete.")
    C.printStatus()
    print("")

    # print("Enable Device.")
    # X1.Enable2()  #seems that for the 2nd motor does not work the Enable2 function
    # Y2.Enable2()
    # C.printStatus()
    # print("")

    # for i in range(3):
    #     pos = round(i*204800 + 0)
    #     Y2.positionAbsolute(pos)
    #     X1.positionAbsolute(pos)
    #     yt = Y2.TargetReached('y2')
    #     xt = X1.TargetReached('x1')
    #     while (yt!=1 and xt!=1):
    #         time.sleep(0.5)
    #     print (i)
    #     time.sleep(0.3)

    # X1.Disable2()
    # Y2.Disable2()
    # # C.SetDigOut(1)
    # C.close()

