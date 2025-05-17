from fastapi.testclient import TestClient
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

from server.config.config import contract
from server.main import app

app = TestClient(app)

# to 만들기
user = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
# imei_hash만들기
imei_hash = keccak(text="IMEI: 123456789012345")
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
nonce_bytes = nonce.to_bytes((nonce.bit_length()+7) // 8 or 1, byteorder='big')

packed = method_bytes + imei_bytes + to_bytes + nonce_bytes
msghash = keccak(packed)

# EIP-191 prefix 붙이기 (Ethereum Signed Message)
message = encode_defunct(msghash)

# 서명
user_private_key = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
signed_message = Account.sign_message(message, user_private_key)
signature = signed_message.signature

# 서명자로부터 주소 복원
recovered_address = Account.recover_message(message, signature=signature)

# 비교 출력
print("Expected address (user):   ", Web3.to_checksum_address(user))
print("Recovered from signature:  ", recovered_address)

# 검증
if Web3.to_checksum_address(user) == recovered_address:
    print("✅ Signature is valid and matches the expected user address.")
else:
    print("❌ Signature does NOT match the expected user address.")

def test_registerIMEI():
    params = {
        "imei_hash": imei_hash.hex(),        # bytes32 → hex string
        "to": user,                          # address
        "nonce": nonce,                      # int
        "signature": signature.hex(),        # bytes → hex string
    }
    response = app.post("/register", json=params)
    print(response.status_code)
    print(response.text)

test_registerIMEI()

