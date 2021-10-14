"""
Simple counting app.  It only accepts values sent to it in correct order.  The
state maintains the current count. For example, if starting at state 0, sending:
-> 0x01 = OK!
-> 0x03 = Will fail! (expects 2)

To run it:
- make a clean new directory for tendermint
- start this server: python counter.py
- start tendermint: tendermint --home "YOUR DIR HERE" node
- The send transactions to the app:


curl http://localhost:26657/broadcast_tx_commit?tx=0x01
curl http://localhost:26657/broadcast_tx_commit?tx=0x02
...

To see the latest count:
curl http://localhost:26657/abci_query

The way the app state is structured, you can also see the current state value
in the tendermint console output (see app_hash).
"""
import struct
from tendermint.abci.types_pb2 import (  
    ResponseInfo,
    ResponseInitChain,
    ResponseCheckTx,
    ResponseDeliverTx,
    ResponseQuery,
    ResponseCommit,
)

from abci.server import ABCIServer
from abci.application import BaseApplication, OkCode, ErrorCode 

import json 
import pathlib 
from hashlib import sha256

thisdir = pathlib.Path(__file__).resolve().parent

def encode_number(value):
    return struct.pack(">I", value)


def decode_number(raw):
    return int.from_bytes(raw, byteorder="big")


class FileApprover(BaseApplication):
    def info(self, req) -> ResponseInfo:
        """Returns info on applciation"""
        r = ResponseInfo()
        r.version = req.version
        r.last_block_height = 0
        r.last_block_app_hash = b""
        return r

    def init_chain(self, req) -> ResponseInitChain:
        """Initializes Application"""
        self.data = {}
        return ResponseInitChain()

    def check_tx(self, tx: bytes) -> ResponseCheckTx:
        """Validate transactions before entry into the mempool

        Optional method for performing basic checks on a transaction.
        This method is optional, since it's not actually used in consensus.
        This method should only perform basic checks like formatting, signature, etc. 
        These checks should also be re-performed in deliver_tx.
        This method should not modify application state.
        """
        return ResponseCheckTx(code=OkCode)

    def deliver_tx(self, tx: bytes) -> ResponseDeliverTx:
        """Validate transactions to be committed to blockchain

        Perform all checks, verify transaction is valid, and modify 
        applciation state.
        """
        req = json.loads(tx)

        res = {"message": "Unknown Error"}
        try: 
            if req["mode"] == "upload":
                file_id = str(uuid4())
                self.data[file_id] = {
                    "content": req["content"],
                    "approvals": set(),
                    "disapprovals": set(),
                    "required_approvers": random.sample(approver_ids, 5),
                    "has_majority": False
                } 
                return ResponseDeliverTx(
                    code=OkCode,
                    log="Success: File Added"
                )
            elif req["mode"] == "approval":
                if req["approve"]:
                    if req['approver_id'] not in self.data[req["file_id"]]["required_approvers"]:
                        return ResponseDeliverTx(
                            code=ErrorCode,
                            log=f"{req['approver_id']} is not a required approver"
                        )
                    else:
                        self.data[req["file_id"]]["approvals"].add(req["approver_id"])
                        return ResponseDeliverTx(
                            code=OkCode,
                            log=f"Success: File {req['file_id']} approved by {req['approver_id']}"
                        )

                    # Smart Contract Behavior
                    if len(self.data[req["file_id"]]["approvals"]) >= math.ceil(len(self.data[req["file_id"]]["required_approvers"]) / 2):
                        self.data[req["file_id"]]["has_majority"] = True
                else:
                    if req['approver_id'] not in self.data[req["file_id"]]["required_approvers"]:
                        return ResponseDeliverTx(
                            code=ErrorCode,
                            log=f"{req['approver_id']} is not a required approver"
                        )
                    else:
                        self.data[req["file_id"]]["disapprovals"].add(req["approver_id"])
                        return ResponseDeliverTx(
                            code=OkCode,
                            log=f"Success: File {req['file_id']} disapproved by {req['approver_id']}"
                        )
            else:
                ResponseDeliverTx(
                    code=ErrorCode,
                    log=f"INVALID MODE: {req['mode']}"
                )
        except Exception as e:
            ResponseDeliverTx(
                code=ErrorCode,
                log=f"ERROR: ({type(e)}) {e}"
            )


    def query(self, req) -> ResponseQuery:
        """Return piece of application state 
        
        In this implementation, the query returns the current value for a 
        specified key or N/A if the key does not exist
        """
        key: str = req.data.decode("utf-8")
        return ResponseQuery(
            code=OkCode, value=self.data.get(key, {"value": "N/A"})["value"].encode("utf-8")
        )

    def commit(self) -> ResponseCommit:
        """Persist the application state"""
        json_str = json.dumps(self.data, indent=4)
        thisdir.joinpath("state.json").write_text(json_str)
        return ResponseCommit(data=sha256(json_str.encode("utf-8")).digest())


def main():
    app = ABCIServer(app=FileApprover())
    app.run()


if __name__ == "__main__":
    main()