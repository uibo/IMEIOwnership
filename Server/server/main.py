from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tinydb import TinyDB, Query
from web3 import Web3

from server.model import RegisterIMEIRequest, GetIMEIOwnerRequest, TransferIMEIRequest, TradeIMEIRequest, ConfirmTradeRequest, MintTokenRequest, TradeInfoRequest, BuyerQuery, BuyerInfoMatch
from server.config.config import w3, contract, server_account, contract_currency
from server.function import registerIMEI, getIMEIOwner, transferIMEI, tradeIMEI, confirmTrade, mint


app = FastAPI()
db = TinyDB("trades.json")
trade_table = db.table("trades")
trade_table.truncate()
query = Query()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def main_page():
    return "Welcome to IMEIOwnership"

@app.post("/register")
def register_imei(req: RegisterIMEIRequest):
    imei_hash = Web3.to_bytes(hexstr=req.imei_hash)
    to = Web3.to_bytes(hexstr=req.to)
    nonce = int(req.nonce)
    signature = Web3.to_bytes(hexstr=req.signature)
    tx_hash = registerIMEI(w3, contract, server_account.address, server_account.key, imei_hash, to, nonce, signature)
    return tx_hash

@app.post("/get")
def get_imei_owner(req: GetIMEIOwnerRequest):
    imei_hash = Web3.to_bytes(hexstr=req.imei_hash)
    return getIMEIOwner(w3, contract, imei_hash)


@app.post("/tradeinfo")
def store_tradeInfo(req: TradeInfoRequest):
    imei = req.tradeInfo.imei_hash
    if trade_table.contains(query.tradeInfo["imei_hash"] == imei):
        raise HTTPException(status_code=400, detail="Trade already exists with this IMEI hash.")
    trade_table.insert(req.model_dump())
    return {"status": "stored"}

@app.post("/tradeinfo/list")
def get_trades_by_buyer(req: BuyerQuery):
    buyer = req.buyer.lower()

    filtered_trades = trade_table.search(query.tradeInfo["buyer"] == buyer)
    if not filtered_trades:
        return {"trades": [], "message": "No trades found for this buyer."}
    return {"trades": filtered_trades}

@app.post("/buyerinfo")
def match_buyerInfo(req: BuyerInfoMatch):
    imei = req.imei_hash
    results = trade_table.search(query.tradeInfo["imei_hash"] == imei)
    if results:
        trade_entry = results[0]  # 첫 번째 매치

        tradeInfo = trade_entry.get("tradeInfo", {})
        tradeInfo = {
            "imeiHash": Web3.to_bytes(hexstr=tradeInfo["imei_hash"]),
            "seller": Web3.to_checksum_address(tradeInfo["seller"]),
            "buyer": Web3.to_checksum_address(tradeInfo["buyer"]),
            "price": int(tradeInfo["price"])
        }
        sellerInfo = trade_entry.get("sellerInfo", {})
        sellerInfo = {
            "nonce": int(sellerInfo["nonce"]),
            "signature": Web3.to_bytes(hexstr=sellerInfo["signature"])
        }
        buyerInfo = req.buyerInfo.model_dump()
        buyerInfo = {
            "nonce": int(buyerInfo["nonce"]),
            "signature": Web3.to_bytes(hexstr=buyerInfo["signature"]),
            "v": int(buyerInfo["v"]),
            "r": Web3.to_bytes(hexstr=buyerInfo["r"]),
            "s": Web3.to_bytes(hexstr=buyerInfo["s"]),
            "deadline": int(buyerInfo["deadline"])
        }

        tx_hash = tradeIMEI(w3, contract, server_account.address, server_account.key, tradeInfo, sellerInfo, buyerInfo)
        return {"status": "성공", "tx_hash": tx_hash}
    return {"status": "실패", "message": "일치하는 거래 정보가 없습니다."}

@app.post("/transfer")
def transfer_imei(req: TransferIMEIRequest):
    imei_hash = Web3.to_bytes(hexstr=req.imei_hash)
    from_addr = Web3.to_bytes(hexstr=req.from_addr)
    to_addr = Web3.to_bytes(hexstr=req.to_addr)
    nonce_int = int(req.nonce)
    signature_bytes = Web3.to_bytes(hexstr=req.signature)
    tx_hash = transferIMEI(
        w3=w3,
        contract=contract,
        sender=server_account.address,
        private_key=server_account.key,
        imei_hash=imei_hash,
        from_addr=from_addr,
        to_addr=to_addr,
        nonce=nonce_int,
        signature=signature_bytes
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

@app.post("/mint")
def mint_token(req: MintTokenRequest):
    to = Web3.to_bytes(hexstr=req.to)
    amount = int(req.amount)
    tx_hash = mint(w3, contract_currency, server_account.address, server_account.key, to, amount)
    return tx_hash