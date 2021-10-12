import socket
import sys
import os
import json
from uuid import uuid4
from pprint import pprint 
import random
import math

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

DATABASE = {}


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 3125
s.bind(('0.0.0.0', port))
print ('Socket binded to port 3125')
s.listen(3)
print ('socket is listening')

approver_ids = [f"A{i}" for i in range(1, 21)]

while True:
  c, addr = s.accept()
  print ('Got connection from ', addr)
  var_re = c.recv(1024)

  req = json.loads(var_re)

  res = {"message": "Unknown Error"}
  try: 
    if req["mode"] == "upload":
      file_id = str(uuid4())
      DATABASE[file_id] = {
        "content": req["content"],
        "approvals": set(),
        "disapprovals": set(),
        "required_approvers": random.sample(approver_ids, 5),
        "has_majority": False
      } 
      res = {"message": "Success: File Added", "file_id": file_id}
    elif req["mode"] == "approval":
      if req["approve"]:
        if req['approver_id'] not in DATABASE[req["file_id"]]["required_approvers"]:
          res = {
            "message": f"{req['approver_id']} is not a required approver", 
            "required_approvers": DATABASE[req["file_id"]]["required_approvers"]
          }
        else:
          DATABASE[req["file_id"]]["approvals"].add(req["approver_id"])
          res = {"message": f"Success: File {req['file_id']} approved by {req['approver_id']}"}
          if len(DATABASE[req["file_id"]]["approvals"]) >= math.ceil(len(DATABASE[req["file_id"]]["required_approvers"]) / 2):
            DATABASE[req["file_id"]]["has_majority"] = True
      else:
        DATABASE[req["file_id"]]["disapprovals"].add(req["approver_id"])
        res = {"message": f"Success: File {req['file_id']} disapproved by {req['approver_id']}"}
    elif req["mode"] == "query":
      file_id = req["file_id"]
      res = {"message": "Success: Found file {file_id}", "file": DATABASE[file_id]} 
    else:
      res = {"message": f"INVALID MODE: {req['mode']}"}
  except Exception as e:
    res = {"message": f"ERROR: ({type(e)}) {e}"}

  print("Current Database State:")
  pprint(DATABASE)
  
  c.sendall(json.dumps(res, default=serialize_sets).encode())
  c.close()