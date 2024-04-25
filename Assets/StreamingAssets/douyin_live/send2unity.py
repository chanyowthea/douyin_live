import json
import threading
import time
import requests
from config import SEND_URL

_pending_messages = []

def add_pending_msg(msg):
    _pending_messages.append(msg)

def clear_pending_msg():
    _pending_messages.clear()

def send_msg2unity():
    if not _pending_messages:
        return
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        'Content-Type': 'application/json'
    }
    print("====================send_msg2unity ",len(_pending_messages))
    requests.request("POST", SEND_URL, headers=headers, data={"msgs":_pending_messages})
    clear_pending_msg()

def _http_send():
    while True:
        time.sleep(1)
        try:
            send_msg2unity()
        except Exception as e:
            print(f"=====================_http_send 线程错误！send_msg2unity")

def start_send_unity():
    print("====================start_send_unity")
    t = threading.Thread(target=_http_send)
    t.start()
