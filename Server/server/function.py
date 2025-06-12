from web3 import Web3
from web3.contract import Contract

def registerIMEI(w3: Web3, contract: Contract, sender: str, private_key: str, imei_hash: bytes, to: bytes, nonce: int, signature: bytes) -> str:
    tx = contract.functions.registerIMEI(imei_hash, to, nonce, signature)
    gas_estimate = tx.estimate_gas({'from': sender})
    tx_dict = tx.build_transaction({
        'from': sender,
        'nonce': w3.eth.get_transaction_count(sender),
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    })
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return w3.to_hex(tx_hash)

def getIMEIOwner(w3: Web3, contract: Contract, imei_hash: bytes) -> str:
    imei_owner = contract.functions.imeiHashToOwner(imei_hash).call()
    return imei_owner

def transferIMEI(w3: Web3, contract: Contract, sender: str, private_key: str, imei_hash: bytes, from_addr: bytes, to_addr: bytes, nonce: int, signature: bytes
) -> str:
    """
    Solidity: transferIMEI(bytes32 imeiHash, address from, address to, uint nonce, bytes calldata signature)
    """
    tx = contract.functions.transferIMEI(imei_hash, from_addr, to_addr, nonce, signature)
    gas_estimate = tx.estimate_gas({'from': sender})
    tx_dict = tx.build_transaction({
        'from': sender,
        'nonce': w3.eth.get_transaction_count(sender),
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    })
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return w3.to_hex(tx_hash)

def tradeIMEI(w3: Web3, contract: Contract, sender: str, private_key: str,
    tradeInfo: dict, sellerInfo: dict, buyerInfo: dict
) -> str:
    tx = contract.functions.tradeIMEI(tradeInfo, sellerInfo, buyerInfo)
    gas_estimate = tx.estimate_gas({'from': sender})
    tx_dict = tx.build_transaction({
        'from': sender,
        'nonce': w3.eth.get_transaction_count(sender),
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    })
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)

def confirmTrade(w3: Web3, contract: Contract, sender: str, private_key: str,
    imei_hash: bytes, nonce: int, signature: bytes
) -> str:
    """
    Solidity: confirmTrade(bytes32 imeiHash, uint nonce, bytes calldata signature)
    """
    tx = contract.functions.confirmTrade(imei_hash, nonce, signature)
    gas_estimate = tx.estimate_gas({'from': sender})
    tx_dict = tx.build_transaction({
        'from': sender,
        'nonce': w3.eth.get_transaction_count(sender),
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    })
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.to_hex(tx_hash)

def mint(w3: Web3, contract: Contract, sender: str, private_key: str, to: bytes, amount: int):
    tx = contract.functions.mint(to, amount)
    gas_estimate = tx.estimate_gas({'from': sender})
    tx_dict = tx.build_transaction({
        'from': sender,
        'nonce': w3.eth.get_transaction_count(sender),
        'gas': gas_estimate,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    })
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return w3.to_hex(tx_hash)
    