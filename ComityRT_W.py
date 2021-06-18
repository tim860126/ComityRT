import curses, time
import pyfiglet, random
import inquirer
import psutil
import subprocess
import math
import configparser
import shutil
import threading
import os
from configobj import ConfigObj

Config_ConList=["Container_Use_Cores","Container_Cores_Weights","Container_Memory_Limit","Container_Priority_Mode"]

workfolder="./work/"

multifolder="./multi-level/"

logfolder="./logs/"

workprintline=9

def AL():
  
  for level in WorkQueue:
    Wtemp=WorkQueue[level]['Queue'].copy()
    if WorkQueue[level]['run']!="":
      Wtemp.append(WorkQueue[level]['run'])
    for name in Wtemp:
      exc=0
      exc=exc+int(config['Tasks'][name]['c'])-int(config['Tasks'][name]['runtime'])
      Wtemp2=Wtemp.copy()
      Wtemp2.remove(name)
      for name2 in Wtemp:
        if config['Tasks'][name]['priority'] < config[name2]['priority']:
          exc=exc+int(config[name2]['c'])-int(config[name2]['runtime'])
          #worklog="{name} {name2} {p} {p2}\n".format(name=str(Wtemp2),name2=name, p=str(config['Tasks'][name]['priority']),p2=str(config[name2]['priority']))
          #WriteAL(worklog)
      nowEnd=settime+exc
      if nowEnd > int(config['Tasks'][name]['d']):
        worklog="{name} MissDeadline It FINSH {Time} Not {D} in {level}\n".format(name=name,level=level,Time=nowEnd,D=config['Tasks'][name]['d'])
        WriteAL(worklog)
          

def WriteAL(string):
  localtime = time.localtime()
  localtime = time.strftime("%I:%M:%S ", localtime)
  f = open(logname+"AL",'a+')
  f.write(str(settime)+" "+string)
  f.close()  

def WriteLog(string):
  localtime = time.localtime()
  localtime = time.strftime("%I:%M:%S ", localtime)
  f = open(logname,'a+')
  f.write(str(settime)+" "+string)
  f.close()

def ContChangeLevel(wname,chlevel):
  global WorkQueue
  global config
  FindPid(wname)
  config['Tasks'][wname]['Sub']=chlevel
  if wname in WorkQueue[config['Tasks'][wname]['level']]['Queue']: 
    WorkQueue[config['Tasks'][wname]['level']]['Queue'].remove(wname)
  os.system("./ChangeContainer.sh "+chlevel+" "+config['Tasks'][wname]['pid'])

def SubChangeLevel(wname,level,chlevel):
  global WorkQueue
  global config
  FindPid(wname)
  Sub_StopWork(wname)
  os.system("./ChangeContainer.sh "+chlevel+" "+config['Tasks'][wname]['pid'])
  config['Tasks'][wname]['level']=chlevel
  #config['Tasks'][wname]['c']=config['Tasks'][wname][chlevel]
  config['Tasks'][wname]['statusprint']=config['Tasks'][wname]['statusprint'].replace(config['Tasks'][wname]['Sub'],chlevel)
  config['Tasks'][wname]['Sub']=""
  worklog="SubChange {name} in {level}\n".format(name=wname,level=chlevel)
  WriteLog(worklog)
  stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
  stdscr.clrtoeol()
  stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" Change Level "+config['Tasks'][wname]['c']+" "+config['Tasks'][wname]['level'],curses.A_BOLD)
  WorkQueue[chlevel]['Queue'].append(wname)
  LevelSort(chlevel)
  WorkQueue[level]['print']=level+":"+str(WorkQueue[level]['Queue'])+" "+str(WorkQueue[level]['status'])+" "+str(WorkQueue[level]['run'])
  stdscr.move(int(WorkQueue[level]['statuspr']),0)
  stdscr.clrtoeol()
  stdscr.addstr(int(WorkQueue[level]['statuspr']),0,WorkQueue[level]['print'],curses.A_BOLD)
  WorkQueue[chlevel]['print']=chlevel+":"+str(WorkQueue[chlevel]['Queue'])+" "+str(WorkQueue[chlevel]['status'])+" "+str(WorkQueue[chlevel]['run']
  )
  stdscr.move(int(WorkQueue[chlevel]['statuspr']),0)
  stdscr.clrtoeol()
  stdscr.addstr(int(WorkQueue[chlevel]['statuspr']),0,WorkQueue[chlevel]['print'],curses.A_BOLD)
  Schedule()
 
def ChangeLevel(wname,level,chlevel):
  global WorkQueue
  global config
  FindPid(wname)
  StopWork(wname)
  if wname in WorkQueue[level]['Queue']:
    WorkQueue[level]['Queue'].remove(wname)
  os.system("./ChangeContainer.sh "+chlevel+" "+config['Tasks'][wname]['pid'])
  if WorkQueue[level]['run']==wname:
    WorkQueue[level]['run']=""
  config['Tasks'][wname]['level']=chlevel
  worklog="Change {name} in {level}\n".format(name=wname,level=chlevel)
  WriteLog(worklog)
  #config['Tasks'][wname]['c']=config['Tasks'][wname][chlevel]
  config['Tasks'][wname]['statusprint']=config['Tasks'][wname]['statusprint'].replace(level,chlevel)
  stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
  stdscr.clrtoeol()
  stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" Change Level "+config['Tasks'][wname]['c']+" "+config['Tasks'][wname]['level'],curses.A_BOLD)
  #StopWork(wname)
  #Check_Work()
  WorkQueue[chlevel]['Queue'].append(wname)
  LevelSort(chlevel)
  WorkQueue[level]['print']=level+":"+str(WorkQueue[level]['Queue'])+" "+str(WorkQueue[level]['status'])+" "+str(WorkQueue[level]['run'])
  stdscr.move(int(WorkQueue[level]['statuspr']),0)
  stdscr.clrtoeol()
  stdscr.addstr(int(WorkQueue[level]['statuspr']),0,WorkQueue[level]['print'],curses.A_BOLD)
  WorkQueue[chlevel]['print']=chlevel+":"+str(WorkQueue[chlevel]['Queue'])+" "+str(WorkQueue[chlevel]['status'])+" "+str(WorkQueue[chlevel]['run']
  )
  stdscr.move(int(WorkQueue[chlevel]['statuspr']),0)
  stdscr.clrtoeol()
  stdscr.addstr(int(WorkQueue[chlevel]['statuspr']),0,WorkQueue[chlevel]['print'],curses.A_BOLD)
  Schedule()

def FindPid(wname):
  global config 
  try:
    c=subprocess.check_output(['pidof',wname])
    c=c.decode('utf-8').split("\n")[0]
    config['Tasks'][wname]['pid']=c
    return "true"
  except:
    return "false"

