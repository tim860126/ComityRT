import os 
import subprocess
#try:
#  c=subprocess.check_output(['kill','-9','12345'])
#  c=c.decode('utf-8').split("\n")[0]
#except:
#  print("none")

c=subprocess.check_output(['./StopWorkPID.sh','12345'])
msg=c.decode('utf-8').split("\n")[0]
print(msg)

