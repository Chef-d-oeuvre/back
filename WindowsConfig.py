import os, sys, socket

def GetDefaultGateway():
    if os.name == "nt":
        # Get the default gateway using ipconfig
        f = os.popen("ipconfig /all")
        # Read from the object, storing the output in a string
        s = f.read()
        # Close the object
        f.close()
        # Find the default gateway using find and index
        i = s.find("Default Gateway")
        # If the gateway is found, return it
        if i >= 0:
            j = s.find(":", i)
            k = s.find("\n", j)
            return s[j+2:k]
        # Otherwise, return an empty string
        return None
    else:
        print("This function was made entirely with githubcopilot and not tested on linux it might not work")
        print("If it doesn't work please open an issue on github")
        print("thank you")
        #get default gateway on raspberry pi
        f = os.popen("ip route show")
        s = f.read()
        f.close()
        i = s.find("default via")
        if i >= 0:
            j = s.find("dev", i)
            k = s.find(" ", j)
            return s[j+4:k]
        return None
def GetLocalIP():
    return socket.gethostbyname(socket.gethostname())

