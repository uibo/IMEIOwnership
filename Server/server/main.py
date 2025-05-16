import json
import os

from fastapi import FastAPI, HTTPException
from web3 import Web3
from dotenv import load_dotenv

from model import RegisterIMEIRequest, GetIMEIRequest
from function import registerIMEI, getIMEIOwner

app = FastAPI()

load_dotenv("config/.env")
with open("config/IMEIOwnership.abi.json") as f:
    abi = json.load(f)

CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SENDER = os.getenv("ACCOUNT_ADDRESS")

w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))  # RPC 주소 확인
contract = w3.eth.contract(CONTRACT_ADDRESS, abi=abi)

@app.get("/")
def main_page():
    return (CONTRACT_ADDRESS, PRIVATE_KEY, SENDER)

@app.post("/register")
def register_imei(req: RegisterIMEIRequest):
    try:
        tx_hash = registerIMEI(w3, contract, SENDER, PRIVATE_KEY, req.to, req.imei_hash, req.nonce, Web3.to_bytes(hexstr=req.signature))
        return {"tx_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# IMEI 소유자 조회
@app.post("/get")
def get_imei_owner(req: GetIMEIRequest):
    try:
        return getIMEIOwner(contract, req.imei_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
