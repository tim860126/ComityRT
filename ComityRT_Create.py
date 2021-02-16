import configparser
import inquirer
import os
import copy
#config = configparser.ConfigParser()


Config_MainList=["Cirityical_Name","CPU_Use","Ciritical_Level_Count","Pirority_algorithm","CPU_Limit","Workload_Name","Execution_Level_Mode","Priority_Mode","Scheduleability_analysis","Back"]

Config_ConList=["CPU_Limit","CPU_Use","CPU_Weights","Memory_Limit","Back"]

Cirityical_Name =""

CPU_Use =""

Ciritical_Level_Count =""

Pirority_algorithm =""

CPU_Limit=""

Workload_Name =""

Execution_Level_Mode =""

Priority_Mode =""

Scheduleability_analysis =""

Ciritical_container=[]

key=""
option=""

def Show_Welcom():
  print('\n================ ComityRT-Control =================\n')
	
  print('Docker Container Status')

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
    Edit_config()
  elif answers['action']=="(3)System Start":
    print("3")
  elif answers['action']=="(4)System Stop":
    print("4")
  elif answers['action']=="(5)View ComityRT Log":
    print("5")

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

def Choose_edit_config(config,AList):
  global option
  global key

  option=Choose_config_option(AList)
  if option=="ComityRT":
    key=Choose_config_Mkey()
  #elif option=="Back":
  #  Edit_config()
  else:
    key=Choose_config_Ckey()

  if key=="Back":
    Choose_edit_config(config,AList)
  
  
def Edit_config():
  config = configparser.ConfigParser()
  config_name=Load_config()
  print(config_name)
  if config_name==False:
    Edit_config()
  else:
    path="./config/"+str(config_name)
    config.read(path)
    global option
    global key
    AList=config.sections()
    AList.append("Back")
    Choose_edit_config(config,AList)
    print(option+" "+key)
  
def Bulid_system():
  config_name=Load_config()

def Load_config():
  config = configparser.ConfigParser()
  choices=[]
  path="./config"
  if os.path.isdir(path):
    for fname in os.listdir(path):
      if fname.endswith(".ini"):
        choices.append(fname)
  else:
    print("config folder not found!")
  #choices.append("Back") 
  questions = [
  inquirer.List('action',
                message="Choose An configuration file",
                choices=choices,
            ),
  ]
  answers = inquirer.prompt(questions)
  
  cfgN=answers['action'] 

  ans = ContinueQue()

  if ans['continue']==True:
  #if answers['action']=="Back":
  #  Choose_List()
  #  pass  
  
    configpath='./config/'+cfgN
  
    config.read(configpath)
  
    global Cirityical_Name
    global CPU_Use
    global Ciritical_Level_Count
    global Pirority_algorithm
    global CPU_Limit
    global Workload_Name
    global Execution_Level_Mode
    global Priority_Mode
    global Scheduleability_analysis

    Cirityical_Name = config.get('ComityRT' , 'Cirityical_Name').split()

    CPU_Use = config.get('ComityRT' , 'CPU_Use').split()

    Ciritical_Level_Count=config['ComityRT']['Ciritical_Level_Count']

    Pirority_algorithm =config['ComityRT']['Pirority_algorithm']

    CPU_Limit=config['ComityRT']['CPU_Limit']

    Workload_Name = config['ComityRT']['Workload_Name']

    Execution_Level_Mode = config['ComityRT']['Execution_Level_Mode']

    Priority_Mode = config['ComityRT']['Priority_Mode']

    Scheduleability_analysis = config['ComityRT']['Scheduleability_analysis']
  
    fname=answers['action']

    #讀取關鍵層級容器的參數
    Level=[]
    for i in Cirityical_Name:
      #Level=config[str(i)]
      Ciritical_container.append(config[str(i)])
      #print(config[str(i)][str(j)])
  
    View_parameters(fname)

  
    #print(Ciritical_container['level1']['CPU_Limit'])
 
    return fname
   
  else:
    return ans['continue']

def ContinueQue():
  questions = [
    inquirer.Confirm('continue',
                  message="Choose this configuration file?"),
  ]
  answers = inquirer.prompt(questions)
  return answers

def ComityRT_Status():
  print('he')  

def View_parameters(fname):
  Temp=""
  print('\n================ '+fname+' =================\n')

  print('Ciritical_Level_Count =',Ciritical_Level_Count)
  print('\nCirityical_Name =',Cirityical_Name)
  print('\nPirority_algorithm =',Pirority_algorithm)
  print('\nCPU_Limit =',CPU_Limit)
  print('\nCPU_Use =',CPU_Use);
  print('\nWorkload_Name =',Workload_Name)
  print('\nExecution_Level_Mode =',Execution_Level_Mode)
  print('\nPriority_Mode =',Priority_Mode)
  print('\nScheduleability_analysis =',Scheduleability_analysis)
  Temp=copy.deepcopy(Config_ConList)
  Temp.pop()
  for i in range(len(Cirityical_Name)):
    print('╔════════════╗')
    print('║{0:12}║'.format(str(Cirityical_Name[i])))
    print('╚════════════╝')
    for j in Temp:
      print('\n'+str(j)+' ='+Ciritical_container[i][j])
    print('\n')

  print('\n===============================================\n')

Show_Welcom()

Choose_List()
#View_parameters()

