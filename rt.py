import os 

print(os.system("pidof PrintXX"))
os.system("kill $(pidof PrintXX)")
