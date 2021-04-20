import subprocess
c=subprocess.check_output(['pidof','work4'])
c=c.decode('utf-8').split("\n")[0]
print(c)
