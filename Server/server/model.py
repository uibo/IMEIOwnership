from pydantic import BaseModel

# 요청 모델 정의
class RegisterIMEIRequest(BaseModel):
    to: str
    imei_hash: str  # bytes32 hash string
    nonce: int
    signature: str  # signed message


class GetIMEIRequest(BaseModel):
    imei_hash: str