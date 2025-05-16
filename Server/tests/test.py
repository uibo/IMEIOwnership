from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

# 서명자 개인 키 (테스트용)
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

to_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
imei_hash = "0xabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabca"
nonce = 1

# 해시 만들기 (Solidity와 동일하게)
message = (
    Web3.to_bytes(text="registerIMEI") +
    Web3.to_bytes(hexstr=to_address) +
    Web3.to_bytes(hexstr=imei_hash) +
    nonce.to_bytes(32, byteorder='big')
)
message_hash = Web3.keccak(message)

# Ethereum Signed Message
eth_message = encode_defunct(message_hash)
signed_message = Account.sign_message(eth_message, private_key=private_key)

# FastAPI 요청에 필요한 정보
print("to:", to_address)
print("imei_hash:", imei_hash)
print("nonce:", nonce)
print("signature:", signed_message.signature.hex())
