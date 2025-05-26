from pydantic import BaseModel

# 요청 모델 정의
class RegisterIMEIRequest(BaseModel):
    imei_hash: str
    to: str
    nonce: str
    signature: str 

class GetIMEIOwnerRequest(BaseModel):
    imei_hash: str