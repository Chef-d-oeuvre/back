import json
import colorama
colorama.init()
class NetworkDBManager:
    def __init__(self):
        self.baseDB = {}
        self.dummyHost = {"hostname":"", "mac":"", "blocked":False, "blockedReason":"", "blockedBy":"", "VirtualMachineAcces":False}
    def CreateDevice(self, ip,hostname="", mac=""):
        if ip in self.baseDB:
            return False
        else:
            #create a new device
            dummy = self.dummyHost
            dummy["hostname"] = hostname
            dummy["mac"] = mac
            self.baseDB[ip] = dummy
            return True
    def IsDeviceExist(self, ip):
        if ip in self.baseDB:
            return True
        else:
            return False
    def UpdateDevice(self, ip, hostname="", mac="", blocked=False, blockedReason="", blockedBy="", VirtualMachineAcces=False):
        if ip in self.baseDB:
            self.baseDB[ip]["hostname"] = hostname
            self.baseDB[ip]["mac"] = mac
            self.baseDB[ip]["blocked"] = blocked
            self.baseDB[ip]["blockedReason"] = blockedReason
            self.baseDB[ip]["blockedBy"] = blockedBy
            self.baseDB[ip]["VirtualMachineAcces"] = VirtualMachineAcces
            return True
        else:
            return False

    def DeleteDevice(self, ip):
        try:
            self.baseDB.pop(ip)
            return True
        except:
            return False

    def GetDevice(self, ip):
        return self.baseDB[ip]

    def saveDB(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(self.baseDB))

    def loadDB(self, filename):
        try:
            with open(filename, "r") as f:
                self.baseDB = json.loads(f.read())
        except:
            #show red error message
            print(f"{colorama.Fore.RED}Error: Could not load the database{colorama.Fore.RESET}")