def SubContWork(wname,level):
  global WorkQueue
  global config
  FindPid(wname)
  c=subprocess.check_output(['./StopWorkPID.sh',config['Tasks'][wname]['pid']])
  msg=c.decode('utf-8').split("\n")[0]
  if msg=="True":
    #os.system("./ContWork.sh "+wname);
    SubLevel[level]['status']=1
    SubLevel[level]['run']=wname
    config['Tasks'][wname]['status']="1"
    #os.system("kill -CONT $(pidof "+wname+")")
    #os.system("kill -CONT "+config['Tasks'][wname]['pid'])
    worklog="Cont Sub {name} in {level}\n".format(name=wname,level=level)
    WriteLog(worklog)
    config['Tasks'][wname]['statusprint']=config['Tasks'][wname]['statusprint'].replace(config['Tasks'][wname]['level'],level)
    stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" Cont "+config['Tasks'][wname]['status'],curses.A_BOLD)


def ContWork(wname):
  global WorkQueue
  global config
  FindPid(wname)
  c=subprocess.check_output(['./ContWorkPID.sh',config['Tasks'][wname]['pid']])
  msg=c.decode('utf-8').split("\n")[0]
  if msg=="True":
    #os.system("./ContWork.sh "+wname);
    WorkQueue[config['Tasks'][wname]['level']]['status']=1 
    WorkQueue[config['Tasks'][wname]['level']]['run']=wname
    config['Tasks'][wname]['status']="1"
    #os.system("kill -CONT $(pidof "+wname+")")
    #os.system("kill -CONT "+config['Tasks'][wname]['pid'])
    worklog="Cont {name} in {level}\n".format(name=wname,level=config['Tasks'][wname]['level'])
    WriteLog(worklog)
    stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" Cont "+config['Tasks'][wname]['status'],curses.A_BOLD)

  #os.system("kill -CONT "+str(pid))
  #os.system("docker exec "+config['Tasks'][wname]['level']+" kill -CONT $(pidof "+wname+")")
  #stdscr.addstr(29,0,wname+":"+config['Tasks'][wname]['status'],curses.A_BOLD)
def KillWork(wname):
  global workQueue
  global config

  ck=FindPid(wname)
  #ck="true" 
  if ck=="true":
    #WorkQueue[config['Tasks'][wname]['level']]['status']=0
    config['Tasks'][wname]['status']="0"
    #os.system("kill -9 "+str(pid))
    if WorkQueue[config['Tasks'][wname]['level']]['run']==wname:
      WorkQueue[config['Tasks'][wname]['level']]['status']=0
      WorkQueue[config['Tasks'][wname]['level']]['run']=""
    elif wname in WorkQueue[config['Tasks'][wname]['level']]['Queue']:
      WorkQueue[config['Tasks'][wname]['level']]['Queue'].remove(wname)
    if config['Tasks'][wname]['Sub']!="":
      if SubLevel[config['Tasks'][wname]['Sub']]['run']==wname:
        SubLevel[config['Tasks'][wname]['Sub']]['run']=""
        SubLevel[config['Tasks'][wname]['Sub']]['status']=0  
    #WorkQueue[config['Tasks'][wname]['level']]['Queue'].remove(wname)
    config['Tasks'][wname]['runtime']="0"
    config['Tasks'][wname]['priority']="0"
    #config['Tasks'][wname]['d']=str(int(config['Tasks'][wname]['d'])+int(config['Tasks'][wname]['d']))
    #config['Tasks'][wname]['C']=config['Tasks'][wname][config['Tasks'][wname]['orilevel']]
    config['Tasks'][wname]['Kill']="1"
    #os.system("kill -9 $(pidof "+wname+")")
    os.system("kill -9 "+config['Tasks'][wname]['pid'])
    worklog="Kill {name} in {level}\n".format(name=wname,level=config['Tasks'][wname]['level'])
    config['Tasks'][wname]['level']=config['Tasks'][wname]['orilevel']
    WriteLog(worklog)
    stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" kill "+config['Tasks'][wname]['status'],curses.A_BOLD)
    #os.system("docker exec "+config['Tasks'][wname]['level']+" kill -9 $(pidof "+wname+")")
  else:
    config['Tasks'][wname]['status']="0"
    #os.system("kill -9 "+str(pid))
    WorkQueue[config['Tasks'][wname]['level']]['status']=0
    WorkQueue[config['Tasks'][wname]['level']]['run']=""
    #WorkQueue[config['Tasks'][wname]['level']]['Queue'].remove(wname)
    config['Tasks'][wname]['runtime']="0"
    config['Tasks'][wname]['level']=config['Tasks'][wname]['orilevel']
    worklog="Kill error {name} in {level}\n".format(name=wname,level=config['Tasks'][wname]['level'])
    WriteLog(worklog)
    stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" kill "+config['Tasks'][wname]['status'],curses.A_BOLD)
  #Check_Work()
  #Schedule()
 
def Sub_StopWork(wname):
  global WorkQueue
  global config
  FindPid(wname)
  c=subprocess.check_output(['./StopWorkPID.sh',config['Tasks'][wname]['pid']])
  msg=c.decode('utf-8').split("\n")[0]
  if msg=="True":
    #os.system("kill -STOP "+config['Tasks'][wname]['pid'])
    worklog="Stop Sub {name} in {level}\n".format(name=wname,level=config['Tasks'][wname]['Sub'])
    WriteLog(worklog)
    #os.system("./StopWork.sh "+wname);
    SubLevel[config['Tasks'][wname]['Sub']]['status']=0 #佇列旗標進程更改為空閒
    SubLevel[config['Tasks'][wname]['Sub']]['run']=""#重新加入到佇列中
    config['Tasks'][wname]['status']="-1" #工作狀態顯示為暫停
    stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" stop "+config['Tasks'][wname]['status'],curses.A_BOLD)

