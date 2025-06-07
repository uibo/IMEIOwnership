from fastapi import FastAPI
from web3 import Web3

from server.model import RegisterIMEIRequest, GetIMEIOwnerRequest, TransferIMEIRequest, TradeIMEIRequest, ConfirmTradeRequest
from server.config.config import w3, contract, server_account
from server.function import (
    registerIMEI,
    getIMEIOwner,
    transferIMEI,
    tradeIMEI,
    confirmTrade
)

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


@app.post("/transfer")
def transfer_imei(req: TransferIMEIRequest):
    imei_hash_bytes = Web3.to_bytes(hexstr=req.imei_hash)
    from_addr = Web3.to_checksum_address(req.from_addr)
    to_addr = Web3.to_checksum_address(req.to_addr)
    nonce_int = int(req.nonce)
    signature_bytes = Web3.to_bytes(hexstr=req.signature)

    tx_hash = transferIMEI(
        w3=w3,
        contract=contract,
        sender=server_account.address,
        private_key=server_account.key,
        imei_hash=imei_hash_bytes,
        from_addr=from_addr,
        to_addr=to_addr,
        nonce=nonce_int,
        signature=signature_bytes
    )
    return {"tx_hash": tx_hash}


@app.post("/trade")
def trade_imei(req: TradeIMEIRequest):
    imei_hash_bytes = Web3.to_bytes(hexstr=req.imei_hash)
    seller_addr = Web3.to_checksum_address(req.seller)
    buyer_addr = Web3.to_checksum_address(req.buyer)
    price_int = int(req.price)

    seller_nonce_int = int(req.seller_nonce)
    seller_sig_bytes = Web3.to_bytes(hexstr=req.seller_signature)

    buyer_nonce_int = int(req.buyer_nonce)
    buyer_sig_bytes = Web3.to_bytes(hexstr=req.buyer_signature)
    buyer_v_int = int(req.buyer_v)
    buyer_r_bytes = Web3.to_bytes(hexstr=req.buyer_r)
    buyer_s_bytes = Web3.to_bytes(hexstr=req.buyer_s)
    buyer_deadline_int = int(req.buyer_deadline)

    tx_hash = tradeIMEI(
        w3=w3,
        contract=contract,
        sender=server_account.address,
        private_key=server_account.key,
        imei_hash=imei_hash_bytes,
        seller=seller_addr,
        buyer=buyer_addr,
        price=price_int,
        seller_nonce=seller_nonce_int,
        seller_signature=seller_sig_bytes,
        buyer_nonce=buyer_nonce_int,
        buyer_signature=buyer_sig_bytes,
        buyer_v=buyer_v_int,
        buyer_r=buyer_r_bytes,
        buyer_s=buyer_s_bytes,
        buyer_deadline=buyer_deadline_int
    )
    return {"tx_hash": tx_hash}


@app.post("/confirm")
def confirm_trade(req: ConfirmTradeRequest):
    imei_hash_bytes = Web3.to_bytes(hexstr=req.imei_hash)
    nonce_int = int(req.nonce)
    signature_bytes = Web3.to_bytes(hexstr=req.signature)

    tx_hash = confirmTrade(
        w3=w3,
        contract=contract,
        sender=server_account.address,
        private_key=server_account.key,
        imei_hash=imei_hash_bytes,
        nonce=nonce_int,
        signature=signature_bytes
    )
    return {"tx_hash": tx_hash}