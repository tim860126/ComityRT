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

workfolder="./work/"

multifolder="./multi-level/"

logfolder="./logs/"

workprintline=9

def WriteLog(string):
  localtime = time.localtime()
  localtime = time.strftime("%I:%M:%S ", localtime)
  f = open(logname,'a+')
  f.write(localtime+string)
  f.close()
def ContWork(wname):
  global WorkQueue
  global config
  #os.system("./ContWork.sh "+wname);
  WorkQueue[config[wname]['level']]['status']=1 
  config[wname]['status']="1"
  os.system("kill -CONT $(pidof "+wname+")")
  #stdscr.addstr(29,0,wname+":"+config[wname]['status'],curses.A_BOLD)
def KillWork(wname):
  global workQueue
  global config

  #WorkQueue[config[wname]['level']]['status']=0
  config[wname]['status']="-2"
  os.system("kill -9 $(pidof "+wname+")")

def StopWork(wname):
  global WorkQueue
  global config
  
  #os.system("./StopWork.sh "+wname);
  WorkQueue[config[wname]['level']]['status']=0 #佇列旗標進程更改為空閒
  WorkQueue[config[wname]['level']]['Queue'].append(wname)#重新加入到佇列中
  config[wname]['status']="-1" #工作狀態顯示為暫停
  os.system("kill -STOP $(pidof "+wname+")")
  #stdscr.addstr(28,0,wname+":"+config[wname]['status'],curses.A_BOLD)

def Choose_config(choices):
  global logname
  global WorkQueue
  WorkQueue={}
  questions = [
  inquirer.List('action',
                message="Choose An configuration file",
                choices=choices,
            ),
  ]
  answers = inquirer.prompt(questions)
  cfg = configparser.ConfigParser()
  print(answers['action'])
  localtime = time.localtime()
  localtime = time.strftime("%Y-%m-%d-%I:%M:%S", localtime)
  runingstr="Running {system} system at {starttime}\n".format(system=answers['action'],starttime=localtime)
  logname=logfolder+"ComityRT."+answers['action']+"."+str(localtime)
  f = open(logname,'w+')
  f.write(runingstr)
  f.close()
  cfg.read("./config/"+answers['action']+".ini")
  levellist=cfg.sections()
  levellist.remove("ComityRT")
  for level in levellist:
    WorkQueue[level]=dict()
    WorkQueue[level]['status']=0
    WorkQueue[level]['Queue']=list()
 
  return cfg['ComityRT']['Workload_Name']
def SystemTimeStart():
   global settime
   global config
   while(1):
     time.sleep(1)
     settime=settime+1
     for name in config.sections():
       if(config[name]['status']=="0" or config[name]['status']=="-1"):
         config[name]['print']=config[name]['print']+" "
       elif config[name]['status']=="1":
         config[name]['print']=config[name]['print']+"▄"
def TimeStart(name):
   #string="{0:10}".format(name)+"↑"
   #time.sleep(1)
   #string=config[name]['print']
   #time.sleep(1)
   i=0;
   j=0; 
   while(config[name]['status']=='1' or config[name]['status']=='-1'):
     
     time.sleep(1)
     while(config[name]['status']=='-1'):
       i=i+1 
     #string=string+"▄"
       #config[name]['print']=config[name]['print']+"▄"
     stdscr.addstr(int(config[name]['workpr']),0,config[name]['print'],curses.A_BOLD)
     j=j+1
     #if len(WorkQueue[config[name]['level']]['Queue'])>0:
     #   for qwname in WorkQueue[config[name]['level']]['Queue']:
     #     if qwname != name:
     #       config[qwname]['nextstart']=str(int(config[qwname]['nextstart'])+1)  
