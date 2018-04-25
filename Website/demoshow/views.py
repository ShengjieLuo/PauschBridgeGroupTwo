from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render_to_response
import requests
import json

#Bridge Threshold
minPanel  = 5
maxPanel  = 50

#Status Constant
WALK      = 1
RUN       = 2
BACK      = 3
LEAVE     = 4
STOP      = 5

#Registration Constant
GHC       = 0
PURNELL   = 1

#Pausch Bridge Server
URL = "http://pbridge.adm.cs.cmu.edu:3456/"

def index(request):
  template = loader.get_template("demoshow/index.html")
  return HttpResponse(template.render(None,request))

def process(request):
  ctx = {}
  print(request.path)
  if 'q' not in request.GET or 'd' not in request.GET or request.GET['d'] not in {'g':1,'p':2}:
    template = loader.get_template("demoshow/index.html")
    return HttpResponse(template.render(None,request))
  username  = request.GET['q']
  direction = request.GET['d']
  if direction == 'g':
      sendRegMsgToServer(GHC,username)
      dfrom = "GHC (School of Computer Science)"
      dto   = "Purnel (School of Drama)"
  elif direction == 'p':
      sendRegMsgToServer(PURNELL,username)
      dto   = "GHC (School of Computer Science)"
      dfrom = "Purnell (School of Drama)"
  context = {'username':username,'from':dfrom,'to':dto}
  template = loader.get_template("demoshow/process.html")
  return HttpResponse(template.render(context,request))

def sendRegMsgToServer(direct,name):
    print("Send registration back to Pausch Server")
    s = json.dumps({'direct':direct,'name':name})
    r = requests.post(URL+"reg",data=s)
    return 0

def sendMoveMsgToServer(status,name):
    print("Send Move Message to Pausch Server")
    s = json.dumps({'status':status,'name':name})
    r = requests.post(URL+"exec",data=s)
    return 0

def onbridge(request):
  print(request.path)
  username = request.path.split('/')[-1]
  direct   = request.path.split('/')[-2]
  context = {'username':username}
  if 'walk' in request.GET:
      sendMoveMsgToServer(WALK,username)
      context['status'] = "Keep Walking"
  elif 'run' in request.GET:
      sendMoveMsgToServer(RUN,username)
      context['status'] = "Running, but not too fast"
  elif 'back' in request.GET:
      sendMoveMsgToServer(BACK,username)
      context['status'] = "Turn Back, and then walk back"
  elif 'leave' in request.GET:
      sendMoveMsgToServer(LEAVE,username)
      context['status'] = "Leave the bridge, the light will not follow you"
  elif 'stop' in request.GET:
      sendMoveMsgToServer(STOP, username)
      context['status'] = "Stop the step, keep patient"
  template = loader.get_template("demoshow/onbridge.html")
  return HttpResponse(template.render(context,request))
