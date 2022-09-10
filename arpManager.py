from http import client
from typing import Dict
import kamene.all as scapy
import time
import os
import sys
import threading
import socket


class ArpManager:
    def __init__(self, verbose=False):
        #get local ip
        self.localIp = self.GetLocalIp()
        self.verbose = verbose
        self.arpTable = {}
        self.arpTableLock = threading.Lock()
        self.arpTable['00:00:00:00:00:00'] = ''
        if self.verbose:
            #show local ip 
            print("Local IP: " + self.localIp)

    def GetLocalIp(self):
        return socket.gethostbyname(socket.gethostname())

    def GetMac(self, ip):
        pass

    def SpoofTarget(self, ip, gateway):

        #send arp packet to target to spoof it
        arpPacket = scapy.ARP(op=2, pdst=ip, hwdst=self.GetMac(ip), psrc=gateway)
        scapy.send(arpPacket, verbose=False)
        

    def GetNetworkDevices(self, deepLevel : int) -> Dict:
        """
        Get all devices in the network
        deepLevel: define the mask of the network
                     mask      ip range
            1 : 255.255.255.0 -> 256    
            2 : 255.255.0.0   -> 65,536   
            3 : 255.0.0.0     -> 16,777,216 
        warning: more deepLevel = more time to scan and less accuracy
        """

        #target ip is local ip without last octet
        targetIp = self.localIp.split('.')
        targetIp = targetIp[0] + '.' + targetIp[1] + '.' + targetIp[2] + '.' + '1'
        
        #change mask of the network by deepLevel
        if deepLevel == 1:
            target_ip = targetIp +"/24"
        elif deepLevel == 2:
            target_ip = targetIp +"/16"
        elif deepLevel == 3:
            target_ip = targetIp +"/8"
        else:
            ValueError("deepLevel must be between 1 and 3")
        arp = scapy.ARP(pdst=target_ip)
        # create the Ether broadcast packet
        # ff:ff:ff:ff:ff:ff MAC address indicates broadcasting
        ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        # stack them
        packet = ether/arp

        result = scapy.srp(packet, timeout=1, verbose=0)[0]

        # a list of clients, we will fill this in the upcoming loop
        clients = {}
        for sent, received in result:
            # for each response, append ip and mac address to `clients` list
            clients[received.psrc] = received.hwsrc

        return clients

manager = ArpManager(verbose=True)
print(manager.GetNetworkDevices(2))