def StopWork(wname):
  global WorkQueue
  global config
  FindPid(wname)
  #c=os.system("pidof "+wname)
  #print(c)
  if config['Tasks'][wname]['status']!=100:
    #os.system("kill -STOP $(pidof "+wname+")")
    #os.system("kill -STOP "+config['Tasks'][wname]['pid'])
    c=subprocess.check_output(['./StopWorkPID.sh',config['Tasks'][wname]['pid']])
    msg=c.decode('utf-8').split("\n")[0]
    if msg=="True":
      worklog="Stop {name} in {level}\n".format(name=wname,level=config['Tasks'][wname]['level'])
      WriteLog(worklog)
      #os.system("./StopWork.sh "+wname);
      WorkQueue[config['Tasks'][wname]['level']]['status']=0 #佇列旗標進程更改為空閒
      WorkQueue[config['Tasks'][wname]['level']]['Queue'].append(wname)#重新加入到佇列中
      config['Tasks'][wname]['status']="-1" #工作狀態顯示為暫停
      stdscr.move(int(config['Tasks'][wname]['statuspr']),0)
      stdscr.clrtoeol()
      stdscr.addstr(int(config['Tasks'][wname]['statuspr']),0,config['Tasks'][wname]['statusprint']+" stop "+config['Tasks'][wname]['status'],curses.A_BOLD)

  #os.system("docker exec "+config['Tasks'][wname]['level']+" kill -STOP $(pidof "+wname+")")
  #os.system("kill -STOP "+str(c))
  #os.system("kill -STOP $(pidof "+wname+")")
  #stdscr.addstr(28,0,wname+":"+config['Tasks'][wname]['status'],curses.A_BOLD)

def Choose_config(choices):
  global sysconfig
  global CLconfig
  global CTconfig
  global logname
  global WorkQueue
  global SubLevel
  global levellist
  WorkQueue={}
  SubLevel={}
  questions = [
  inquirer.List('action',
                message="Choose An configuration file",
                choices=choices,
            ),
  ]
  answers = inquirer.prompt(questions)
  #sysconfig = configparser.ConfigParser()
  #print(answers['action'])
  localtime = time.localtime()
  localtime = time.strftime("%Y-%m-%d-%I:%M:%S", localtime)
  runingstr="Running {system} system at {starttime}\n".format(system=answers['action'],starttime=localtime)
  logname=logfolder+"ComityRT."+answers['action']+"."+str(localtime)
  f = open(logname,'w+')
  f.write(runingstr)
  f.close()
  #sysconfig.read("./config/"+answers['action']+".ini")
  #levellist=sysconfig['Tasks'].keys()
  sysconfig =ConfigObj('./config/System/'+answers['action']+'.ini')
  CLconfig =ConfigObj('./config/CL/'+sysconfig['ComityRT']['Criticality_Level_Filename'])
  CTconfig =ConfigObj('./config/Container/'+sysconfig['ComityRT']['Container_Filename'])
  #config.read('./config/'+sname+'.ini')
  levellist = CLconfig.keys()
  #WorkQueue 初始化
  #print(levellist)
  #print(CLconfig['level1']['CL_Use_Container'][0])
  for level in levellist: 
    Wtemp=list()
    if isinstance(CLconfig[level]['CL_Use_Container'],list)==True:
      for a in CLconfig[level]['CL_Use_Container']:
        Wtemp.append(a)
      MCT=CLconfig[level]['CL_Use_Container'][0]
      del Wtemp[0]
    else:
      MCT=CLconfig[level]['CL_Use_Container']
    WorkQueue[MCT]=dict()
    WorkQueue[MCT]['status']=0
    WorkQueue[MCT]['level']=level
    WorkQueue[MCT]['Queue']=list()
    WorkQueue[MCT]['Sub']=list()
    for SubN in Wtemp:
      WorkQueue[MCT]['Sub'].append(SubN)
      SubLevel[SubN]=dict()
      SubLevel[SubN]['status']=0
      SubLevel[SubN]['run']=""
    #print(WorkQueue[MCT]['Sub'])
  print(WorkQueue)
  return sysconfig['ComityRT']['TDF_Filename']

def SystemTimeStart():
   global settime
   global config
   global sysconfig
   timeprint=""
   #for name in config['Tasks'].keys():
   #  tp1=threading.Thread(target=TimeStart,args=(name,))
   #  tp1.start()
   while(1):
     time.sleep(1)
     settime=settime+1
     #if sysconfig['ComityRT']['Scheduleability_analysis']=="EDF":
     #  priority_method(config,"EDF")
       #WorkSort(config)
     s=0
     m=0
     if settime>60:
       m=settime/60
       s=settime-(60*int(m))
       timeprint=str(int(m))+" min "+str(int(s))+" sec"
     else:
       timeprint=str(settime)+" sec"
     
     #stdscr.addstr(6,0,"time:"+str(timeprint),curses.A_BOLD)
     #Check_Work()
     #Schedule()
     for name in H:
       if(config['Tasks'][name]['status']=="0" or config['Tasks'][name]['status']=="-1"):
         config['Tasks'][name]['print']=config['Tasks'][name]['print']+" "
         stdscr.addstr(int(config['Tasks'][name]['workpr']),0,config['Tasks'][name]['print'],curses.A_BOLD)
         #config['Tasks'][name]['runtime']=str(int(config['Tasks'][name]['runtime'])+1)
       elif config['Tasks'][name]['status']=="1":
         config['Tasks'][name]['print']=config['Tasks'][name]['print']+"▄"
         config['Tasks'][name]['runtime']=str(int(config['Tasks'][name]['runtime'])+1)
         stdscr.addstr(int(config['Tasks'][name]['workpr']),0,config['Tasks'][name]['print'],curses.A_BOLD)
     
     for name in config['Tasks'].keys():
       if config['Tasks'][name]['d']==str(settime):
         config['Tasks'][name]['d']=str(int(config['Tasks'][name]['d'])+int(config['Tasks'][name]['Deadline_Time']))
         msg=FindPid(name)
         if msg=="true":
           KillWork(name)
 
     levellist=CLconfig.keys()
     if sysconfig['ComityRT']['Task_Move']=="true":
       for name in config['Tasks'].keys():
         for chlevel in levellist:
           if chlevel in config['Tasks'][name]:
             if config['Tasks'][name]['runtime']==config['Tasks'][name][chlevel] and WorkQueue[config['Tasks'][name]['level']]['level']!=chlevel:
               level=config['Tasks'][name]['level']
               for CT in WorkQueue:
                 if WorkQueue[CT]['level']==chlevel:
                   chlevel=CT
               if config['Tasks'][name]['Sub']=="":
                 ChangeLevel(name,level,chlevel)
               else:
                 SubChangeLevel(name,level,chlevel)
    
     #AL()
     #for name in config['Tasks'].keys():
     #  if config['Tasks'][name]['runtime']==config['Tasks'][name][config['Tasks'][name]['level']] and sysconfig['ComityRT']['Change_Level_Mode']=="true":
     #      level=config['Tasks'][name]['level']
     #      pst=levellist.index(config['Tasks'][name]['level'])
     #      if pst+1<=len(levellist)-1:
     #        chlevel=levellist[pst+1]
     #        if config['Tasks'][name]['Sub']=="":
     #          ChangeLevel(name,level,chlevel)
     #        else:
     #          SubChangeLevel(name,level,chlevel)
     #      else:
     #        ca=1
       #if config['Tasks'][name]['nextstart']==str(settime) and config['Tasks'][name]['nextstart']!="0" and config['Tasks'][name]['status']=="1":
       #  KillWork(name)
       
     Check_Work()
     Schedule()
     stdscr.addstr(6,0,"time:"+str(timeprint),curses.A_BOLD)
