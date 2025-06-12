from fastapi.testclient import TestClient
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import keccak
import json
import os

from server.config.config import contract, w3
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

def make_signature_transfer(private_key: str, imei_hash: str, from_addr: str, to_addr: str, nonce: str) -> str:
    """
    transferIMEI <imeiHash> from <from> to <to> (nonce: <nonce>) 메시지 서명
    """
    prefix = b"transferIMEI "
    imei_bytes = Web3.to_bytes(hexstr=imei_hash)
    mid1 = b" from "
    from_bytes = Web3.to_bytes(hexstr=from_addr)
    mid2 = b" to "
    to_bytes = Web3.to_bytes(hexstr=to_addr)
    nonce_part = b" (nonce: " + nonce.encode("utf-8") + b")"

    packed = prefix + imei_bytes + mid1 + from_bytes + mid2 + to_bytes + nonce_part
    msg_hash = keccak(packed)
    eth_message = encode_defunct(msg_hash)
    signed = Account.sign_message(eth_message, private_key=private_key)
    return Web3.to_hex(signed.signature)


def make_signature_trade(private_key: str, imei_hash: str, seller: str, buyer: str, price: str, nonce: str) -> str:
    """
    tradeIMEI <imeiHash> from <seller> to <buyer> price: <price> (nonce: <nonce>) 메시지 서명
    - 판매자와 구매자 각각 같은 내용으로 서명 (단, nonce 값은 각자 userNonce+1)
    """
    prefix = b"tradeIMEI "
    imei_bytes = Web3.to_bytes(hexstr=imei_hash)
    mid1 = b" from "
    seller_bytes = Web3.to_bytes(hexstr=seller)
    mid2 = b" to "
    buyer_bytes = Web3.to_bytes(hexstr=buyer)
    mid3 = b" price: "
    price_bytes = price.encode("utf-8")
    nonce_part = b" (nonce: " + nonce.encode("utf-8") + b")"

    packed = prefix + imei_bytes + mid1 + seller_bytes + mid2 + buyer_bytes + mid3 + price_bytes + nonce_part
    msg_hash = keccak(packed)
    eth_message = encode_defunct(msg_hash)
    signed = Account.sign_message(eth_message, private_key=private_key)
    return Web3.to_hex(signed.signature)


def make_signature_confirm(private_key: str, imei_hash: str, nonce: str) -> str:
    """
    confirmTrade <imeiHash> (nonce: <nonce>) 메시지 서명
    """
    prefix = b"confirmTrade "
    imei_bytes = Web3.to_bytes(hexstr=imei_hash)
    nonce_part = b" (nonce: " + nonce.encode("utf-8") + b")"

    packed = prefix + imei_bytes + nonce_part
    msg_hash = keccak(packed)
    eth_message = encode_defunct(msg_hash)
    signed = Account.sign_message(eth_message, private_key=private_key)
    return Web3.to_hex(signed.signature)


def test_registerIMEI():
    imei_hash = "0x" + keccak(text="IMEI: 012345678901235").hex()
    to = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"# 첫번째 소유자자
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
    imei_hash = "0x" + keccak(text="IMEI: 012345678901235").hex()
    params = {"imei_hash": imei_hash}
    response = app.post("/get", json=params)
    print(response.text)

# test_registerIMEI()
# test_get_imei_owner()

