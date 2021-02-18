import requests
import time

url = 'https://www.google.com.tw/'

start_time = time.time()

def send_req(url):

    t = time.time()
    print("Send a request at",t-start_time,"seconds.")

    res = requests.get(url)

    t = time.time()
    print("Receive a response at",t-start_time,"seconds.")

t = time.time()
for i in range(100):
    send_req(url)
print(t-start_time)