def TimeStart(name):
  global config
  time.sleep(0.5)
  #c=subprocess.check_output(['pidof','work4'])
  #c=c.decode('utf-8').split("\n")[0]
  #config['Tasks'][name]['pid']=c
     #if(config['Tasks'][name]['status']=="0" or config['Tasks'][name]['status']=="-1"):
     #  config['Tasks'][name]['print']=config['Tasks'][name]['print']+" "
     #  stdscr.addstr(int(config['Tasks'][name]['workpr']),0,config['Tasks'][name]['print'],curses.A_BOLD)
     #elif config['Tasks'][name]['status']=="1":
       #for wname in WorkQueue[config['Tasks'][name]['level']]['Queue']:
       #  if wname!=name and int(settime)>int(config['Tasks'][wname]['nextstart']):
       #    config['Tasks'][wname]['nextstart']=str(int(config['Tasks'][wname]['nextstart'])+1)
     #  config['Tasks'][name]['print']=config['Tasks'][name]['print']+"▄"
     #  stdscr.addstr(int(config['Tasks'][name]['workpr']),0,config['Tasks'][name]['print'],curses.A_BOLD)
   
   #string="{0:10}".format(name)+"↑"
   #time.sleep(1)
   #string=config['Tasks'][name]['print']
   #time.sleep(1)
   #i=0;
   #j=0; 
   #while(config['Tasks'][name]['status']=='1' or config['Tasks'][name]['status']=='-1'):
     
   #  time.sleep(1)
     #while(config['Tasks'][name]['status']=='-1'):
       #i=i+1 
     #string=string+"▄"
       #config['Tasks'][name]['print']=config['Tasks'][name]['print']+"▄"
   #  stdscr.addstr(int(config['Tasks'][name]['workpr']),0,config['Tasks'][name]['print'],curses.A_BOLD)
   #  j=j+1
     #if len(WorkQueue[config['Tasks'][name]['level']]['Queue'])>0:
     #   for qwname in WorkQueue[config['Tasks'][name]['level']]['Queue']:
     #     if qwname != name:
     #       config[qwname]['nextstart']=str(int(config[qwname]['nextstart'])+1)  
#config['Tasks'][name]['print']=string
def producer(str123,T,name):
    global config
    global WorkQueue
    config['Tasks'][name]['status']="1"
    WorkQueue[config['Tasks'][name]['level']]['status']=1
    #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
    pname="{0:10}".format(name)
    C="{0:4}".format(config['Tasks'][name]['C'])
    T="{0:4}".format(config['Tasks'][name]['T'])
    level="{0:8}".format(config['Tasks'][name]['level'])
    worklog="Run {name} in {level} excution {C} period {T}\n".format(name=pname,level=level,C=C,T=T)
    WriteLog(worklog)
    #tp1=threading.Thread(target=TimeStart,args=(name,))
    #t2=threading.Thread(target=consumer,args=(workname,worklevel,))
    #tp1.start()
    config['Tasks'][name]['statusprint']=str123
    stdscr.move(int(config['Tasks'][name]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,str123+" start "+config['Tasks'][name]['status'],curses.A_BOLD)
    ggg=str123.split()
    #ggg[0] level ggg[1] ggg[2] ggg[3]
    #os.system("docker exec "+str123)
    #por=subprocess.run(["docker", "exec",ggg[0],ggg[1],ggg[2],ggg[3]])
    por=subprocess.run(["docker", "exec",ggg[0],ggg[3]])
    #if config['Tasks'][name]['status']!="-1":
    worklog="Finish {name} \n".format(name=name)
    WriteLog(worklog)
    if config['Tasks'][name]['Kill']!="1":
      config['Tasks'][name]['status']="0"
      config['Tasks'][name]['runtime']="0"
      #config['Tasks'][name]['c']=config['Tasks'][name][config['Tasks'][name]['orilevel']]
      config['Tasks'][name]['priority']="0"
      WorkQueue[config['Tasks'][name]['level']]['status']=0
      WorkQueue[config['Tasks'][name]['level']]['run']=""
      config['Tasks'][name]['level']=config['Tasks'][name]['orilevel']
      #config['Tasks'][name]['d']=str(int(config['Tasks'][name]['d'])+int(config['Tasks'][name]['d']))
      #if len(WorkQueue[config['Tasks'][name]['level']]['Queue'])>0:
      #  for qwname in WorkQueue[config['Tasks'][name]['level']]['Queue']:
      #    if qwname != name:
      #      config[qwname]['nextstart']=str(int(config[qwname]['nextstart'])+int(config['Tasks'][name]['c']))
     
    #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
      stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,str123+" OK next arrive "+config['Tasks'][name]['nextstart']+" sec "+config['Tasks'][name]['status'],curses.A_BOLD)
    config['Tasks'][name]['Kill']=""
    #tp1.join()
    #elif config['Tasks'][name]['status']=="-1":
    #  worklog="Stop {name} \n".format(name=name)
    #  WriteLog(worklog)
      #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
      #stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,str123+" Stop "+config['Tasks'][name]['nextstart']+" sec ",curses.A_BOLD)
    #else:
    #  worklog="Kill {name} \n".format(name=name)
    #  WriteLog(worklog)
    #  config['Tasks'][name]['status']="0"
    #  WorkQueue[config['Tasks'][name]['level']]['status']=0
    #  config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
    #  stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,str123+" Kill next start "+config['Tasks'][name]['nextstart']+" sec ",curses.A_BOLD)
    #Check_Work()
    #Schedule()

