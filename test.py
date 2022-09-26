import time
import sys
import NetworkManager

ntwkMng = NetworkManager.NetworkHandler(True)

#create a callback function when a new device connects to the network
def OnConnectedDevice(device):
    print(f"New device connected to the network: {device}")

#call the callback function when a new device connects to the network
ntwkMng.OnConnectedDevice(OnConnectedDevice)
