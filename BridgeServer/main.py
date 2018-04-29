#!/usr/bin/python
'''
Pausch Bridge Light Show
Following is the main function of Pausch Bridge Light Show
'''

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import json
import time
import thread
import requests
import lumiversepython as L

#User-defined Constant
PORT_NUMBER = 3456
URL = "http://127.0.0.1:3456/"
SMALL_INTERVAL = 0.1
LARGE_INTERVAL = 1
WALK    = 1
RUN     = 2
BACK    = 3
LEAVE   = 4
STOP    = 5
GHC     = 0
PURNELL = 1

#Intialize the light
rig = L.Rig("/home/teacher/Lumiverse/PBridge.rig.json")
rig.init()

#Set the colour
GHC_COLOUR = (0,0,0)
PURNELL_COLOR = (0,0,0)

'''
Light
Interactive with light
'''
class Light:

    #Light the bridge
    def light(self,users):
        for userkey in users:
            user = users[userkey]
            if user.direct==GHC:
                panel = "$panel="+str(user.loc)
                rig.select(panel).setRGBRaw(1,0,0)
                panel = "$panel="+str(user.loc-1)
                rig.select(panel).setRGBRaw(0,0,0)
                if user.status==RUN:
                    panel = "$panel="+str(user.loc-1)
                    panel = "$panel="+str(user.loc-2)
                    rig.select(panel).setRGBRaw(1,0,0)
            elif user.direct ==PURNELL:
                panel = "$panel="+str(user.loc)
                rig.select(panel).setRGBRaw(0,1,0)
                panel = "$panel="+str(user.loc+1)
                rig.select(panel).setRGBRaw(0,0,0)
                if user.status==RUN:
                    panel = "$panel="+str(user.loc+2)
                    rig.select(panel).setRGBRaw(0,1,0)
                    
        rig.updateOnce() 

'''
User
Keep User Status and Location for each user
'''
class User:

    #Init: Register the user direction and name
    def __init__(self,direct,name):
        self.name = name
        self.direct = direct
        if direct == GHC:
            self.loc = 5
        else:
            self.loc = 50
        self.status = STOP

    #Update: Triggered when status changed
    def update(self,status):
        self.status = status

    #Keep: Triggered each second to move
    def keep(self):
        if self.status==WALK:
            self.loc = self.loc + (1-self.direct*2)
        elif self.status==RUN:
            self.loc = self.loc + 2*(1-self.direct*2)

'''
Users
'''
class Users:

    #Init: No available users when initialized
    def __init__(self):
        self.users = {}

    #AddUser: add new user into the tracklist
    def addUser(self,direct,name):
        self.users[name] = User(direct,name)
    
    #RemoveUser: remove user from tracklist
    def removeUser(self,name):
        del self.users[name]

    #Update User:
    def updateMovement(self,status,name):
        if status==LEAVE:
            self.removeUser(name)
        elif status==WALK or status==RUN or status==STOP:
            self.users[name].update(status)
            self.users[name].keep()
        elif status==BACK:
            self.users[name].direct = 1-self.users[name].direct
            self.users[name].update(WALK)
            self.users[name].keep()
            
    #Keep former movement
    def keepMovement(self):
        for name in self.users:
            self.users[name].keep()
            if self.users[name].loc<1 or self.users[name].loc>50:
                self.removeUser(name)

    #Operate Light
    def light(self,mode):
        light.light(self.users)
        if mode==1:
            lights = ["*"]*51
            for user in self.users:
                lights[self.users[user].loc] = "+"
            print "".join(lights)
   
'''
TCP Request Handler
Handle TCP request and update the light
'''
class myHandler(BaseHTTPRequestHandler):    

    def do_POST(self):
        if self.path=="/reg":
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            users.addUser(data["direct"],data["name"])
            self.send_response(200)
            self.end_headers()
            return
        elif self.path=="/exec":
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            users.updateMovement(data["status"],data["name"])
            self.send_response(200)
            self.end_headers() 
        elif self.path=="/small":
            #users.light(0)
            self.send_response(200)
        elif self.path=="/large":
            users.keepMovement()
            users.light(1)
            self.send_response(200)

    def log_message(self, format, *args):
        return

'''
Server Thread
Receive http requests and handle the requests
'''
def ServerThread():
    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ' , PORT_NUMBER
        #Wait forever for incoming htto requests
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()


'''
SmallTimerThread:
Call the main thread every 0.05s to keep light stable
'''
def SmallTimerThread():
    while (1):
        time.sleep(SMALL_INTERVAL)
        requests.post(URL+"small",data="d")

'''
LargeTimerThread
Call the main thread every 1s to make light changes
'''
def LargeTimerThread():
    while (1):
        time.sleep(LARGE_INTERVAL)
        requests.post(URL+"large",data="d")

users   = Users()
light = Light()
if __name__=="__main__":
    thread.start_new_thread(ServerThread,())
    time.sleep(5)
    thread.start_new_thread(SmallTimerThread,())
    thread.start_new_thread(LargeTimerThread,())
    while 1:
        pass