def Sub_producer(str123,T,name,level):
    global config
    global SubLevel
    config['Tasks'][name]['status']="1"
    config['Tasks'][name]['Sub']=level
    SubLevel[level]['status']=1
    SubLevel[level]['run']=name
    #str123.replace(config['Tasks'][name]['level'],level)
    #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
    pname="{0:10}".format(name)
    C="{0:4}".format(config['Tasks'][name]['C'])
    T="{0:4}".format(config['Tasks'][name]['T'])
    level2="{0:8}".format(level)
    worklog="Run Sub {name} in {level} excution {C} period {T}\n".format(name=pname,level=level2,C=C,T=T)
    WriteLog(worklog)
    #tp1=threading.Thread(target=TimeStart,args=(name,))
    #t2=threading.Thread(target=consumer,args=(workname,worklevel,))
    #tp1.start()
    config['Tasks'][name]['statusprint']=str123
    stdscr.move(int(config['Tasks'][name]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,str123+" start "+config['Tasks'][name]['status'],curses.A_BOLD)
    ggg=str123.split()
    #ggg[0] level ggg[1] ggg[2] ggg[3]
    #os.system("docker exec "+str123)
    #por=subprocess.run(["docker", "exec",ggg[0],ggg[1],ggg[2],ggg[3]])
    por=subprocess.run(["docker", "exec",level,ggg[3]])
    #if config['Tasks'][name]['status']!="-1":
    worklog="Finish {name} \n".format(name=name)
    WriteLog(worklog)
    if config['Tasks'][name]['Kill']!="1":
      config['Tasks'][name]['status']="0"
      config['Tasks'][name]['runtime']="0"
      #config['Tasks'][name]['c']=config['Tasks'][name][config['Tasks'][name]['orilevel']]
      config['Tasks'][name]['priority']="0"
      if config['Tasks'][name]['Sub']=="":
        if WorkQueue[config['Tasks'][name]['level']]['run']==name:
          WorkQueue[config['Tasks'][name]['level']]['run']=""
          WorkQueue[config['Tasks'][name]['level']]['status']=0
      else:
        SubLevel[config['Tasks'][name]['Sub']]['status']=0
        SubLevel[config['Tasks'][name]['Sub']]['run']=""
      config['Tasks'][name]['Sub']=""
      config['Tasks'][name]['level']=config['Tasks'][name]['orilevel']
      #config['Tasks'][name]['d']=str(int(config['Tasks'][name]['d'])+int(config['Tasks'][name]['d']))
      #if len(WorkQueue[config['Tasks'][name]['level']]['Queue'])>0:
      #  for qwname in WorkQueue[config['Tasks'][name]['level']]['Queue']:
      #    if qwname != name:
      #      config[qwname]['nextstart']=str(int(config[qwname]['nextstart'])+int(config['Tasks'][name]['c']))

    #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
      stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,str123+" OK next arrive "+config['Tasks'][name]['nextstart']+" sec "+config['Tasks'][name]['status'],curses.A_BOLD)
    config['Tasks'][name]['Kill']=""


