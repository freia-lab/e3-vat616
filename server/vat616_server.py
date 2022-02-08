#!/usr/bin/python
# 
import time,atexit,socketserver,sys
import hid
import binascii
import struct

def cleanup():
    hid.close()

print ("Starting vat616_server.py")    
try:
  hid = hid.device()
  hid.open(0x272b, 0x0010)
  atexit.register(cleanup)
except:
  sys.exit("Cannot open USB port")

def send_reset():
    try:
        wr_local(hid)
        wr_reset(hid)
        return 'R 0 0\n'
    except:
        return 'R 0 -1\n'

def wr_local(h):
    h.write([0xd1,0x11,0x1a,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x31,0x30,0x46,0x30,0x42,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)
    return

def wr_reset(h):
    h.write([0x3c,0x15,0x19,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x31,0x31,0x45,0x30,0x32,0x30,0x33,0x30,0x30,0x30,0x30,0x31,0x0d,0x0a])
    time.sleep(0.05)
    d = h.read(64)


def rd_pos(h):
    try:
        h.write([0x6b,0xf5,0x18,0x00,0x15,0x00,0x00,0x00,0x70,0x3a,0x30,0x42,0x31,0x31,0x30,0x31,0x30,0x30,0x30,0x30,0x30,0x30,0x0d,0x0a])
        time.sleep(0.05)
        d = h.read(64)
        print(d[24:34])
        for i in range (24,32):
            d[i] = chr(d[i])
        strval = ''.join(map(str,d[24:32]))
    #    print (strval)
        fval = struct.unpack('!f', binascii.unhexlify(strval.replace('', '')))[0]
    #    print(fval)
    #    print("Pos: %4.1f" % fval)
        return fval
    except:
        try:
            hid.open(0x272b, 0x0010)
        except:
            pass
        return -1.0
            
def getdata():
    p = rd_pos(hid)
    s = "L= 0 "+str(p)+" 1 1.1 2 2.2 -3 3.3\n"
    print("In getdata: "+s)
    return s
    
#....callback function to handle the connection on the socket
class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):
      while 1:
        dataReceived = self.request.recv(10)
        if not dataReceived: break
        request=dataReceived.decode()
        print(request)
        if request == 'L?\n':
          txt = getdata()
          print(txt)
          self.request.send(txt.encode())
        elif request == 'R 0\n':
          txt = send_reset()
          print(txt)
          self.request.send(txt.encode())
            
port=1138   # port number for epics to connect to
myserver = socketserver.TCPServer(('',port),MyHandler)
myserver.serve_forever()
