#!/usr/bin/python
# 
import time,atexit,socketserver,sys
import socket
import hid
import binascii
import struct
import logging
import logging.handlers

# Set up syslog handler
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')  # Works on Linux

# Configure logging
logger = logging.getLogger("vat616Server")
logger.setLevel(logging.INFO)  # Log INFO and above
syslog_handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s - %(message)s'))
logger.addHandler(syslog_handler)

cv580_serno="61632-KEM1-0001/0001" #not connected atm
cv581_serno="61634-KEM1-0001/0002"
cv582_serno="61640-PEM1-0003/0011"
cv583_serno="61634-KEM1-0001/0001" 

valveId = ["CV580", "CV581", "CV582", "CV583"]
serial_number = (cv580_serno, cv581_serno, cv582_serno, cv583_serno)
path = len(valveId) * [""]
hid_device=len(valveId)*[None]
for i in range(len(valveId)):
    hid_device[i] = hid.device()
#hid_device = len(valveId) * [hid.device()]

#lists of data for getdata()

ec_list = len(valveId)*["0"]
en_list = len(valveId)*["0"]
am_list = len(valveId)*["0"]
es_list = len(valveId)*["0"]
p_list = len(valveId)*["0"]



print ("Starting vat616_server.py")    
logger.info("Starting vat616_server.py")

def identify(v):
    try:
        #hd=hid.device()
        logger.info(f"identify: index={v}; path={path[v]}")
        if path[v]!="":
            # print(f"Opening device for index={v}")
            hid_device[v].open_path(path[v])
        else:
            logger.info("identify: enumerating hid devices 0x272b, 0x0010")
            for d in hid.enumerate(0x272b, 0x0010):
                # print(f"path={d['path']}")
                #i.e if the enumerated path is already in pathlist, do NOT try to open it
                if path[v]=="":
                    try:
                        i=path.index(d['path'])
                        logger.info(f"identify: already found path {d['path']} in path[{i}]")
                        continue
                    except Exception as e:
                        logger.error(f"identify: path.index(): {e}")
                        hid_device[v].close()
                        logger.info(f"Opening device {d['path']}")
                        hid_device[v].open_path(d['path']) #CANNOT/SHOULD NOT OPEN A PATH ALREADY OPEN!
                        logger.info(f"Opened device {d['path']}")
                        pass
                
                logger.info(f"identify: reading serial number of {d['path']}")
                sn = rd_serialNo(hid_device[v])
                logger.info(f"identify: serial number: {sn}")
                if serial_number[v]==sn:
                    path[v]=d['path']
                    logger.info(f"identify: identified: {valveId[v]} connected to {path[v]}")
                    print(f"Identified {valveId[v]} at index={v} device {path[v]}")
                    # print(f"path[]={path}")
                    return
                else:
                    hid_device[v].close()    
    except Exception as e:
        print("indetify: " + str(e))
        logger.error(f"identify: {e}")
        pass
    return

def cleanup():
    for d in hid_device:
        try:
            d.close()
        except:
            logger.error(f"cleanup: d.close() {e}")
            pass
        
        
####### FUNCTIONS USED BY PROTOCOL #############################

def send_reset(v):
    try:
        wr_local(hid_device[v])
        wr_reset(hid_device[v])
        logger.info(f"send_reset: {v}")
        hid_device[v].close
        path[v] = ""
        time.sleep(1)
        identify(v)
        return "CS " + str(v) + " 0\n"
    except Exception as e:
        #print("send_reset " + str(e))
        logger.error(f"send_reset: {e}")
        identify(v)
        return "CS " + str(v) + " -1\n"
    
def getdata(v):
    try:
        p = rd_pos(hid_device[v])
        ec = rd_errCode(hid_device[v])
        en = rd_errNo(hid_device[v])
        am = rd_accMode(hid_device[v])
        es = rd_endSwitch(hid_device[v])
        #L= <N> <err_code> <err_no> <acc_mode> <sw_state> <pos>
        
        
        ec_list[v] = str(ec)
        en_list[v] = str(en)
        am_list[v] = str(am)
        es_list[v] = str(es)
        p_list[v] = str(p)
        
        
        s = "L= " + str(v) + " " + str(ec) + " " + str(en) + " " + str(am) + " " + str(es) + " " + str(p) + "\n" #teststring?
        #print("In getdata: "+s)
        #print("before return")
        return s
    except Exception as e:
        print("getdata: " + str(e))
        logger.error(f"getdata: {e}")
        identify(v)
        #return "L= " + str(v) + " -1 00 0 0.00\n" # CORRECT?
        s = "L= " + str(v) + " -1 " + en_list[v] + " " + am_list[v] + " " + es_list[v] + " " + p_list[v] + "\n"
        return s
def set_local(v):
    try:
        wr_local(hid_device[v])
        return "CS " + str(v) + " 0\n"
    except Exception as e:
        print("set_local " + str(e))
        logger.error(f"set_local: {e}")
        identify(v)
        return "CS " + str(v) + " -1\n"
    
def set_remote(v):
    try:
        wr_remote(hid_device[v])
        return "CS " + str(v) + " 0\n"
    except Exception as e:
        print("set_remote " + str(e))
        logger.error(f"set_remote: {e}")
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

def rd_endSwitch(h):
    h.write([0x0c,0x1a,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x31,0x30,0x31,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    res= "%c" % d[24] + "%c" % d[25]
    return res

######################################################################
    
#....callback function to handle the connection on the socket
class MyHandler(socketserver.StreamRequestHandler):
    def handle(self):
      while 1:
        dataReceived = self.rfile.readline() #buffer size in bytes, will split longer messages
#        print(dataReceived)
        if not dataReceived: break
        request=dataReceived.decode()
#        print(request)
        
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
            print("handle " + str(e))
            logger.error(f"handle: {e}")
#        print(txt)
        self.wfile.write(txt.encode())
        
# https://stackoverflow.com/a/18858817        
class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

          
port=1138   # port number for epics to connect to
myserver = MyTCPServer(("", port), MyHandler)
try:
    myserver.serve_forever()
except KeyboardInterrupt:
    cleanup()
    print("Ctrl-c user exit. \nClosing all devices...")
    logger.info(f"Ctrl-c user exit: {e}")
    sys.exit()
