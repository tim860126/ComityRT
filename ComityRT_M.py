import configparser
import inquirer
import os
import copy
import subprocess
import prettytable as pt
import time
import pyfiglet	
import threading
from progressbar import *
from configobj import ConfigObj

#config = configparser.ConfigParser()


Config_MainList=["Num_Criticality_Level","Sched_Algorithm","Sys_Max_Num_Cores","Sys_Use_Cores","Sys_Preemption","TDF_Filename","Container_Filename","Criticality_Level_Filename","Execution_Level_Mode","Task_Move","Back"]

Config_ConList=["Container_Use_Cores","Container_Cores_Weights","Container_Memory_Limit","Container_Priority_Mode","Back"]


Num_Criticality_Level=""

Sched_Algorithm=""

Sys_Max_Num_Cores=""

Sys_Use_Cores=""

Sys_Preemption=""

TDF_Filename=""

Container_Filename=""

Criticality_Level_Filename=""

Execution_Level_Mode=""

Task_Move=""

Ciritical_container=[]

key=""
option=""

def Show_System_Status():
  #config = configparser.ConfigParser()
  #config.read('System.ini')
  config = ConfigObj('./config/System.ini')
  #sysname=config.sections()
  sysname=config.keys()
  tb1 = pt.PrettyTable()
  tb1.field_names = ["System","Status"] 
  
  for sname in sysname:
    #config = configparser.ConfigParser()
    #config =ConfigObj('./config/'+sname+'.ini')
    config=ConfigObj('./config/System/'+sname+'.ini')
    #config.read('./config/'+sname+'.ini')
    CTFilename=config['ComityRT']['Container_Filename']
    CTconfig=ConfigObj('./config/Container/'+CTFilename)
    Criti_Name = CTconfig.keys()
    sysinfo="" 
    syserror=""
    for cname in Criti_Name:
      SubL=[]
      Del=[]
      status=subprocess.check_output(["sh","CheckDocker.sh",cname])   
      
      stauts=status.decode('utf-8').split("\n")[0]

      if stauts=="false":
        sysinfo=sysinfo+" "+cname+":Error\n"
        syserror="true"
      

    if syserror!="true":
      sysinfo="System Running!"     
    tb1.add_row([sname,sysinfo])

  if len(sysname)==0:
    tb1.add_row(["None","None"]) 

  #tb1.align="l"
  print(tb1)

def Show_Welcom():
  
  title = pyfiglet.figlet_format("ComityRT", font = "slant" )
  #print('\n================ ComityRT-Control =================\n')
  print(title)	
  print('Running System Status')

  Show_System_Status()

  print('\n===================================================\n')

def Choose_List():
  questions = [
  inquirer.List('action',
                message="Choose An Action",
                choices=['(1)Build system through configuration file', '(2)Edit system configuration file', '(3)System Start', '(4)System Stop' ,'(5)View ComityRT Log'],
            ),
  ]
  answers = inquirer.prompt(questions)
  if answers['action']=="(1)Build system through configuration file":
    Bulid_system()
  elif answers['action']=="(2)Edit system configuration file":
    Edit_config("","")
  elif answers['action']=="(3)System Start":
    os.system("python ComityRT_new.py")
  elif answers['action']=="(4)System Stop":
    Stop2Rm()
  elif answers['action']=="(5)View ComityRT Log":
    Choose_logs()

def Choose_logs():
  questions = [
  inquirer.List('action',
                message="Choose An Action",
                choices=['(1)Create logs', '(2)Deleted logs'],
            ),
  ]
  answers = inquirer.prompt(questions)
  logspath="./logs/"
  if answers['action']=="(1)Create logs":
    os.system("cat "+logspath+"CreateDocker")
  elif answers['action']=="(2)Deleted logs":
    os.system("cat "+logspath+"DeletedDocker")

def Choose_config(choices):
  questions = [
  inquirer.List('action',
                message="Choose An configuration file",
                choices=choices,
            ),
  ]
  answers = inquirer.prompt(questions)
  return answers['action']

def Choose_config_option(AList):
  questions = [
  inquirer.List('option',
                message="Choose An option",
                choices=AList,
            ),
  ]

  answers = inquirer.prompt(questions)
  return answers['option']

def Choose_config_Mkey():
  questions = [
  inquirer.List('action',
                message="Choose a parameter to modify",
                choices=Config_MainList,
            ),
  ]
  answers = inquirer.prompt(questions)
  return answers['action']

def Choose_config_Ckey():
  questions = [
  inquirer.List('action',
                message="Choose a parameter to modify",
                choices=Config_ConList,
            ),
  ]
  answers = inquirer.prompt(questions)
  return answers['action']

