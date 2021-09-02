#! /usr/bin/python3

from scapy.all import sniff
from scapy.layers.l2 import ARP
from signal import signal, SIGINT
import sys

#arpWatcherDBFile = "/var/cache/arp-watcher.db"
arpWatcherDBFile = "/home/k3/Desktop/arp-watcher.db"
ip_mac = {}

#Save ARP table on shutdown
def sigIntHandler(signum, frame):
    print("Got SIGINT. Saving ARP database...")
    try:
        f = open(arpWatcherDBFile, "w")

        for (ip, mac) in ip_mac.items():
            f.write("{0} {1}\n".format(ip, mac))

        f.close()
        print("Done!!!")

    except IOError:
        print("Cannot write file {}".format(arpWatcherDBFile))
    
    sys.exit(1)

def watchARP(pkt):
    #got is-at pkt(ARP response)
    if pkt[ARP].op == 2:
        print("{0} {1}".format(pkt[ARP].hwsrc, pkt[ARP].psrc))

        if ip_mac.get(pkt[ARP].psrc) == None:
            print("Found new device {0} {1}".format(pkt[ARP].hwsrc, pkt[ARP].psrc))
            ip_mac[pkt[ARP].psrc] = pkt[ARP].hwsrc
        
        elif ip_mac.get(pkt[ARP].psrc) and ip_mac[pkt[ARP].psrc] != pkt[ARP].hwsrc:
            print("{0} has got new ip {1} (old {2})".format(pkt[ARP].hwsrc, pkt[ARP].psrc, ip_mac[pkt[ARP].psrc]))
            ip_mac[pkt[ARP].psrc] = pkt[ARP].hwsrc


signal(SIGINT, sigIntHandler)

if len(sys.argv) < 2:
    print(sys.argv[0] + ": <iface>")
    sys.exit(0)

try:
    fh = open(arpWatcherDBFile, "r")
except IOError:
    print("Cannot read file {}".format(arpWatcherDBFile))
    sys.exit(1)

for line in fh:
    line.rstrip()
    (ip, mac) = line.split(" ")
    ip_mac[ip] = mac

sniff(prn=watchARP, filter="arp", iface=sys.argv[1], store=0)

