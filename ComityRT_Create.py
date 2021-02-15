import configparser
import inquirer
import os
config = configparser.ConfigParser()
config.read('ComityRT.ini')

Cirityical_Name = config.get('ComityRT' , 'Cirityical_Name').split()

CPU_Use = config.get('ComityRT' , 'CPU_Use').split()

Ciritical_Level_Count=config['ComityRT']['Ciritical_Level_Count']

Pirority_algorithm =config['ComityRT']['Pirority_algorithm']

CPU_Limit=config['ComityRT']['CPU_Limit']

Workload_Name = config['ComityRT']['Workload_Name']

Execution_Level_Mode = config['ComityRT']['Execution_Level_Mode']

Priority_Mode = config['ComityRT']['Priority_Mode']

Scheduleability_analysis = config['ComityRT']['Scheduleability_analysis']
def Show_Welcom():
  print('\n================ ComityRT-Control =================\n')
	
  print('Docker Container Status')

  print('\n===================================================\n')

def Choose_List():
  questions = [
  inquirer.List('action',
                message="Choose An Action",
                choices=['(1)Build system through configuration file', '(2)Edit system configuration file', '(3)System running', '(4)System Stoping'],
            ),
  ]
  answers = inquirer.prompt(questions)
  if answers['action']=="(1)Build system through configuration file":
    Bulid_system()
  elif answers['action']=="(2)Edit system configuration file":
    print("2")
  elif answers['action']=="(3)System running":
    print("3")
  elif answers['action']=="(4)System Stoping":
    print("4")

def Bulid_system():
  choices=[]
  path="./config"
  if os.path.isdir(path):
    for fname in os.listdir(path):
      if fname.endswith(".ini"):
        choices.append(fname)
  else:
    print("config folder not found!")
  
  questions = [
  inquirer.List('action',
                message="Choose An configuration file",
                choices=choices,
            ),
  ]
  answers = inquirer.prompt(questions)
  

def ComityRT_Status():
  print('he')  

def View_parameters():
  print('Ciritical_Level_Count =',Ciritical_Level_Count)
  print('\nCirityical_Name =',Cirityical_Name)
  print('\nPirority_algorithm =',Pirority_algorithm)
  print('\nCPU_Limit =',CPU_Limit)
  print('\nCPU_Use =',CPU_Use);
  print('\nWorkload_Name =',Workload_Name)
  print('\nExecution_Level_Mode =',Execution_Level_Mode)
  print('\nPriority_Mode =',Priority_Mode)
  print('\nScheduleability_analysis =',Scheduleability_analysis)

Show_Welcom()

Choose_List()
#View_parameters()

