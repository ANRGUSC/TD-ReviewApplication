import socket
import json 
import argparse 
import sys 
   
import requests
from base64 import b64decode, b64encode
from datetime import datetime 

def get_value(args: argparse.Namespace) -> None:
    res = requests.get(f'http://localhost:26657/abci_query?data="{args.key}"')
    if res.status_code == 200:
        res_json = res.json()["result"]
        value = b64decode(res_json["response"]["value"].encode("utf-8")).decode("utf-8")
        print(value)
    else:
        print(res.status_code)
        print(res.text)

def send_tx(tx: Dict) -> None:
    tx_serialized = b64encode(json.dumps(tx).encode()).decode()
    res = requests.get(f'http://localhost:26657/broadcast_tx_commit?tx="{tx_serialized}"')
    print(res.status_code)
    print(res.text)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

upload_parser = subparsers.add_parser("upload")
upload_parser.set_defaults(mode="upload")
upload_parser.add_argument("content", help="File content if mode=upload, otherwise approver ID")

approval_parser = subparsers.add_parser("approve")
approval_parser.set_defaults(mode="approve")
approval_parser.add_argument("--id", help="approver ID")
approval_parser.add_argument("file_id", help="file ID to approve")

disapproval_parser = subparsers.add_parser("disapprove")
disapproval_parser.set_defaults(mode="disapprove")
disapproval_parser.add_argument("--id", help="disapprover ID")
disapproval_parser.add_argument("file_id", help="file ID to disapprove")

query_parser = subparsers.add_parser("query")
query_parser.set_defaults(mode="query")
query_parser.add_argument("file_id", help="file ID to query")

args = parser.parse_args()

if not hasattr(args, "mode"):
    sys.argv.append("--help")
    parser.parse_args()

    

if args.mode == "upload":
    z = json.dumps({"mode": "upload", "content": args.content})
    print(z)
elif args.mode == "approve":
    z = json.dumps({"mode": "approval", "approver_id": args.id, "file_id": args.file_id, "approve": True})
elif args.mode == "disapprove":
    z = json.dumps({"mode": "approval", "approver_id": args.id, "file_id": args.file_id, "approve": False})
elif args.mode == "query":
    z = json.dumps({"mode": "query", "file_id": args.file_id})

s = socket.socket()
port = 3125
s.connect(('localhost', port))
s.sendall(z.encode())    

res = json.loads(s.recv(1024))
print(res)
s.close()


