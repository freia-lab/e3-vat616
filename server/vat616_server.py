#!/usr/bin/python
# 
import time,atexit,socketserver,sys
import hid
import binascii
import struct

cv580_serno="61632-KEM1-0001/0001" #not connected atm
cv581_serno="61634-KEM1-0001/0002"
cv582_serno="61640-PEM1-0003/0011"
cv583_serno="61634-KEM1-0001/0001" 

valveId = ["CV580", "CV581", "CV582", "CV583"]
serial_number = (cv580_serno, cv581_serno, cv582_serno, cv583_serno)
path = ["", "", "", ""]
hid_device = [None, None, None, None]


print ("Starting vat616_server.py")    

def identify(v):
    try:
        hd=hid.device()
        if path[v]!="":
            hd.open_path(path[v])
            hid_device[v]=hd
        else:
            for d in hid.enumerate(0x272b, 0x0010):
                #print(d['path'])
                ##CHECK: IS PATH IN PATHLIST? 
                
                continueFlag=False
                
                for p in path:
                    if d['path']==p:
                        continueFlag=True #i.e if the enumerated path is already in pathlist, do NOT try to open it
                        break
                
                if continueFlag:
                    continue
        
                #print(path)
                hd.open_path(d['path']) #CANNOT/SHOULD NOT OPEN A PATH ALREADY OPEN!
                #print(rd_serialNo(hd))
                if serial_number[v]==rd_serialNo(hd):
                    hid_device[v]=hd
                    path[v]=d['path']
                    print("Identified "+valveId[v])
                    return
                else:
                    hd.close()      
    except Exception as e:
        print(e)
        pass
    return

def cleanup():
    for d in hid_device:
        try:
            d.close()
        except:
            pass
        
        
####### FUNCTIONS USED BY PROTOCOL #############################

def send_reset(v):
    try:
        wr_local(hid_device[v])
        wr_reset(hid_device[v])
        return "R " + str(v) + " 0\n"
    except Exception as e:
        print(e)
        identify(v)
        return "R " + str(v) + " -1\n"
    
def getdata(v):
    try:
        p = rd_pos(hid_device[v])
        #print("before rd_errcCode")
        ec = rd_errCode(hid_device[v])
        #print("before string")
        en = rd_errNo(hid_device[v])
        am = rd_accMode(hid_device[v])
        #L= <N> <err_code> <err_no> <acc_mode> <pos>
        s = "L= " + str(v) + " " + str(ec) + " " + str(en) + " " + str(am) + " " + str(p) + "\n" #teststring?
        #print("In getdata: "+s)
        #print("before return")
        return s
    except Exception as e:
        print(e)
        identify(v)
        return "L= -1.0\n" # CORRECT?
    
def set_local(v):
    try:
        wr_local(hid_device[v])
        return "CS " + str(v) + " 0\n"
    except Exception as e:
        print(e)
        identify(v)
        return "CS " + str(v) + " -1\n"
    
def set_remote(v):
    try:
        wr_remote(hid_device[v])
        return "CS " + str(v) + " 0\n"
    except Exception as e:
        print(e)
        identify(v)
        return "CS " + str(v) + " -1\n"
    
######################################################################



#################### HID READ/WRITE ##################################

def wr_local(h):
    h.write([0xd1,0x11,0x1a,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x31,0x30,0x46,0x30,0x42,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    return

def wr_remote(h):
    h.write([0x67,0x3d,0x1a,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x31,0x30,0x46,0x30,0x42,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    return

def wr_reset(h):
    h.write([0x3c,0x15,0x19,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x31,0x31,0x45,0x30,0x32,0x30,0x33,0x30,0x30,0x30,0x30,0x31,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    

def rd_errCode(h):
    h.write([0x86,0x33,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x30,0x46,0x33,0x30,0x30,0x37,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    #print("\t\tError code: " + "%c" %  d[26] + "%c" % d[27])
    res="%c" %  d[26] + "%c" % d[27]
    return res

def rd_errNo(h):
    h.write([0x66,0xd1,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x30,0x46,0x33,0x30,0x30,0x36,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    res="%c" %  d[26] + "%c" % d[27]
    return res

def rd_accMode(h):
    h.write([0xa1,0xa1,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x30,0x46,0x30,0x42,0x30,0x30,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    #print("\t\tAccess mode: " + "%c" %  d[24] + "%c" % d[25], end=" ")
    res= "%c" % d[25]
    return res
    
def rd_serialNo(h):
    h.write([0x66,0x9e,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x30,0x46,0x31,0x30,0x30,0x31,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    string=""
    for i in d[24:44]:
       string += chr(i)
    return string

def rd_pos(h):
    h.write([0x6b,0xf5,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x31,0x31,0x30,0x31,0x30,0x30,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    for i in range (24,32):
        d[i] = chr(d[i])
    strval = ''.join(map(str,d[24:32]))
    fval = struct.unpack('!f', binascii.unhexlify(strval.replace('', '')))[0]
    res="{:.2f}".format(fval)
    return res

######################################################################
    
#....callback function to handle the connection on the socket
class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):
      while 1:
        dataReceived = self.request.recv(10) #buffer size in bytes, will split longer messages
        if not dataReceived: break
        request=dataReceived.decode()
        print(request)
        
        res=request.split(" ")
        
        txt="?\n"
        
        try:
            ind=int(res[1])
            #ind=1
            #print(ind)
            if 0 <= ind <= 3 and len(res)==2:
                if res[0]=="L?":
                    txt = getdata(ind) 
                elif res[0]=="R":
                    txt = send_reset(ind)
                elif res[0]=="Loc":
                    txt = set_local(ind)
                elif res[0]=="Rem":
                    txt = set_remote(ind)
        except Exception as e:
            print(e)
        
        print(txt)
        self.request.send(txt.encode())
        
            
port=1138   # port number for epics to connect to


myserver = socketserver.TCPServer(('',port),MyHandler)
try:
    myserver.serve_forever()
except KeyboardInterrupt:
    cleanup()
    print("Ctrl-c user exit. \nClosing all devices...")
    sys.exit()
