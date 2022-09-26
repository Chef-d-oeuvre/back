from concurrent.futures import thread
import kamene.all as scapy
import socket
import threading
import time

class NetworkHandler():
    def __init__(self, verbose=False):
        self.verbose = verbose
        #scan 3time for connected devices at the startup
        self.connectedDevices = []
        if self.verbose:
            print("Scanning for connected devices...")
        for x in range(1, 4):
            #merge the list of connected devices
            self.connectedDevices += self.GetConnectedDevice()
            if self.verbose:
                print(f"{x}/3")
        if self.verbose:
            print("Connected devices scanned")
            print(self.connectedDevices)


    def GetLocalIP(self):
        return socket.gethostbyname(socket.gethostname())

    def GetConnectedDevice(self):
        """
        Get the connected devices on the local network
        """
        #get the local ip
        localIp = self.GetLocalIP()
        #get the local ip range
        localIpRange = localIp.split(".")
        localIpRange.pop()
        localIpRange = ".".join(localIpRange)
        localIpRange += ".1/24"
        #scan the local network
        arpRequest = scapy.ARP(pdst=localIpRange)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arpRequestBroadcast = broadcast/arpRequest
        answeredList = scapy.srp(arpRequestBroadcast, timeout=1, verbose=False)[0]
        #get the ip and mac address of the connected devices
        connectedDevices = []
        for element in answeredList:
            deviceDict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
            connectedDevices.append(deviceDict)
        return connectedDevices

    def OnConnectedDevice(self, callback):
        """
        Call the callback function when a new device connects to the network
        """
        def Scanner():
            while True:
                #get the connected devices
                connectedDevices = self.GetConnectedDevice()
                #check if there is a new device
                for device in connectedDevices:
                    if device not in self.connectedDevices:
                        self.connectedDevices.append(device)
                        callback(device)
                time.sleep(5)
        threading.Thread(target=Scanner).start()

    def getHostName(self, ip):
        """
        Get the hostname of a device
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None