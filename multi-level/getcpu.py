import psutil
import pandas as pd
df = pd.DataFrame()
for i in range(28):
  cpuarray=psutil.cpu_percent(interval=1,percpu=True)
  ps=pd.DataFrame([{'time':str(i),'core1':cpuarray[0],'core2':cpuarray[1],'core3':cpuarray[2],'core4':cpuarray[3]}],columns=['time','core1','core2','core3','core4'])
  df = df.append(ps,ignore_index=True)
df.to_excel('index2.xlsx',index = False)
  

