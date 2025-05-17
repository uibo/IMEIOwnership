from web3 import Web3
from web3.contract import Contract
from eth_account.messages import encode_defunct
from eth_account import Account

from server.config.config import w3, contract, SERVER_ADDRESS, SERVER_PRIVATE_KEY

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
    tx_hash = w3.eth.send_raw_transaction(signed_tx)

    return w3.to_hex(tx_hash)

def Test_registerIMEI():
    # to 만들기
    user = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    # imei_hash만들기
    imei_hash = Web3.keccak(text="IMEI: 123456789012345")
    # nonce 만들기
    nonce = contract.functions.userNonce(user).call() + 1

    #signature 만들기
    #method_bytes만들기
    method = "registerIMEI"
    method_bytes = method.encode('utf-8')
    #imei_bytes만들기
    imei_bytes = imei_hash
    #to_bytes만들기
    to_bytes = Web3.to_bytes(hexstr=user)
    #nonce_bytes만들기
    nonce_bytes = nonce.to_bytes(length=32,byteorder='big')

    packedMsg = method_bytes + imei_bytes + to_bytes + nonce_bytes

    msgHash = Web3.keccak(packedMsg)

    # EIP-191 prefix 붙이기 (Ethereum Signed Message)
    ethMsgHash = encode_defunct(msgHash)

    # 서명
    user_private_key = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    signed_message = Account.sign_message(ethMsgHash, user_private_key)
    signature = signed_message.signature

    # 서명자로부터 주소 복원
    recovered_address = Account.recover_message(ethMsgHash, signature=signature)

    print("packedMsg:", packedMsg.hex())
    print("msgHash:", msgHash.hex())
    print("ethMsgHash:", ethMsgHash)
    print("recovered_address:", recovered_address)

    return registerIMEI(w3, contract, SERVER_ADDRESS, SERVER_PRIVATE_KEY, imei_hash, to_bytes, nonce, signature)

Test_registerIMEI()