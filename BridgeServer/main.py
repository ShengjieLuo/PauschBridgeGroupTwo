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
GHC     = -1
PURNELL = 1
NEXT_USER_ID = 0
BG_COLOR = (1,0,0)
DEVICES_PER_PANEL = 4

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
    def __init__(self):
        self.light_colors = {}
        self.bridge = [rig.select("$panel="+str(i)) for i in range(58)]
        self.devices = {}
        all_device_ids = rig.getalldevices().getIds()
        for did in all_device_ids:
            self.devices[did] = rig.select(all_device_ids[did])
        for did in all_device_ids:
            self.light_colors[did] = BG_COLOR

    def resetColors(self):
        self.light_colors[did] = BG_COLOR

    #Light the bridge
    def light(self):
        for dev_id,color in self.light_colors:
            (r,g,b) = color
            self.devices[dev_id].setRGBRaw(r,g,b)
        rig.updateOnce()

def chooseColor():
    return (1,0,0)

'''
User
Keep User Status and Location for each user
'''
class User:

    #Init: Register the user direction and name
    def __init__(self,direct):
        self.color = chooseColor()
        self.direct = direct
        self.origin = direct
        if direct == GHC:
            self.loc = 20
        else:
            self.loc = 200
        self.status = STOP

    #Update: Triggered when status changed
    def update(self,status):
        self.status = status

    #Keep: Triggered each second to move
    #EDIT
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
    def addUser(self,direct):
        self.users[NEXT_USER_ID] = User(direct)
         
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
            self.users[name].direct = -self.users[name].direct
            self.users[name].update(WALK)
            self.users[name].keep()
            
    #Keep former movement
    def keepMovement(self):
        for name in self.users:
            self.users[name].keep()
            if self.users[name].loc<1 or self.users[name].loc>199:
                self.removeUser(name)

def render(users, lights):
    lights.resetColors()
    for user_id,user in users.users:
        current_panel = user.loc // DEVICES_PER_PANEL + 1
        for dev_id in current_panel.getIds()
            lights.light_colors[dev_id] = user.color
     
'''
        if user.origin==PURNELL:
            current_panel = user.loc // 4 + 1
            prev_panel    = current_panel - user.direct
            next_panel    = current_panel + user.direct
            current_dev   = sort(lights.bridge[current_panel].getIds())
            prev_dev      = sort(lights.bridge[prev_panel].getIds())
            next_dev      = sort(lights.bridge[next_panel].getIds())
            devices = prev_panel + current_panel + next_panel
            for dev in devices:
                
        else:
'''              
    
'''
TCP Request Handler
Handle TCP request and update the light
'''
class myHandler(BaseHTTPRequestHandler):    

    def do_POST(self):
        if self.path=="/reg":
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            users.addUser(data["direct"])
            self.send_response(200)
            self.end_headers()
            return
        elif self.path=="/exec":
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            users.updateMovement(data["status"])
            self.send_response(200)
            self.end_headers() 
        elif self.path=="/small":
            #users.light(0)
            self.send_response(200)
        elif self.path=="/large":
            users.keepMovement()
            Light.light()
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
Light = Light()
if __name__=="__main__":
    thread.start_new_thread(ServerThread,())
    time.sleep(5)
    #thread.start_new_thread(SmallTimerThread,())
    thread.start_new_thread(LargeTimerThread,())
    while 1:
        pass
