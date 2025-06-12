# IMEIOwnership 프로젝트
실물 단말기 소유에 대응하는 소유권 기록 시스템. 해당 시스템을 BlockChain상에 공개된 상태로 기록하며, 안전한 거래 시스템 구축에 목적이 있다.

---

## 폴더 구조
Contract: IMEIOwnership Contract 폴더 / foundry로 관리  
Server: IMEIOwnership Server 폴더 / foetry로 관리  
Clinet: IMEIOwnership Client 폴더 / vue로 관리  
 
---
## 프로젝트 설명
IMEI 소유권 기록 시스템을 블록체인에 구축하는 프로젝트이다. IMEI의 hash값이 블록체인에서 사용하는 계정주소에 매핑되어, 단말기의 IMEI의 소유자를 계정주소로써 확인할 수 있다.  
Contract는 이러한 정보가 기록된 Mapping 객체를 관리하고, 등록, 전송, 거래와 같은 실질적인 on-chain 로직이 구현돼있다.  
Server는 사용자가 클라이언트를 통해 입력한 값을 컨트랙트로 전달해주는 매개역할을 한다. 그 밖에 거래 매칭 등 소유권과 관련한 부가적인 작업을 처리한다.  
Client는 추후 안드로이드로 구현할 클라이언트를 웹으로 모의적으로 구현하였다. 기기에 IMEI값과 연동된 메타마스크 계정을 활용해 signature와 parameter를 만든다. 이 값들로 Tx를 요청하기 위해 서버에게 전달한다.  
