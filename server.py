import socket
import sys
import os
import json
from uuid import uuid4
from pprint import pprint 
import random

DATABASE = {}



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 3125
s.bind(('0.0.0.0', port))
print ('Socket binded to port 3125')
s.listen(3)
print ('socket is listening')

while True:
  c, addr = s.accept()
  print ('Got connection from ', addr)
  var_re = c.recv(1024)

  req = json.loads(var_re)

  try: 
    if req["mode"] == "upload":
      file_id = str(uuid4())
      DATABASE[file_id] = {
        "content": req["content"],
        "approvals": set(),
        "disapprovals": set()
      } 
      print(f"Saved new file with ID: {file_id}")
      approver_id = ["a1","a2","a3","a4","a5","a6","a7","a8","a9","a10"]
      sample_list = random.sample(approver_id, 5)
      for x in sample_list:
        print("Hello, %s You are chosen to give your review!! " %x)
      
      

    elif req["mode"] == "approval":
      if req["approve"]:
        DATABASE[req["file_id"]]["approvals"].add(req["approver_id"])
        print(f"{req['file_id']} approved by {req['approver_id']}")
        #print(DATABASE[1]['approvals'])
      else:
        DATABASE[req["file_id"]]["disapprovals"].add(req["approver_id"])
        print(f"{req['file_id']} disapproved by {req['approver_id']}")
    else:
      print(f"INVALID MODE: {req['mode']}")
  except Exception as e:
    print(f"ERROR: ({type(e)}) {e}")

  print("Current Database State:")
  pprint(DATABASE)
  
  ap = len(DATABASE[file_id]['approvals'])
  dp = len(DATABASE[file_id]['disapprovals'])
  m = ap + dp
  if(m == 5):
    if ap>dp:
      print("Product Approved~Your reviews are accepted,kudos with File-ID:", file_id, DATABASE[file_id]['approvals'])
    else:
      print("Product Rejected~Your reviews are accepted,kudos with File-ID:", file_id, DATABASE[file_id]['disapprovals'])
    
  c.close()