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

def transferIMEI(w3: Web3,contract: Contract,sender: str,private_key: str,imei_hash: bytes,from_addr: str,to_addr: str,nonce: int,signature: bytes
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


def tradeIMEI(w3: Web3,contract: Contract,
    sender: str,
    private_key: str,
    imei_hash: bytes,
    seller: str,
    buyer: str,
    price: int,
    seller_nonce: int,
    seller_signature: bytes,
    buyer_nonce: int,
    buyer_signature: bytes,
    buyer_v: int,
    buyer_r: bytes,
    buyer_s: bytes,
    buyer_deadline: int
) -> str:
    """
    Solidity: 
      struct TradeInfo { bytes32 imeiHash; address seller; address buyer; uint price; }
      struct SellerInfo { uint nonce; bytes signature; }
      struct BuyerInfo { uint nonce; bytes signature; uint8 v; bytes32 r; bytes32 s; uint256 deadline; }
      function tradeIMEI(
          TradeInfo calldata tradeInfo, 
          SellerInfo calldata sellerInfo,
          BuyerInfo calldata buyerInfo
      ) external
    """
    # 1) TradeInfo tuple 순서: (imeiHash, seller, buyer, price)
    trade_info = (imei_hash, seller, buyer, price)

    # 2) SellerInfo tuple 순서: (nonce, signature)
    seller_info = (seller_nonce, seller_signature)

    # 3) BuyerInfo tuple 순서: (nonce, signature, v, r, s, deadline)
    buyer_info = (buyer_nonce, buyer_signature, buyer_v, buyer_r, buyer_s, buyer_deadline)

    tx = contract.functions.tradeIMEI(trade_info, seller_info, buyer_info)
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


def confirmTrade(
    w3: Web3,
    contract: Contract,
    sender: str,
    private_key: str,
    imei_hash: bytes,
    nonce: int,
    signature: bytes
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