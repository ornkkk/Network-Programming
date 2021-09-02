#!/usr/bin/python3

import sys
import getopt
import pcapy
from impacket.ImpactDecoder import EthDecoder


dev = "eth0"
filter = "arp"
decoder = EthDecoder()

def handlePacket(hdr, data):
    """
    This function will be callled for every packet
    and just print it.

    We use EthDecoder here instead of ArpDecoder,
    because the PCAP filter can be specified by the 
    user with the use of the -f parameter.
    """
    print(decoder.decode(data))


def usage():
    print(sys.argv[0] + " -i <dev> -f <pcap_fiter>")
    sys.exit(1)

#Parsing parameter
try:
    cmdOpts = "f:i:"
    opts, args = getopt.getopt(sys.argv[1:], cmdOpts)
except getopt.GetoptError:
    usage()

for opt in opts:
    if opt[0] == "-f":
        filter = opt[1]
    elif opt[0] == "-i":
        dev = opt[1]
    else:
        usage()

#Open device in promisc mode
pcap = pcapy.open_live(dev, 1500, 0, 100) #-->(device, snaplen(bytes), promiscmode(On/Off), timeout(ms))

#Set pcap filter
pcap.setfilter(filter)

#Start Sniffing
pcap.loop(0, handlePacket)
