import  socket
import json 
import argparse 
import sys 


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

s = socket.socket()
port = 3125
s.connect(('localhost', port))
s.sendall(z.encode())    
s.close()