def Schedule():
  global WorkQueue
  for level in WorkQueue:
    if CTconfig[level]['Container_Priority_Mode']=="CFS":
      for i in range(len(WorkQueue[level]['Queue'])):
        wname=WorkQueue[level]['Queue'].pop(0)
        #WorkQueue[level]['print']==WorkQueue[level]['level']+":"+str(WorkQueue[level]['Queue'])
        if config['Tasks'][wname]['status']=="-1": #判斷工作是否是暫停還是尚未執行
          ContWork(wname)
        else:
          Run_Work(wname)
 
    elif WorkQueue[level]['status']==0 and len(WorkQueue[level]['Queue'])>0:
      wname=WorkQueue[level]['Queue'].pop(0)
      #WorkQueue[level]['print']==WorkQueue[level]+":"+str(WorkQueue[level]['Queue'])
      WorkQueue[level]['run']=wname
      if config['Tasks'][wname]['status']=="-1":
        ContWork(wname)
      else:
        print("hhh")
        Run_Work(wname)
    
    #若有Sub_Level 則會將佇列中的工作搬移到空閒的Sub_Level
    if len(WorkQueue[level]['Sub'])>0:
      for SubL in WorkQueue[level]['Sub']:
        if SubLevel[SubL]['status']==0 and len(WorkQueue[level]['Queue'])>0:
          wname=WorkQueue[level]['Queue'].pop(0)
          #config['Tasks'][wname]['level']=SubL
          if config['Tasks'][wname]['status']=="0":   #工作尚未在任何容器下執行
            #orkQueue[config['Tasks'][wname]['level']]['print']=config['Tasks'][wname]['level']+":"+str(WorkQueue[config['Tasks'][wname]['level']]['Queue'])+" "+str(WorkQueue[config['Tasks'][wname]['level']]['status'])+" "+str(WorkQueue[config['Tasks'][wname]['level']]['run'])
            Sub_Work(wname,SubL)
          elif config['Tasks'][wname]['status']=="-1": #工作在其他容器內執行了 所以要進行工作搬移
            ContChangeLevel(wname,SubL)
            SubContWork(wname,SubL)
          #else:       
          #  WorkQueue[level]['Queue'].insert(0,wname)
    WorkQueue[level]['print']=WorkQueue[level]['level']+":"+str(WorkQueue[level]['Queue'])+" "+str(WorkQueue[level]['status'])+" "+str(WorkQueue[level]['run'])
    for SubN in WorkQueue[level]['Sub']:
      WorkQueue[level]['print']=WorkQueue[level]['print']+" "+SubLevel[SubN]['run']
    #WorkQueue[level]['print']=WorkQueue[level]['level']+":"+str(WorkQueue[level]['Queue'])+" "+str(WorkQueue[level]['status'])+" "+str(WorkQueue[level]['run'])     
    stdscr.move(int(WorkQueue[level]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(WorkQueue[level]['statuspr']),0,WorkQueue[level]['print'],curses.A_BOLD)

def RunWork(stdscr):
  i=0
  for wkname in config['Tasks'].keys():
    string="[process "+str(i+1)+": "+str(wkname)+" computing:%3d"%int(config['Tasks'][wkname]['c'])+" period:%3d"%int(config['Tasks'][wkname]['t'])+" level: "+str(config['Tasks'][wkname]['level'])+"]"
    stdscr.addstr(int(config['Tasks'][wkname]['workpr'])-5,0,string,curses.A_BOLD)
    try:
      sho=shutil.copy2(workfolder+str(wkname), multifolder+config['Tasks'][wkname]['level']+"/"+str(wkname))
      if len(WorkQueue[config['Tasks'][wkname]['level']]['Sub'])>0:
        for SubL in WorkQueue[config['Tasks'][wkname]['level']]['Sub']:
          jj=shutil.copy2(workfolder+str(wkname), multifolder+SubL+"/"+str(wkname))
    except FileExistsError:
      print("error")
    string2=str(wkname)+" was assigned to '"+sho+"'"
    stdscr.addstr(int(config['Tasks'][wkname]['statuspr'])-5,0,string2,curses.A_BOLD)
    i=i+1
  #stdscr.addstr(12,0,"Start press s!",curses.A_BOLD) 

def Start_Work():
  i=0
  for wkname in config['Tasks'].keys():
    workstats=str(config['Tasks'][wkname]['level'])+" timeout "+str(config['Tasks'][wkname]['c'])+" "+multifolder+str(config['Tasks'][wkname]['level'])+"/"+str(wkname)
    workperiod=config['Tasks'][wkname]['t']
    #config['Tasks'][wkname]['workpr']=str(pg1+i)
    #workname=str(workload[i]['WorkName'])
    #worklevel=str(workload[i]['level'])
    t1=threading.Thread(target=producer,args=(workstats,workperiod,wkname,))
    #t2=threading.Thread(target=consumer,args=(workname,worklevel,))
    t1.start()
    #t2.start()
    i=i+1

def Run_Work(wkname):
  global conifg
  config['Tasks'][wkname]['level']=config['Tasks'][wkname]['orilevel']
  workstats=str(config['Tasks'][wkname]['level'])+" timeout "+str(config['Tasks'][wkname]['c'])+" "+multifolder+str(config['Tasks'][wkname]['level'])+"/"+str(wkname)
  workperiod=config['Tasks'][wkname]['t']
  t1=threading.Thread(target=producer,args=(workstats,workperiod,wkname,))
  t1.start()

def Sub_Work(wkname,level):
  global conifg
  workstats=str(level)+" timeout "+str(config['Tasks'][wkname]['c'])+" "+multifolder+str(level)+"/"+str(wkname)
  workperiod=config['Tasks'][wkname]['t']
  t1=threading.Thread(target=Sub_producer,args=(workstats,workperiod,wkname,level,))
  t1.start()

def Preemption(name):
  StopWork(WorkQueue[config['Tasks'][name]['level']]['run'])
  wname=WorkQueue[config['Tasks'][name]['level']]['Queue'].pop(0)
  WorkQueue[config['Tasks'][name]['level']]['run']=wname
  if config['Tasks'][wname]['status']=="0":
    Run_Work(wname)
  elif config['Tasks'][name]['status']=="-1":
    ContWork(wname) 
def LevelSort(level):
  global WorkQueue
  global config
  for i in range(len(WorkQueue[level]['Queue'])):
    for j in range(i):
      aa=int(config[WorkQueue[level]['Queue'][j]]['priority'])
      bb=int(config[WorkQueue[level]['Queue'][i]]['priority'])
      if aa < bb :
        temp=WorkQueue[level]['Queue'][j]
        WorkQueue[level]['Queue'][j]=WorkQueue[level]['Queue'][i]
        WorkQueue[level]['Queue'][i]=temp


def WorkSort(config):
  global WorkQueue
  for level in WorkQueue:
    for i in range(len(WorkQueue[level]['Queue'])):
      for j in range(i):
        aa=int(config[WorkQueue[level]['Queue'][j]]['priority'])
        bb=int(config[WorkQueue[level]['Queue'][i]]['priority'])
        if aa < bb :
          temp=WorkQueue[level]['Queue'][j]
          WorkQueue[level]['Queue'][j]=WorkQueue[level]['Queue'][i]
          WorkQueue[level]['Queue'][i]=temp
  #print(WorkQueue)
 # kk=WorkQueue['level1']['Queue'].pop()
  #print(kk)
 # print(WorkQueue)
 # time.sleep(5)

#def priority_method2(config,Ch):
#  if Ch=="RM":
#    for level in WorkQueue:
#      Wtemp=[]
#      for wname in config['Tasks'].keys():
#        if config['Tasks'][wname]['level']==level:
#          Wtemp.append(wname)
#      for i in range(len(Wtemp)):
#        for j in range(i):
#          aa=int(config[Wtemp[j]]['t'])
#          bb=int(config[Wtemp[i]]['t'])
#          if aa > bb :
#            temp=Wtemp[j]
#            Wtemp[j]=Wtemp[i]
#            Wtemp[i]=temp
#      length=len(Wtemp)
#      for wname in Wtemp:
#        config['Tasks'][wname]['priority']=str(length)
#        length=length-1
      #for wname in Wtemp:
        #print(level+":"+wname+":"+config['Tasks'][wname]['priority'])

def fd():
  for level in WorkQueue:
    priority_mod(config,CTconfig[level]['Container_Priority_Mode'],level)
    for i in range(len(WorkQueue[level]['Queue'])):
      for j in range(i):
        aa=int(config[WorkQueue[level]['Queue'][j]]['priority'])
        bb=int(config[WorkQueue[level]['Queue'][i]]['priority'])
        if aa < bb :
          temp=WorkQueue[level]['Queue'][j]
          WorkQueue[level]['Queue'][j]=WorkQueue[level]['Queue'][i]
          WorkQueue[level]['Queue'][i]=temp
 
def priority_mod(config,Ch,level):
  Wtemp=WorkQueue[level]['Queue'].copy()
  if WorkQueue[level]['run']!="":
    Wtemp.append(WorkQueue[level]['run'])
  if Ch=="RM":
    for i in range(len(Wtemp)):
      for j in range(i):
        aa=int(config[Wtemp[j]]['t'])
        bb=int(config[Wtemp[i]]['t'])
        if aa > bb :
          temp=Wtemp[j]
          Wtemp[j]=Wtemp[i]
          Wtemp[i]=temp
      length=len(Wtemp)
      for wname in Wtemp:
        config['Tasks'][wname]['priority']=str(length)
        length=length-1
      #for wname in Wtemp:
      #  print(wname+":"+config['Tasks'][wname]['priority'])

  if Ch=="EDF":
    for i in range(len(Wtemp)):
      for j in range(i):
        aa=int(config[Wtemp[i]]['nextstart'])-settime
        bb=int(config[Wtemp[j]]['nextstart'])-settime
        if aa > bb :
          temp=Wtemp[i]
          Wtemp[i]=Wtemp[j]
          Wtemp[j]=temp
      length=len(Wtemp)
      for wname in Wtemp:
        config['Tasks'][wname]['priority']=str(length)
        length=length-1

def priority_method(config,Ch):
  global settime
  if Ch=="RM":
    Wtemp=config['Tasks'].keys()
    for i in range(len(Wtemp)):
      for j in range(i):
        aa=int(config[Wtemp[j]]['t'])
        bb=int(config[Wtemp[i]]['t'])
        if aa > bb :
          temp=Wtemp[j]
          Wtemp[j]=Wtemp[i]
          Wtemp[i]=temp
      length=len(Wtemp)
      for wname in Wtemp:
        config['Tasks'][wname]['priority']=str(length)
        length=length-1
      #for wname in Wtemp:
      #  print(wname+":"+config['Tasks'][wname]['priority'])
  
  if Ch=="EDF":
    Wtemp=config['Tasks'].keys()
    for i in range(len(Wtemp)):
      for j in range(i):
        aa=int(config[Wtemp[i]]['nextstart'])-settime
        bb=int(config[Wtemp[j]]['nextstart'])-settime
        if aa > bb :
          temp=Wtemp[i]
          Wtemp[i]=Wtemp[j]
          Wtemp[j]=temp
      length=len(Wtemp)
      for wname in Wtemp:
        config['Tasks'][wname]['priority']=str(length)
        length=length-1
      #for wname in Wtemp:
      #  print(wname+":"+config['Tasks'][wname]['priority'])

def read_config(workloadname):
    global config
    global WorkQueue
    config=ConfigObj("./config/Workload/"+workloadname)
    i=0  
    for name in config['Tasks'].keys():
       try:
         c=subprocess.check_output(['pidof',name])
         c=c.decode('utf-8').split("\n")[0]
         if not c is None:
           os.system("kill -9 $(pidof "+name+")")
       except:
         ca=1
       #config['Tasks'][name]['c']=config['Tasks'][name][config['Tasks'][name]['level']]
       config['Tasks'][name]['c']=config['Tasks'][name]['Execution_Time']
       config['Tasks'][name]['d']=config['Tasks'][name]['Deadline_Time']
       config['Tasks'][name]['t']=config['Tasks'][name]['Period_Time']
       config['Tasks'][name]['runtime']="0"
       config['Tasks'][name]['status']='0'
       config['Tasks'][name]['print']="{0:10}".format(name)
       config['Tasks'][name]['statusprint']=name
       config['Tasks'][name]['workpr']=str(workprintline+i)
       config['Tasks'][name]['nextstart']=str(config['Tasks'][name]['Arrival_Time'])
       config['Tasks'][name]['priority']="0"
       config['Tasks'][name]['Sub']=""
       config['Tasks'][name]['Kill']=""
       i=i+1    
    j=0

    for name in config['Tasks'].keys():
      for Ct in WorkQueue:
        if config['Tasks'][name]['Assignment_Level']==WorkQueue[Ct]['level']:
           config['Tasks'][name]['level']=Ct
           config['Tasks'][name]['orilevel']=Ct
   
    for name in config['Tasks'].keys():
      config['Tasks'][name]['statuspr']=str(workprintline+i+j+1)
      if config['Tasks'][name]['nextstart']=="0":
        WorkQueue[config['Tasks'][name]['level']]['Queue'].append(name)
        config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
      j=j+1
     
    k=0

    for level in WorkQueue:
      WorkQueue[level]['statuspr']=str(workprintline+i+j+k+2)
      WorkQueue[level]['print']=WorkQueue[level]['level']+":"+str(WorkQueue[level]['Queue'])
      WorkQueue[level]['run']="" 
      k=k+1
      print(level+" "+CTconfig[level]['Container_Priority_Mode'])
      print(str(WorkQueue[level]['Queue'])) 
    #print(config['Tasks'][name]) 
    priority_method(config,"RM")
    WorkSort(config)
    #print(levellist.index("level1"))
    
    time.sleep(5)

def get_io():
    global cpu_num
    global cpu_info
    cpu_num=psutil.cpu_count(logical=True)
    cpu_info=psutil.cpu_percent(interval=1,percpu=True)

def Schedule_Analytics():
  for name in config['Tasks'].keys():
    print("h") 



def Check_Work():
  global config
  global WorkQueue
  global sysconfig

  AL()
  for name in config['Tasks'].keys():
      #if config['Tasks'][name]['nextstart']==str(settime) and config['Tasks'][name]['nextstart']!="0":
      #   KillWork(name)
        #WorkSort(config)   
      if config['Tasks'][name]['nextstart']==str(settime) and config['Tasks'][name]['nextstart']!="0":
        #WorkQueue[config['Tasks'][name]['level']]['Queue'].append(name)
        fd()
        #if sysconfig['ComityRT']['Scheduleability_analysis']=="EDF":
          #priority_method(config,"EDF")
        
        if len(WorkQueue[config['Tasks'][name]['level']]['Queue'])>0: #加入的工作優先權向前排
          ch=0
          for i in range(len(WorkQueue[config['Tasks'][name]['level']]['Queue'])): #將工作依照優先權加入的佇列中
            if config['Tasks'][name]['priority'] > config[WorkQueue[config['Tasks'][name]['level']]['Queue'][i]]['priority']:
              if (name not in WorkQueue[config['Tasks'][name]['level']]['Queue']) and (WorkQueue[config['Tasks'][name]['level']]['run']!=name):
                WorkQueue[config['Tasks'][name]['level']]['Queue'].insert(i,name)
                #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
                stdscr.move(int(config['Tasks'][name]['statuspr']),0)
                stdscr.clrtoeol()
                stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,config['Tasks'][name]['statusprint']+" add the Queue "+config['Tasks'][name]['status'],curses.A_BOLD)
                ch=1
                break

          if ch==0:#假設工作是佇列優先權最低
            if (name not in WorkQueue[config['Tasks'][name]['level']]['Queue']) and (WorkQueue[config['Tasks'][name]['level']]['run']!=name):
              WorkQueue[config['Tasks'][name]['level']]['Queue'].append(name)
              #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
              stdscr.move(int(config['Tasks'][name]['statuspr']),0)
              stdscr.clrtoeol()
              stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,config['Tasks'][name]['statusprint']+" add the Queue "+config['Tasks'][name]['status'],curses.A_BOLD)
          #判斷新工作的優先權是否比運行中工作的優先權高 有就切換運行並將工作排回柱列
          #if WorkQueue[config['Tasks'][name]['level']]['run']!="":
          #  if config[WorkQueue[config['Tasks'][name]['level']]['run']]['priority'] < config['Tasks'][name]['priority']:
              #StopWork(WorkQueue[config['Tasks'][name]['level']]['run'])
              #wname=WorkQueue[config['Tasks'][name]['level']]['Queue'].pop(0)
              #WorkQueue[config['Tasks'][name]['level']]['run']=wname
              #Run_Work(wname)
              #Preemption(name)
        else:#佇列沒工作
          if (name not in WorkQueue[config['Tasks'][name]['level']]['Queue']) and (WorkQueue[config['Tasks'][name]['level']]['run']!=name):
            WorkQueue[config['Tasks'][name]['level']]['Queue'].append(name)
            #config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
            stdscr.move(int(config['Tasks'][name]['statuspr']),0)
            stdscr.clrtoeol()
            stdscr.addstr(int(config['Tasks'][name]['statuspr']),0,config['Tasks'][name]['statusprint']+" add the Queue "+config['Tasks'][name]['status'],curses.A_BOLD)
          #Preemption(name)
        
        config['Tasks'][name]['nextstart']=str(int(config['Tasks'][name]['nextstart'])+int(config['Tasks'][name]['t']))
      
      if sysconfig['ComityRT']['Sys_Preemption']=="true" or sysconfig['ComityRT']['Sys_Preemption']=="True":
        if WorkQueue[config['Tasks'][name]['level']]['run']!="":
          if name in WorkQueue[config['Tasks'][name]['level']]['Queue']:       
            fd()
            if config[WorkQueue[config['Tasks'][name]['level']]['run']]['priority'] < config['Tasks'][name]['priority']:
              #print("www"+name)
              worklog="{name} Preemption {name2}\n".format(name=name,name2=WorkQueue[config['Tasks'][name]['level']]['run'])
              WriteLog(worklog)
              Preemption(name)
      fd()
      WorkQueue[config['Tasks'][name]['level']]['print']=WorkQueue[config['Tasks'][name]['level']]['level']+":"+str(WorkQueue[config['Tasks'][name]['level']]['Queue'])+" "+str(WorkQueue[config['Tasks'][name]['level']]['status'])+" "+str(WorkQueue[config['Tasks'][name]['level']]['run'])
      
      stdscr.move(int(WorkQueue[config['Tasks'][name]['level']]['statuspr']),0)
      stdscr.clrtoeol()
      stdscr.addstr(int(WorkQueue[config['Tasks'][name]['level']]['statuspr']),0,WorkQueue[config['Tasks'][name]['level']]['print'],curses.A_BOLD)
 
