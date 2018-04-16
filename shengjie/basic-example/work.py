import lumiversepython as L
import time

rig = L.Rig("/home/teacher/Lumiverse/PBridge.rig.json")
rig.init()
rig.run()

count = 0
flag  = 1
judge = "$panel=0"
while (1):
    #devices = rig.getAllDevices()
    #devices = rig.getIds()
    #rig.select("$side=top").setRGBRaw(0,1,0)
    #rig.select("$side=bot").setRGBRaw(1,0,0)
    if flag==1:
        rig.select(judge).setRGBRaw(0,0,0)
        print(count)
        judge = "$panel="+str(count)
        rig.select(judge).setRGBRaw(1,0,0)
        rig.select(judge).setIntensity(0.01)
        count += 1
        if (count==56):
	        flag = 0
    elif (flag==0):
        rig.select(judge).setRGBRaw(0,0,0)
        print(count)
        count -= 1
        judge = "$panel="+str(count)
        rig.select(judge).setRGBRaw(0,1,0)
        rig.select(judge).setIntensity(count*10)
        if (count==0):
        	flag = 1
        
    rig.updateOnce()
    time.sleep(0.1)
	
