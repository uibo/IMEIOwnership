from eth_account import Account
from web3 import Web3

def registerIMEI(w3: Web3, contract, sender, private_key, to, imei_hash, nonce, signature):
    tx = contract.functions.registerIMEI(to, imei_hash, nonce, signature).build_transaction({
        "from": sender,
        "nonce": w3.eth.get_transaction_count(sender),
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })
    signed_tx = Account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def getIMEIOwner(contract, imei_hash):
    return contract.functions.getIMEIOwner(imei_hash).call()

def transferIMEI(w3, contract, sender, private_key, imei_hash, from_addr, to_addr, nonce, signature):
    tx = contract.functions.transferIMEI(imei_hash, from_addr, to_addr, nonce, signature).build_transaction({
        "from": sender,
        "nonce": w3.eth.get_transaction_count(sender),
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def tradeIMEI(w3, contract, sender, private_key, trade_info, seller_info, buyer_info):
    tx = contract.functions.tradeIMEI(trade_info, seller_info, buyer_info).build_transaction({
        "from": sender,
        "nonce": w3.eth.get_transaction_count(sender),
        "gas": 400000,
        "gasPrice": w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def confirmIMEI(w3, contract, sender, private_key, imei_hash, signature):
    tx = contract.functions.confirmTrade(imei_hash, signature).build_transaction({
        "from": sender,
        "nonce": w3.eth.get_transaction_count(sender),
        "gas": 150000,
        "gasPrice": w3.eth.gas_price
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()
