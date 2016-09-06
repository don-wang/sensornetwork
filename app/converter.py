# encoding=utf-8
import serial
import binascii
import datetime
import time
import copy
import math
#import numpy as np

RESP_HEAD = binascii.a2b_hex("4C")
module = 1
if module == 1: #USB
    bufSize = 54
    pmvH = 2
    pmvL = 3
    tempH = 10
    tempL = 11
    humiH = 46
    humiL = 47
    lightH = 48
    lightL = 49
    presH = 50
    presL = 51
    flowXH = 6
    flowXL = 7
    flowYH = 8
    flowYL = 9
    radiH = 12
    radiL = 13
    irH = 14
    irL = 15
    batH = 52
    batL = 53
elif module == 2: #Wireless
    bufSize = 70
    pmvH = 16
    pmvL = 17
    tempH = 24
    tempL = 25
    humiH = 60
    humiL = 61
    lightH = 62
    lightL = 63
    presH = 64
    presL = 65
    flowXH = 20
    flowXL = 21
    flowYH = 22
    flowYL = 23
    radiH = 26
    radiL = 27
    irH = 28
    irL = 29
    batH = 66
    batL = 67

def serialRequest(ser):
    ser.write(RESP_HEAD)

def combineHL(h, l):
    return ((h << 8) | l)

def conv24bit(buf):
    s = (buf[0] << 16) + (buf[1] << 8) + buf[2]
    return s

def conv16bit(buf):
    s = (buf[0] << 8) + buf[1];
    return s


def movingaverage(x, window):
    y = np.empty(len(x)-window+1)
    for i in range(len(y)):
        y[i] = np.sum(x[i:i+window])/window
    return y


def meterFromPa(pa):
    hpa = pa/100
    ret = math.pow(PRES_HP0 / hpa, 1 / PRES_PDEN) - 1
    ret = ret * (Tnow + PRES_TNOM)
    ret = ret / PRES_HDEN + Hnow
    return round(ret, 2)



def parsePkt(seq):
    print seq
    pkt = {}
    pkt['pmv'] = combineHL(seq[pmvH], seq[pmvL]) / 100.0
    pkt['temp'] = combineHL(seq[tempH], seq[tempL]) / 100.0
    pkt['humi'] = combineHL(seq[humiH], seq[humiL]) / 100.0
    pkt['light'] = combineHL(seq[lightH], seq[lightL])
    pkt['pres'] = combineHL(seq[presH], seq[presL]) / 10.0
    pkt['flowX'] = combineHL(seq[flowXH], seq[flowXL]) / 1000.0
    pkt['flowY'] = combineHL(seq[flowYH], seq[flowYL]) / 1000.0
    pkt['flowV'] = math.floor(math.sqrt(pkt['flowX'] * pkt['flowX'] + pkt['flowY'] * pkt['flowY']) * 100)/100
    pkt['radi'] = combineHL(seq[radiH], seq[radiL]) / 100.0
    pkt['ir'] = []
    for x in xrange(0,16):
        pkt['ir'].append(combineHL(seq[(2 * x) + irH], seq[(2 * x) + irL]) / 100.0)


    pkt['bat'] = combineHL(seq[batH], seq[batL]) / 1000.0

    return pkt

def test(a):
    print a
