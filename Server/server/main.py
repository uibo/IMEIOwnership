from fastapi import FastAPI
from web3 import Web3

from server.model import RegisterIMEIRequest, GetIMEIOwnerRequest
from server.config.config import w3, contract, server_account
from server.function import registerIMEI, getIMEIOwner

app = FastAPI()

@app.get("/")
def main_page():
    return "Welcome to IMEIOwnership"

@app.post("/register")
def register_imei(req: RegisterIMEIRequest):
    imei_hash = Web3.to_bytes(hexstr=req.imei_hash)
    to = Web3.to_bytes(hexstr=req.to)
    nonce = int(req.nonce)
    signature = Web3.to_bytes(hexstr=req.signature)
    req.imei_hash
    tx_hash = registerIMEI(w3, contract, server_account.address, server_account.key, imei_hash, to, nonce, signature)
    return tx_hash

@app.post("/get")
def get_imei_owner(req: GetIMEIOwnerRequest):
    return getIMEIOwner(w3, contract, req.imei_hash)