def Choose_edit_config(AList):
  global option
  global key

  option=Choose_config_option(AList)
  if option=="ComityRT":
    key=Choose_config_Mkey()
  elif option=="Back":
    Edit_config("",AList)
    return "Back"
  else:
    key=Choose_config_Ckey()
  
  if key=="Back":
    Edit_config("Backop",AList)
    return "Backop"
  else:
    return "edit"
  
  
def Edit_config(msg,AList):
  global option
  global key
  if msg=="Backop":
    msg=Choose_edit_config(AList)
  else:
    #config = configparser.ConfigParser()
    
    config_name=Load_config()
    if config_name==False:
      Edit_config("","")
    elif config_name=="Back":
      pass
    else:
      path="./config/System/"+str(config_name)
      config=ConfigObj(path)
      #config.read(path)
      #AList=config.sections()
      AList=config.keys()
      AList.append("Back")
      msg=Choose_edit_config(AList)
  if msg=="edit":
    print(option+" "+key)
  elif msg=="Back":
    print("Back")
  elif msg=="Backop":
    print("Backop")
  #print(AList)
  
def Bulid_system():
  config = configparser.ConfigParser() 
  config_name=Load_config()
  #config.read("System.ini")
  config.read("./config/System.ini")
  #config = ConfigObj('./System.ini')
  if config_name!="Back" and config_name!=False:
    sysname=config_name[:-4]
    if not config.has_section(sysname):
      config.add_section(sysname)
      #config['sysname']={}
      #config.write()
      config.write(open('./config/System.ini', "w"))
  
    for i in range(len(Criticality_Name)):
      Container_Use_Cores=""
      Container_Cores_Weights=Ciritical_container[i]['Container_Cores_Weights']
      Container_Memory_Limit=Ciritical_container[i]['Container_Memory_Limit']
      for j in range(len(Ciritical_container[i]['Container_Use_Cores'])):
        Container_Use_Cores=Container_Use_Cores+Ciritical_container[i]['Container_Use_Cores'][j]+","
      Container_Use_Cores=Container_Use_Cores[:-1]  ##['0','1','2']將LIST轉換成字串
      print(Container_Cores_Weights)
      CreateCMD(Criticality_Name[i],Container_Use_Cores,Container_Cores_Weights,Container_Memory_Limit)
      progress = ProgressBar().start()
      t1=threading.Thread(target=dosomework,args=(progress,))
      t1.start()
      time.sleep(2)
      print("\n")
      print(Criticality_Name[i]+" Complete the build!")

  os.system("python ComityRT_M.py")
  
def Stop2Rm():
  #config = configparser.ConfigParser()
  #sysconfig =configparser.ConfigParser()
  #sysconfig.read("System.ini") 
  sysconfig =ConfigObj('./config/System.ini')
  choices=[]
  #choices=sysconfig.sections()
  choices=sysconfig.keys()
  choices.append("Back")
  cfgN=Choose_config(choices)
  if cfgN=="Back":
      Choose_List()
      return "Back"
  else:
     ans=ContinueQue("Are you sure you want to stop the system?")
     path="./config/System/"+str(cfgN)+".ini"
     #config.read(path)
     config=ConfigObj(path)
     CTFilename=config['ComityRT']['Container_Filename']
     CTconfig=ConfigObj('./config/Container/'+CTFilename)
     #AList=config.sections()
     AList=CTconfig.keys()
     print(cfgN+" Start stop and delete....")
     for Lname in AList:

       status=subprocess.check_output(["sh","Stop2RmDocker.sh",Lname])
       status=status.decode('utf-8').split("\n")[0]
       if status=="true":
         print(Lname+" Successfully Deleted!")
      
     #sysconfig.remove_section(cfgN)
     del sysconfig[cfgN]
     sysconfig.write()
     #sysconfig.write(open('System.ini', "w"))
     #print(AList)
def dosomework(progress):
  for n in range(1, 80):
    progress.update(int(n/(80-1)*100))
    time.sleep(0.01)

def CreateCMD(Name,CPU_U,weights,Memory):
  #print(Name+" "+CPU_U)
  subprocess.run(["sh","CreateDocker.sh",CPU_U,Name,weights,Memory])

def Found_config():
  choices=[]
  path="./config/System/"
  if os.path.isdir(path):
    for fname in os.listdir(path):
      if fname.endswith(".ini"):
        choices.append(fname)
    return choices
  else:
    print("config folder not found! *.ini")
    return False

