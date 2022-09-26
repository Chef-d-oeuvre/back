import NetworkTableManagement as NTM
import NetworkManager
import time

ntmngr = NetworkManager.NetworkHandler(True)
#Create a NetworkTableManagement object
ntm = NTM.NetworkDBManager()
#load the database
ntm.loadDB("NetworkDB.json")
#Create a new device
for devices in ntmngr.GetConnectedDevice():
    if not ntm.IsDeviceExist(devices["ip"]):
        ntm.CreateDevice(devices["ip"], mac=devices["mac"])
#Save the database
ntm.saveDB("NetworkDB.json")