def test_transfer_imei():
    # 1) 위 test_register_and_get 에서 사용한 IMEI 그대로 사용
    imei_hash = "0x" + keccak(text="IMEI: 012345678901235").hex()

    # 2) from(현재 소유자) = w3.eth.accounts[1], to(새 소유자) = w3.eth.accounts[2]
    from_addr = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    to_addr = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"#두번째 소유자

    # 3) 현재 userNonce[from] + 1
    # current_nonce = contract.functions.userNonce(from_addr).call()
    # next_nonce = current_nonce + 1
    nonce = str(contract.functions.userNonce(from_addr).call() + 1)
    # 4) from 계정의 개인키 (Anvil index=1)
    from_private_key = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

    # 5) transferIMEI 서명 생성
    signature = make_signature_transfer(
        private_key=from_private_key,
        imei_hash=imei_hash,
        from_addr=from_addr,
        to_addr=to_addr,
        nonce= nonce
    )
   

    # 6) /transfer 호출
    payload = {
        "imei_hash": imei_hash,
        "from_addr": from_addr,
        "to_addr": to_addr,
        "nonce": nonce,
        "signature": signature
    }
    resp = app.post("/transfer", json=payload)
    assert resp.status_code == 200
    tx_hash = resp.json().get("tx_hash")
    assert tx_hash.startswith("0x")

    # 7) /get 호출해서 새 소유자가 to_addr 인지 확인
    resp2 = app.post("/get", json={"imei_hash": imei_hash})
    assert resp2.status_code == 200
    new_owner = resp2.json() 
    assert Web3.to_checksum_address(new_owner) == Web3.to_checksum_address(to_addr)
    print("TransferIMEI: OK → new owner =", new_owner)


# ----------------------------------------------------------------------------
# 3) test_tradeIMEI → seller=accounts[2], buyer=accounts[3] 로 가정
# ----------------------------------------------------------------------------
def test_trade_imei():
    # 1) 같은 IMEI 해시 사용
    imei_hash = "0x" + keccak(text="IMEI: 012345678901235").hex()

    # 2) seller (현재 소유자) = accounts[2], buyer = accounts[3]
    seller = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    buyer = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"#3번째 소유자자
    price = "1000000000000000000"  # 예: 1 토큰 (단위: wei)
    #    실제 IMEICurrency 토큰 18 decimals 라고 가정

    # 3) seller_nonce = userNonce[seller] + 1
    seller_nonce = str(contract.functions.userNonce(seller).call() + 1)
    # 4) buyer_nonce = userNonce[buyer] + 1
    buyer_nonce = str(contract.functions.userNonce(buyer).call() + 1)

    # 5) seller, buyer 개인키 (Anvil seed 계정 index=2,3)
    seller_key = "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
    buyer_key  = "0x7c852118294e51e653712a81e05800f88e7a6d8d0520da1ed52e6d0e5f7e07d6"

    # 6) tradeIMEI 메시지 서명 (판매자, 구매자 각각)
    seller_sig = make_signature_trade(
        private_key=seller_key,
        imei_hash=imei_hash,
        seller=seller,
        buyer=buyer,
        price=price,
        nonce=seller_nonce
    )
    buyer_sig = make_signature_trade(
        private_key=buyer_key,
        imei_hash=imei_hash,
        seller=seller,
        buyer=buyer,
        price=price,
        nonce=buyer_nonce
    )

    # 7) EIP-2612 permit 을 위한 서명 생성 (buyer side)
    #    이 부분은 IMEICurrency 컨트랙트가 permit 메소드를 올바로 지원한다고 가정한 예시입니다.
    
    abi_path = os.path.join(os.getcwd(), "abi", "IMEICurrency.json")
    with open(abi_path, "r", encoding="utf-8") as f:
        full_json = json.load(f)
        token_abi = full_json["abi"]

    token_address = contract.functions.token().call()
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)

    buy_token_nonce = token_contract.functions.nonces(buyer).call()
    # 7-2) deadline 설정 (1시간 후)
    import time
    deadline = int(time.time()) + 3600

    # 7-3) EIP-712 도메인/Message 구조에 맞춰 서명
    #      IMEICurrency contract의 DOMAIN_SEPARATOR, PERMIT_TYPEHASH 등 내부 구현을 참고해야 합니다.
    #      (여기서는 예시일 뿐, 실제 EIP-2612 signTypedData 로직으로 대체해야 합니다.)
    #
    #    아래는 EIP-2612 메시지를 잡는 가상의 로직 예시
    #
    domain_separator = token_contract.functions.DOMAIN_SEPARATOR().call()
    permit_typehash = keccak(text="Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)")
    # solidity keccakPacked(owner, spender, value, nonce, deadline)
    struct_hash = keccak(
        b"\x19\x01" +
        domain_separator +
        keccak(
            Web3.to_bytes(hexstr=Web3.to_checksum_address(buyer)[2:]) +
            Web3.to_bytes(hexstr=Web3.to_checksum_address(contract.address)[2:]) +
            int(price).to_bytes(32, byteorder="big") +
            buy_token_nonce.to_bytes(32, byteorder="big") +
            deadline.to_bytes(32, byteorder="big")
        )
    )
    eth_message = encode_defunct(struct_hash)
    signed_permit = Account.sign_message(eth_message, buyer_key)
    v, r, s = signed_permit.v, signed_permit.r, signed_permit.s

    # 8) /trade 호출
    payload = {
        "imei_hash": imei_hash,
        "seller": seller,
        "buyer": buyer,
        "price": price,
        "seller_nonce": seller_nonce,
        "seller_signature": seller_sig,
        "buyer_nonce": buyer_nonce,
        "buyer_signature": buyer_sig,
        "buyer_v": str(v),
        "buyer_r": Web3.to_hex(r),
        "buyer_s": Web3.to_hex(s),
        "buyer_deadline": str(deadline)
    }
    resp = app.post("/trade", json=payload)
    assert resp.status_code == 200
    tx_hash = resp.json().get("tx_hash")
    assert tx_hash.startswith("0x")
    print("tradeIMEI tx:", tx_hash)

    # 9) Escrow가 pending 상태일 때, 컨트랙트 내부 상태를 직접 query 해 볼 수도 있습니다.
    #    (예: contract.functions.imeiHashToEscrow(imei_hash).call() → (seller, buyer, price, isPending))
    escrow_data = contract.functions.imeiHashToEscrow(imei_hash).call()
    assert escrow_data[0] == Web3.to_checksum_address(seller)   # seller
    assert escrow_data[1] == Web3.to_checksum_address(buyer)    # buyer
    assert escrow_data[2] == int(price)                         # price
    assert escrow_data[3] is True                                # isPending

    print("Escrow state after tradeIMEI: ", escrow_data)


