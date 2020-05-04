Faulhaber mc5005
============

mc5005.py provides a python module to interface to the Faulhaber MC5005 motion controller via serial interface. 

This module requires the pyserial module which can be installed via
>>> pip install pyserial

You should still setup your motor with Motion Manager first. After that, you can use the Motor class of mc5005.py to control the motor.

The following code illustrates the usage of the module:

.. code-block:: python

    from mc5005 import Motor
    
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
