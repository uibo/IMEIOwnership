from pydantic import BaseModel

# 요청 모델 정의
class RegisterIMEIRequest(BaseModel):
    imei_hash: str
    to: str
    nonce: str
    signature: str 

class GetIMEIOwnerRequest(BaseModel):
    imei_hash: str
    
class TransferIMEIRequest(BaseModel):
    imei_hash: str    # 32바이트 hex 문자열
    from_addr: str    # 기존 소유자 주소 (체크섬 형태)
    to_addr: str      # 새 소유자 주소 (체크섬 형태)
    nonce: str        # nonce (문자열)
    signature: str    # 서명 hex 문자열

class TradeIMEIRequest(BaseModel):
    imei_hash: str         # 32바이트 hex 문자열
    seller: str            # 판매자 주소 (체크섬)
    buyer: str             # 구매자 주소 (체크섬)
    price: str             # 가격 (문자열, 나중에 int로 변환)
    seller_nonce: str      # 판매자 nonce (문자열)
    seller_signature: str  # 판매자 서명 hex 문자열
    buyer_nonce: str       # 구매자 nonce (문자열)
    buyer_signature: str   # 구매자 서명 hex 문자열
    buyer_v: str           # permit 용 v (문자열)
    buyer_r: str           # permit 용 r (32바이트 hex)
    buyer_s: str           # permit 용 s (32바이트 hex)
    buyer_deadline: str    # permit 용 deadline (문자열, 나중에 int로 변환)

class ConfirmTradeRequest(BaseModel):
    imei_hash: str    # 32바이트 hex 문자열
    nonce: str        # nonce (문자열)
    signature: str    # 서명 hex 문자열