# ----------------------------------------------------------------------------
# 4) test_confirmTrade → buyer가 confirmTrade 호출
# ----------------------------------------------------------------------------
def test_confirm_trade():
    # 1) 동일 IMEI 해시
    imei_hash = "0x" + keccak(text="IMEI: 012345678901235").hex()

    # 2) buyer = w3.eth.accounts[3]
    buyer = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
    # 3) userNonce[buyer] + 1
    buyer_nonce = str(contract.functions.userNonce(buyer).call() + 1)
    # 4) buyer 개인키 (Anvil index=3)
    buyer_key = "0x7c852118294e51e653712a81e05800f88e7a6d8d0520da1ed52e6d0e5f7e07d6"
    # 5) confirmTrade 서명 생성
    confirm_sig = make_signature_confirm(
        private_key=buyer_key,
        imei_hash=imei_hash,
        nonce=buyer_nonce
    )
    # 6) /confirm 호출
    payload = {
        "imei_hash": imei_hash,
        "nonce": buyer_nonce,
        "signature": confirm_sig
    }
    resp = app.post("/confirm", json=payload)
    assert resp.status_code == 200
    tx_hash = resp.json().get("tx_hash")
    assert tx_hash.startswith("0x")

    # 7) Escrow 삭제됐는지 확인 (isPending=False or default)
    #    (만약 mapping에서 삭제되면, isPending 필드는 False를 리턴하거나, 
    #     호출 시 revert 되지 않으면 buyer와 price가 0이 될 수 있음)
    escrow_data = contract.functions.imeiHashToEscrow(imei_hash).call()
    # Solidity delete 후, buyer와 price가 0으로 초기화 됐는지 확인
    assert escrow_data[3] is False
    print("confirmTrade complete, Escrow removed: ", escrow_data)


# ----------------------------------------------------------------------------
# 실제 테스트 함수들 실행 순서
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    test_registerIMEI()
    test_get_imei_owner()
    
    test_transfer_imei()
    #test_trade_imei()
    #test_confirm_trade()