def Load_config():
  #config = configparser.ConfigParser()
  choices=[]
  #path="./config"
  #if os.path.isdir(path):
  #  for fname in os.listdir(path):
  #    if fname.endswith(".ini"):
  #      choices.append(fname)
  #else:
  #  print("config folder not found!")
  
  choices=Found_config()
  choices.append("Back")
  
  #questions = [
  #inquirer.List('action',
  #              message="Choose An configuration file",
  #              choices=choices,
  #          ),
  #]
  #answers = inquirer.prompt(questions)
  
  cfgN=Choose_config(choices)

  if cfgN=="Back":
      Choose_List()
      return "Back"
  else:
    #View_parameters(cfgN)
    ans = ContinueQue("Choose this configuration file?")
  
    if ans['continue']==True:
  
      configpath='./config/System/'+cfgN
      config=ConfigObj(configpath)
      CTFilename=config['ComityRT']['Container_Filename']
      CTconfig=ConfigObj('./config/Container/'+CTFilename)
      #config.read(configpath)
      global Criticality_Name
      global Sys_Use_Cores
      global Num_Criticality_Level
      global Sys_Preemption
      global Sched_Algorithm
      global Sys_Max_Num_Cores
      global TDF_Filename
      global Execution_Level_Mode
      global Task_Move
      global Container_Filename
      global Criticality_Level_Filename

      #Criticality_Name = config.get('ComityRT' , 'Criticality_Name').split()
      #Criticality_Name = config.sections()
      Criticality_Name = CTconfig.keys()
     
      #Sys_Use_Cores = config.get('ComityRT' , 'Sys_Use_Cores').split()

      Sys_Use_Cores = config['ComityRT']['Sys_Use_Cores']
    
      Num_Criticality_Level=config['ComityRT']['Num_Criticality_Level']

      Sys_Preemption=config['ComityRT']['Sys_Preemption']

      Sched_Algorithm =config['ComityRT']['Sched_Algorithm']

      Sys_Max_Num_Cores=config['ComityRT']['Sys_Max_Num_Cores']

      Execution_Level_Mode = config['ComityRT']['Execution_Level_Mode']

      Task_Move = config['ComityRT']['Task_Move']

      Container_Filename = config['ComityRT']['Container_Filename']
      
      Criticality_Level_Filename = config['ComityRT']['Criticality_Level_Filename']
      
      TDF_Filename = config['ComityRT']['TDF_Filename']
  
      
  
      fname=cfgN

      #讀取關鍵層級容器的參數
      Level=[]
      for i in Criticality_Name:
        #Level=config[str(i)]
        Ciritical_container.append(CTconfig[str(i)])
        #print(config[str(i)][str(j)])
  
      View_parameters(fname)

  
      #print(Ciritical_container['level1']['CPU_Limit'])
 
      return fname
   
    else:
      return ans['continue']

def ContinueQue(msg):
  questions = [
    inquirer.Confirm('continue',
                  message=msg),
  ]
  answers = inquirer.prompt(questions)
  return answers

def ComityRT_Status():
  print('he')  

def View_parameters(fname):
  os.system("clear")
  Temp=""
  tb1 = pt.PrettyTable()
  tb1.field_names = ["Parameter",fname]
  tb1.add_row(["Num_Criticality_Level",Num_Criticality_Level])
  tb1.add_row(["Sys_Preemption",Sys_Preemption])
  #tb1.add_row(["Criticality_Name",Criticality_Name])
  tb1.add_row(["Sched_Algorithm",Sched_Algorithm])
  tb1.add_row(["Sys_Max_Num_Cores",Sys_Max_Num_Cores])
  tb1.add_row(["Sys_Use_Cores",Sys_Use_Cores])
  tb1.add_row(["Execution_Level_Mode",Execution_Level_Mode])
  tb1.add_row(["Task_Move",Task_Move])
  tb1.add_row(["Container_Filename",Container_Filename])
  tb1.add_row(["Criticality_Level_Filename",Criticality_Level_Filename])
  tb1.add_row(["TDF_Filename",TDF_Filename])
  tb1.align="l"
  print(tb1) 

  Temp=copy.deepcopy(Config_ConList)
  Temp.pop()
  tb1 = pt.PrettyTable()
  
  tb1.field_names = ["Container",
                       "Container_Use_Cores",
                       "Container_Cores_Weights",
                       "Container_Memory_Limit",
                       "Container_Priority_Mode",
                     ]

  configpath='./config/System/'+fname
  config=ConfigObj(configpath)

  for i in range(len(Criticality_Name)):
    Temp2=[]
    Temp2.append(Criticality_Name[i])
    for j in Temp:
      Temp2.append(Ciritical_container[i][j])  
    tb1.add_row(Temp2)
    
          
    
  print(tb1) 
 
  #for i in range(len(Criticality_Name)):
  #  print('╔════════════╗')
  #  print('║{0:12}║'.format(str(Criticality_Name[i]).center(12)))
  #  print('╚════════════╝')
  #  for j in Temp:
  #    print('\n'+str(j)+' ='+Ciritical_container[i][j])
  #  print('\n')

  print('\n===============================================\n')

Show_Welcom()

Choose_List()
#View_parameters()

