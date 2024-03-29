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

def Choose_config(choices):
  global logname
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
  return cfg['ComityRT']['Workload_Name']

def TimeStart(name):
   #string="{0:10}".format(name)+"↑"
   time.sleep(1)
   #string=config[name]['print']
    
   while(config[name]['status']=='1'):
     time.sleep(1)
     #string=string+"▄"
     config[name]['print']=config[name]['print']+"▄"
     stdscr.addstr(int(config[name]['workpr']),0,config[name]['print'],curses.A_BOLD)
   #config[name]['print']=string
   
def producer(str123,T,name):
    global config
    config[name]['status']="1"
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
    os.system("docker exec "+str123)
    worklog="Finish {name} \n".format(name=name)
    WriteLog(worklog)
    config[name]['status']="0"
    config[name]['nextstart']=str(int(config[name]['nextstart'])+int(config[name]['t']))
    stdscr.addstr(int(config[name]['statuspr']),0,str123+" OK next start "+config[name]['nextstart']+" sec",curses.A_BOLD)
    #tp1.join()
def RunWork(stdscr):
  i=0
  for wkname in config.sections():
    string="[process "+str(i+1)+": "+str(wkname)+" computing:%3d"%int(config[wkname]['c'])+" period:%3d"%int(config[wkname]['t'])+" level: "+str(config[wkname]['level'])+"]"
    stdscr.addstr(int(config[wkname]['workpr'])-5,0,string,curses.A_BOLD)
    sho=shutil.copy2(workfolder+str(wkname), multifolder+config[wkname]['level']+"/"+str(wkname))
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


def read_config(workloadname):
    global config
    config = configparser.ConfigParser()
    config.read(workloadname)
    i=0  
    for name in config.sections():
       config[name]['status']='0'
       config[name]['print']="{0:10}".format(name)
       config[name]['workpr']=str(workprintline+i)
       config[name]['nextstart']=str(0)
       i=i+1    
    j=0
    for name in config.sections():
      config[name]['statuspr']=str(workprintline+i+j+1)
      j=j+1

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
  Start_Work()
  #stdscr.addstr(18,0,"abc",curses.A_BOLD)
  global settime
  settime=0
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
    for name in config.sections():
      if config[name]['nextstart']==str(settime) and settime!=0:
        Run_Work(name) 
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
    for name in config.sections():
      if(config[name]['status']=="0"):
        config[name]['print']=config[name]['print']+" "
    settime=settime+1
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
