from http.client import NOT_IMPLEMENTED
import NetworkTableManagement as NTM
import NetworkManager
import time
import threading


CustomConfiguration = {
    "DefaultGateway": "192.168.144.86",
    "baseIpRange": "24",
    "baseIP": "192.168.144.",
    "LocalIP": "192.168.144.116"
}

ntmngr = NetworkManager.NetworkHandler(True, False, CustomConfiguration=CustomConfiguration)
#Create a NetworkTableManagement object
ntm = NTM.NetworkDBManager()
#load the database
ntm.loadDB("NetworkDB.json")
#Create a new device
for devices in ntmngr.GetCompleteDevicesList():
    if not ntm.IsDeviceExist(devices["ip"]):
        ntm.CreateDevice(ip=devices["ip"], mac=devices["mac"], hostname=devices["hostname"])
#Save the database
ntm.saveDB("NetworkDB.json")

#ask the user to block a device or unblock
while True:
    print("1. Block a device")
    print("2. Unblock a device")
    print("3. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        ip = input("Enter the ip of the device you want to block: ")
        if ntm.IsDeviceExist(ip):
            ntm.UpdateDevice(ip, blocked=True, blockedReason="User blocked it", blockedBy="User")
            ntm.saveDB("NetworkDB.json")
            print("Device blocked")
        else:
            print("Device not found")
    elif choice == "2":
        ip = input("Enter the ip of the device you want to unblock: ")
        if ntm.IsDeviceExist(ip):
            ntm.UpdateDevice(ip, blocked=False, blockedReason="", blockedBy="")
            ntmngr.DeUnblockDevice(ip)
            ntm.saveDB("NetworkDB.json")
            print("Device unblocked")
        else:
            print("Device not found")
    elif choice == "3":
        break
    else:
        print("Invalid choice")
