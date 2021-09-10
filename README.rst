Faulhaber mc5005
============

mc5005.py provides a python module to interface to the Faulhaber MC5005 motion controller via serial interface. 

This module requires the pyserial module which can be installed via

>>> pip install pyserial

You should still setup your motor with Motion Manager first. After that, you can use the Motor class of mc5005.py to control the motor.

Things added: Benno Meier: motor class to control more than 1 motor. 
Theodoros Anagnos: Enable, Disable, Target reached confirmation, I/O port handling and debug. This allows for 
smoother operation of the motors (no movements during start/stop).

The motion_example.py code illustrates the usage of the module.


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
