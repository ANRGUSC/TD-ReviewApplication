import socket
import json 
import argparse 
import sys 
   
import requests
from base64 import b64decode, b64encode
from datetime import datetime 

def query(file_id: str) -> None:
    res = requests.get(f'http://localhost:26657/abci_query?data="{file_id}"')
    if res.status_code == 200:
        res_json = res.json()["result"]
        file_info = json.loads(b64decode(res_json["response"]["value"].encode()).decode())
        print(file_info)
    else:
        print(res.status_code)
        print(res.text)

def send_tx(tx) -> None:
    tx_serialized = b64encode(json.dumps(tx).encode()).decode()
    res = requests.get(f'http://localhost:26657/broadcast_tx_commit?tx="{tx_serialized}"')
    print(res.status_code)
    print(res.text)


def get_parser() -> argparse.ArgumentParser:
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
    query_parser.add_argument("--file-id", default="", help="file ID to query")

    return parser 

def main():
    parser = get_parser()
    args = parser.parse_args()
    if not hasattr(args, "mode"):
        sys.argv.append("--help")
        parser.parse_args()

    if args.mode == "upload":
        send_tx({"mode": "upload", "content": args.content})
    elif args.mode == "approve":
        send_tx({"mode": "approval", "approver_id": args.id, "file_id": args.file_id, "approve": True})
    elif args.mode == "disapprove":
        send_tx({"mode": "approval", "approver_id": args.id, "file_id": args.file_id, "approve": False})
    elif args.mode == "query":
        query(args.file_id)


if __name__ == "__main__":
    main()


