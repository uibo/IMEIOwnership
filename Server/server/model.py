from pydantic import BaseModel

# 요청 모델 정의
class RegisterIMEIRequest(BaseModel):
    imei_hash: bytes
    to: bytes
    nonce: int
    signature: bytes 
