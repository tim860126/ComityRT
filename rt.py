import os 
import subprocess
#try:
#  c=subprocess.check_output(['kill','-9','12345'])
#  c=c.decode('utf-8').split("\n")[0]
#except:
#  print("none")

os.system("kill -9 12345 > /dev/null 2>&1")