#config[name]['print']=string
def producer(str123,T,name):
    global config
    global WorkQueue
    config[name]['status']="1"
    WorkQueue[config[name]['level']]['status']=1
    pname="{0:10}".format(name)
    C="{0:4}".format(config[name]['C'])
    T="{0:4}".format(config[name]['T'])
    level="{0:8}".format(config[name]['level'])
    worklog="Run {name} in {level} excution {C} period {T}\n".format(name=pname,level=level,C=C,T=T)
    WriteLog(worklog)
    tp1=threading.Thread(target=TimeStart,args=(name,))
    #t2=threading.Thread(target=consumer,args=(workname,worklevel,))
    tp1.start()
    stdscr.move(int(config[name]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(config[name]['statuspr']),0,str123,curses.A_BOLD)
    ggg=str123.split()
    #ggg[0] level ggg[1] ggg[2] ggg[3]
    #os.system("docker exec "+str123)
    #por=subprocess.run(["docker", "exec",ggg[0],ggg[1],ggg[2],ggg[3]])
    por=subprocess.run(["docker", "exec",ggg[0],ggg[3]])
    if config[name]['status']!="-1":
      worklog="Finish {name} \n".format(name=name)
      WriteLog(worklog)
      config[name]['status']="0"
      WorkQueue[config[name]['level']]['status']=0
 
      #if len(WorkQueue[config[name]['level']]['Queue'])>0:
      #  for qwname in WorkQueue[config[name]['level']]['Queue']:
      #    if qwname != name:
      #      config[qwname]['nextstart']=str(int(config[qwname]['nextstart'])+int(config[name]['c']))
     
      config[name]['nextstart']=str(int(config[name]['nextstart'])+int(config[name]['t']))
      stdscr.addstr(int(config[name]['statuspr']),0,str123+" OK next arrive "+config[name]['nextstart']+" sec ",curses.A_BOLD)
    #tp1.join()
    elif config[name]['status']=="-1":
      worklog="Stop {name} \n".format(name=name)
      WriteLog(worklog)
      #config[name]['nextstart']=str(int(config[name]['nextstart'])+int(config[name]['t']))
      #stdscr.addstr(int(config[name]['statuspr']),0,str123+" Stop "+config[name]['nextstart']+" sec ",curses.A_BOLD)
    else:
      worklog="Kill {name} \n".format(name=name)
      WriteLog(worklog)
      config[name]['status']="0"
      WorkQueue[config[name]['level']]['status']=0
      config[name]['nextstart']=str(int(config[name]['nextstart'])+int(config[name]['t']))
      stdscr.addstr(int(config[name]['statuspr']),0,str123+" Kill next start "+config[name]['nextstart']+" sec ",curses.A_BOLD)

def Schedule():
  global WorkQueue
  for level in WorkQueue:
    if WorkQueue[level]['status']==0 and len(WorkQueue[level]['Queue'])>0:
      wname=WorkQueue[level]['Queue'].pop(0)
      WorkQueue[level]['print']=level+":"+str(WorkQueue[level]['Queue'])
      WorkQueue[level]['run']=wname
      if config[wname]['status']=="-1":
        ContWork(wname)
      else:
        Run_Work(wname)

    stdscr.move(int(WorkQueue[level]['statuspr']),0)
    stdscr.clrtoeol()
    stdscr.addstr(int(WorkQueue[level]['statuspr']),0,WorkQueue[level]['print'],curses.A_BOLD)

def RunWork(stdscr):
  i=0
  for wkname in config.sections():
    string="[process "+str(i+1)+": "+str(wkname)+" computing:%3d"%int(config[wkname]['c'])+" period:%3d"%int(config[wkname]['t'])+" level: "+str(config[wkname]['level'])+"]"
    stdscr.addstr(int(config[wkname]['workpr'])-5,0,string,curses.A_BOLD)
    try:
      sho=shutil.copy2(workfolder+str(wkname), multifolder+config[wkname]['level']+"/"+str(wkname))
    except FileExistsError:
      print("error")
    string2=str(wkname)+" was assigned to '"+sho+"'"
    stdscr.addstr(int(config[wkname]['statuspr'])-5,0,string2,curses.A_BOLD)
    i=i+1
  #stdscr.addstr(12,0,"Start press s!",curses.A_BOLD) 

def Start_Work():
  i=0
  for wkname in config.sections():
    workstats=str(config[wkname]['level'])+" timeout "+str(config[wkname]['c'])+" "+multifolder+str(config[wkname]['level'])+"/"+str(wkname)
    workperiod=config[wkname]['t']
    #config[wkname]['workpr']=str(pg1+i)
    #workname=str(workload[i]['WorkName'])
    #worklevel=str(workload[i]['level'])
    t1=threading.Thread(target=producer,args=(workstats,workperiod,wkname,))
    #t2=threading.Thread(target=consumer,args=(workname,worklevel,))
    t1.start()
    #t2.start()
    i=i+1

def Run_Work(wkname):
  workstats=str(config[wkname]['level'])+" timeout "+str(config[wkname]['c'])+" "+multifolder+str(config[wkname]['level'])+"/"+str(wkname)
  workperiod=config[wkname]['t']
  t1=threading.Thread(target=producer,args=(workstats,workperiod,wkname,))
  t1.start()

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
  print(WorkQueue)
 # kk=WorkQueue['level1']['Queue'].pop()
  #print(kk)
 # print(WorkQueue)
  time.sleep(5)
def priority_method(config,Ch):
  if Ch=="RM":
    for level in WorkQueue:
      Wtemp=[]
      for wname in config.sections():
        if config[wname]['level']==level:
          Wtemp.append(wname)
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
        config[wname]['priority']=str(length)
        length=length-1
      for wname in Wtemp:
        print(level+":"+wname+":"+config[wname]['priority'])

def read_config(workloadname):
    global config
    global WorkQueue
    config = configparser.ConfigParser()
    config.read(workloadname)
    i=0  
    for name in config.sections():
       config[name]['status']='0'
       config[name]['print']="{0:10}".format(name)
       config[name]['workpr']=str(workprintline+i)
       config[name]['nextstart']=str(config[name]['a'])
       config[name]['priority']="0"
       i=i+1    
    j=0
    for name in config.sections():
      config[name]['statuspr']=str(workprintline+i+j+1)
      if config[name]['nextstart']=="0":
        WorkQueue[config[name]['level']]['Queue'].append(name)
      j=j+1
     
    k=0
    for level in WorkQueue:
      WorkQueue[level]['statuspr']=str(workprintline+i+j+k+2)
      WorkQueue[level]['print']=level+":"+str(WorkQueue[level]['Queue'])
      k=k+1
    priority_method(config,"RM")
    WorkSort(config)
    time.sleep(5)
def get_io():
    global cpu_num
    global cpu_info
    cpu_num=psutil.cpu_count(logical=True)
    cpu_info=psutil.cpu_percent(interval=1,percpu=True)
 
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
  tp1=threading.Thread(target=SystemTimeStart,args=())
  tp1.start()
  while (k != ord('q')):
    if int(settime%20)==0 or settime==0:
      p=settime/20
      gg=""
      for name in config.sections():
        config[name]['print']="{0:10}".format(name)
        stdscr.move(int(config[name]['workpr']),0)
        stdscr.clrtoeol()
        stdscr.addstr(int(config[name]['workpr']),0,config[name]['print'],curses.A_BOLD) 
      for i in range(int(p)*20,20*(int(p)+1)+1,5):
        gg=gg+str(i)+"   "
      worktime="{0:10}".format("time")+gg
    #stdscr.clear()
    #Start_Work()
    #stdscr.addstr(1,0, title,curses.color_pair(1) )
    #if settime%15==0 and settime!=0:
    #  Start_Work()
    #
    #for name in config.sections():
    #  if config[name]['nextstart']==str(settime) and settime!=0:
    #    Run_Work(name) 
    #
    ch=0
    for name in config.sections():
      if config[name]['nextstart']==str(settime) and config[name]['nextstart']!="0":
        #WorkQueue[config[name]['level']]['Queue'].append(name)
        
        if len(WorkQueue[config[name]['level']]['Queue'])>0: #加入的工作優先權向前排
          ch=0
          for i in range(len(WorkQueue[config[name]['level']]['Queue'])): #將工作依照優先權加入的佇列中
            if config[name]['priority'] > config[WorkQueue[config[name]['level']]['Queue'][i]]['priority']:
              WorkQueue[config[name]['level']]['Queue'].insert(i,name)
              ch=1
              break
          
          if ch==0:#假設工作是佇列優先權最低
            WorkQueue[config[name]['level']]['Queue'].append(name)
        
          if config[WorkQueue[config[name]['level']]['run']]['priority'] < config[name]['priority']:
            StopWork(WorkQueue[config[name]['level']]['run'])
            wname=WorkQueue[config[name]['level']]['Queue'].pop(0)
            WorkQueue[config[name]['level']]['run']=wname
            Run_Work(wname) 

        else:#佇列沒工作
          WorkQueue[config[name]['level']]['Queue'].append(name)
          if config[WorkQueue[config[name]['level']]['run']]['priority'] < config[name]['priority']:
            StopWork(WorkQueue[config[name]['level']]['run'])
            
            wname=WorkQueue[config[name]['level']]['Queue'].pop(0)
            WorkQueue[config[name]['level']]['run']=wname
            Run_Work(wname)
 
        WorkQueue[config[name]['level']]['print']=config[name]['level']+":"+str(WorkQueue[config[name]['level']]['Queue'])
	        
        stdscr.move(int(WorkQueue[config[name]['level']]['statuspr']),0)
        stdscr.clrtoeol()
        stdscr.addstr(int(WorkQueue[config[name]['level']]['statuspr']),0,WorkQueue[config[name]['level']]['print'],curses.A_BOLD)
    
    Schedule()
    
    #for level in WorkQueue:
    #  if WorkQueue[level]['status']==0 and len(WorkQueue[level]['Queue'])>0:
    #    wname=WorkQueue[level]['Queue'].pop(0)
    #    WorkQueue[level]['print']=level+":"+str(WorkQueue[level]['Queue'])
    #    WorkQueue[level]['run']=wname
    #    Run_Work(wname)
    #  
    #  stdscr.move(int(WorkQueue[level]['statuspr']),0)
    #  stdscr.clrtoeol()
    #  stdscr.addstr(int(WorkQueue[level]['statuspr']),0,WorkQueue[level]['print'],curses.A_BOLD)
    
    if settime==8:
      KillWork("work3")
        
    
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
    
    stdscr.addstr(8,0,worktime,curses.A_BOLD)
    #stdscr.addstr(21,0,"{0:10}".format("time")+"1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20",curses.A_BOLD)
    s=0
    m=0
    if settime>60:
      m=settime/60
      s=settime-(60*int(m))
      timeprint=str(int(m))+" min "+str(int(s))+" sec"
    else:
      timeprint=str(settime)+" sec"
    stdscr.addstr(6,0,"time:"+str(timeprint),curses.A_BOLD)
    stdscr.refresh()
    #for name in config.sections():
    #  if(config[name]['status']=="0" or config[name]['status']=="-1"):
    #    config[name]['print']=config[name]['print']+" "
    #  elif config[name]['status']=="1":
    #    config[name]['print']=config[name]['print']+"▄"
    #settime=settime+1
    #stdscr.addstr(15,0,config.sections()[0],curses.A_BOLD)
    
    k = stdscr.getch()
 
  curses.endwin()
  WriteLog("System Running Total {} \n".format(timeprint))
  raise Exception

cfg = configparser.ConfigParser()
cfg.read("System.ini")
choice=cfg.sections()
workloadname=Choose_config(choice)
stdscr = curses.initscr()
main(stdscr,workloadname)
