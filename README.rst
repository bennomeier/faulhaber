Faulhaber mc5005
============

mc5005.py provides a python module to interface to the Faulhaber MC5005 motion controller via serial interface. 

This module requires the pyserial module which can be installed via

>>> pip install pyserial

You should still setup your motor with Motion Manager first. After that, you can use the Motor class of mc5005.py to control the motor.

Things added: Benno Meier: motor class to control more than 1 motor. 
Theodoros Anagnos: Enable, Disable, Target reached confirmation, I/O port handling and debug. This allows for 
smoother operation of the motors (no movements during start/stop).

The following code illustrates the usage of the module:

.. code-block:: python

    import mc5005 as mc
    
    C = mc.Controller("COM4") #setup your port here
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
    Y2 = Motor(C, node = b'\x02')

    X1.setPositionMode()
    Y2.setPositionMode()
    C.printStatus()

    X1.Disable2()
    Y2.Disable2()
    print("Disable Complete.")
    print("Restarting Device.")
    X1.shutDown()
    X1.switchOn()
    X1.enable()
    Y2.shutDown()
    Y2.switchOn()
    Y2.enable()
    print("Restart Complete.")
    C.printStatus()
    print("")

    # print("Enable Device.")
    # X1.Enable2()  #seems that for the 2nd motor does not work the Enable2 function
    # Y2.Enable2()
    # C.printStatus()
    # print("")

    for i in range(3):
        pos = round(i*204800 + 0)
        Y2.positionAbsolute(pos)
        X1.positionAbsolute(pos)
        yt = Y2.TargetReached('y2')
        xt = X1.TargetReached('x1')
        while (yt!=1 and xt!=1):
            time.sleep(0.5)
        print (i)
        time.sleep(0.3)

    X1.Disable2()
    Y2.Disable2()
    # C.SetDigOut(1)
    C.close()


License
-------

MIT License

Copyright (c) 2020 Benno Meier

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