def main(stdscr,workloadname):# Create a string of text based on the Figlet font object
  global worktime
  title = pyfiglet.figlet_format("ComityRT", font = "small" ) 
# stdscr = curses.initscr() # create a curses object
# Create a couple of color definitions
  curses.start_color()
  curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
  read_config(workloadname)
  # Write the BIG TITLE text string
  #stdscr.addstr(1,0, title,curses.color_pair(1) )
  #stdscr.addstr(8,0, "Sensor 1: GPIO 7 Temperature Reading" ,curses.A_BOLD)
 
  # Cycle getting new data, enter a 'q' to quit
  stdscr.nodelay(1)
  k = 0
  pad = curses.newpad(25,100)
  RunWork(pad)
  pad.refresh(0,0,0,0,20,60)
  #time.sleep(5)
  #Start_Work()
  #stdscr.addstr(18,0,"abc",curses.A_BOLD)
  global settime
  settime=0
  stdscr.addstr(6,0,"time:"+str(settime)+" sec",curses.A_BOLD)
  tp1=threading.Thread(target=SystemTimeStart,args=())
  tp1.start()
  Check_Work()
  Schedule()
  while (k != ord('q')):
    if int(settime%20)==0 or settime==0:
      p=settime/20
      gg=""
      for name in config['Tasks'].keys():
        config['Tasks'][name]['print']="{0:10}".format(name)
        stdscr.move(int(config['Tasks'][name]['workpr']),0)
        stdscr.clrtoeol()
        stdscr.addstr(int(config['Tasks'][name]['workpr']),0,config['Tasks'][name]['print'],curses.A_BOLD) 
      for i in range(int(p)*20,20*(int(p)+1)+1,5):
        gg=gg+str(i)+"   "
      worktime="{0:10}".format("time")+gg
    stdscr.addstr(8,0,worktime,curses.A_BOLD)

    for level in WorkQueue:
      WorkQueue[level]['print']=WorkQueue[level]['level']+":"+str(WorkQueue[level]['Queue'])+" "+str(WorkQueue[level]['status'])+" "+str(WorkQueue[level]['run'])
      stdscr.move(int(WorkQueue[level]['statuspr']),0)
      stdscr.clrtoeol()
          
    ch=0
    
    get_io()
    for i in range(cpu_num):
      ppi=math.ceil(cpu_info[i]/4)
      string=""
      for j in range(ppi):
        string=string+"▇"
      stdscr.move(1+i,0)
      stdscr.clrtoeol()
      status="core "+str(i)+"|{0:25}".format(string)+"| "+str(cpu_info[i])+"%"
      stdscr.addstr(1+i,0,status,curses.A_BOLD)
      #stdscr.clrtobot() 
    #stdscr.addstr(9,0,"{0:10}".format("work1")+"↑▄▄▄▄▄▄▄▄▄▄▄▄▄",curses.A_BOLD)
    #stdscr.addstr(10,0,"{0:10}".format("work1")+"↑▄▄▄▄▄▄▄▄▄▄▄▄▄",curses.A_BOLD)
    #stdscr.addstr(11,0,"{0:10}".format("work1")+"↑▄▄▄▄▄▄▄▄▄▄▄▄▄",curses.A_BOLD)
    
    #stdscr.addstr(8,0,worktime,curses.A_BOLD)
    stdscr.move(29,0)
    stdscr.clrtoeol()
    #stdscr.move(30,0)
    #stdscr.clrtoeol()
    #stdscr.move(31,0)
    #stdscr.clrtoeol()
    #stdscr.move(32,0)
    #stdscr.clrtoeol()
    stdscr.addstr(29,0,"level "+config['work4']['statusprint']+" "+config['work4']['nextstart']+" status "+config['work4']['status']+" priority "+config['work4']['priority']+" "+config['work4']['d'],curses.A_BOLD)
    #stdscr.addstr(30,0,"level "+config['work3']['statusprint']+" "+config['work3']['nextstart']+" status "+config['work3']['status']+" priority "+config['work3']['priority'],curses.A_BOLD)
   # 
   # stdscr.addstr(31,0,"level "+config['w1']['statusprint']+" "+config['w1']['nextstart']+" status "+config['w1']['status']+" priority "+config['w1']['priority']+" "+config['w1']['Sub'],curses.A_BOLD)
    #stdscr.addstr(32,0,"wwwww"+WorkQueue['level3']['run'],curses.A_BOLD)

    #s=0
    #m=0
    if settime>60:
      m=settime/60
      s=settime-(60*int(m))
      timeprint=str(int(m))+" min "+str(int(s))+" sec"
    else:
      timeprint=str(settime)+" sec"
    
    k = stdscr.getch()
 
  curses.endwin()
  WriteLog("System Running Total {} \n".format(timeprint))

cfg = configparser.ConfigParser()
cfg.read("./config/System.ini")
choice=cfg.sections()
workloadname=Choose_config(choice)
stdscr = curses.initscr()
main(stdscr,workloadname)
#config=ConfigObj(workloadname)
#for name in config['Tasks'].keys():
#  try:
#     c=subprocess.check_output(['pidof',name])
#     c=c.decode('utf-8').split("\n")[0]
#     if not c is None:
#       os.system("kill -9 $(pidof "+name+")")
#  except:
#     print("Task all Clear")
