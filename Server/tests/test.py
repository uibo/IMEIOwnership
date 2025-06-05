from fastapi.testclient import TestClient
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak

from server.config.config import contract
from server.main import app

app = TestClient(app)

def make_signature(private_key, imeiHash: str, to: str, nonce: str) -> bytes:
    method_bytes = b"registerIMEI "
    imei_bytes = Web3.to_bytes(hexstr=imeiHash)                     # 32바이트
    to_bytes = Web3.to_bytes(hexstr=to)                             # 20바이트
    mid_bytes = b" to "
    nonce_prefix = b" (nonce: "
    nonce_bytes = nonce.encode('utf-8')                        # 문자열 숫자 → 바이트
    end_paren = b")"
    packedMsg = method_bytes + imei_bytes + mid_bytes + to_bytes + nonce_prefix + nonce_bytes + end_paren
    msg_hash = keccak(packedMsg)
    eth_msg_hash = encode_defunct(msg_hash)
    signature = Account.sign_message(eth_msg_hash, private_key).signature.to_0x_hex()

    return signature


def test_registerIMEI():
    imei_hash = "0x" + keccak(text="IMEI: 123456789012349").hex()
    to = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    nonce = str(contract.functions.userNonce(to).call() + 1)
    signature = make_signature("0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d", imei_hash, to, nonce)
    params = {
        "imei_hash": imei_hash,        #hexstr
        "to": to,                      #hexstr
        "nonce": nonce,                #str
        "signature": signature,        #hexstr
    }
    response = app.post("/register", json=params)
    assert response.status_code == 200
    print("txhash: ", response.text)

def test_get_imei_owner():
    imei_hash = "0x" + keccak(text="IMEI: 123456789012349").hex()
    params = {"imei_hash": imei_hash}
    response = app.post("/get", json=params)
    print(response.text)

test_registerIMEI()
test_get_imei_owner()