# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 08:51:52 2021

test to show the faulhaber function through python
@author: tanagnos
"""

import mc5005 as mc
import time

RefOffset = 204800  #Faulhaber motor steps per 1mm using certain incremental encoder TTL signal for position

def MoveAbsWait(Pos_X, Pos_Y, Zero_X=0,Zero_Y=0):
    x_pos = round(-Pos_X*RefOffset+Zero_X)
    y_pos = round(-Pos_Y*RefOffset+Zero_Y)
    print (x_pos,y_pos)
    mc.X1.positionAbsolute(x_pos)
    mc.Y1.positionAbsolute(y_pos)
    xt = mc.X1.getPosition()
    yt = mc.Y1.getPosition()
    # print(xt,yt)
    while abs(x_pos-xt)>=5 or abs(y_pos-yt)>=5:
        time.sleep(0.5)
        xt = mc.X1.getPosition()
        yt = mc.Y1.getPosition()
        # print(xt,yt)

Zero_X = 0
Zero_Y = 0

MoveAbsWait(6,6,Zero_X, Zero_Y)
time.sleep(3)   #waits 3 sec
MoveAbsWait(0,0,Zero_X, Zero_Y)

mc.X1.Disable2()    #pwr off motors
mc.Y1.Disable2()

mc.C.close()    #this command closes the port, make sure you do it before shutting down

