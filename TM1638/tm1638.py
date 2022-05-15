#!/usr/bin/env python3
#

import sys
from time import sleep


import spidev as spi

_SPISPEED   = 8000000


def tmclose(d):
    d.close()

def tmopen():
    d = spi.SpiDev()
    try:
        d.open(0,0)
        d.max_speed_hz = _SPISPEED
        d.mode = 0b11
        #d.lsbfirst = True     # not support

        d.xfer([0x5D])  # 0xb8
        d.xfer([0x02])  # 0x40

        # 0xC0
        d.xfer([0x03,] + [0x00 for _ in range(16)])
    except:
        d.close()
        raise

    return d

#           # 0     1     2     3     4     5     6     7
_ADDRMAP = (0x00, 0x40, 0x20, 0x60, 0x10, 0x50, 0x30, 0x70)
def tmwritedata(d, addr, dat):
    d.xfer([0x22])  # 0x44
    # 0xC0
    if addr < 8:
        d.xfer([0x03|_ADDRMAP[addr], dat&0x0FF])
    else: # for led
        d.xfer([0x83|_ADDRMAP[addr&7], dat!=0 and 0x080 or 0])

NUMTAB = (
    #0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07,
    0xFC, 0x60, 0xDA, 0xF2, 0x66, 0xB6, 0xBE, 0xE0,
    #0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71,
    0xFE, 0xF6, 0xEE, 0x3E, 0x9C, 0x7A, 0x9E, 0x8E,
)

_LASTSTR = None
def disptime(d):
    import time
    import binascii as ba

    global _LASTSTR

    x = time.strftime("%H-%M-%S")
    if x == _LASTSTR:
        return

    _LASTSTR = x

    for i in range(8):
        if x[i]=='-':
            tmwritedata(d, i, 0x02)
            continue

        tmwritedata(d, i, NUMTAB[ord(x[i])-0x30])

_LOGLEVEL = ("<6>", "<5>", "<4>", "<3>") # for syslog

if __name__ == "__main__":

    d = None
    try:
        d = tmopen()

        print(_LOGLEVEL[0],"max_speed_hz =", d.max_speed_hz)
        sys.stdout.flush()

        i = 0
        while True:
            sleep(0.1)
            disptime(d)

            for p in range(8):
                tmwritedata(d, 8|p, i&(1<<p))
            i += 1

        sleep(3)

    finally:
        if d: tmclose(d)


