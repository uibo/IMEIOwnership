from fastapi import FastAPI
from web3 import Web3

from server.model import RegisterIMEIRequest
from server.function import registerIMEI
from server.config.config import w3, contract, SERVER_ADDRESS, SERVER_PRIVATE_KEY

app = FastAPI()

@app.get("/")
def main_page():
    return "Welcome to IMEIOwnership"

@app.post("/register")
def register_imei(req: RegisterIMEIRequest):
    tx_hash = registerIMEI(w3, contract, SERVER_ADDRESS, SERVER_PRIVATE_KEY, req.imei_hash, req.to, req.nonce, Web3.to_bytes(hexstr=req.signature))
    return tx_hash