# IMEIOwnership Server
IMEIOwnership Web3 Project의 Server 프로젝트
## 프로젝트 소개
> 현재 로컬에 배포된 IMEIOwnership Contract의 함수 호출 Tx를 서버의 개인키로 서명하여 대신 호출한다. 이러한 Tx 호출 API를 제공한다.  
IMEI 판매자의 정보를 db에 임시보관하여 구매자가 입력한 정보와 일치했을때 tradeIMEI Tx를 호출하는 거래 매칭 서비스를 제공한
### 주요 파일 소개
```
현재 루트 폴더인 Contract 폴더는 기본적으로 foundry로 관리된다.
Server
├── server/      
│ │ ├─ config/ IMEICurrency와 IMEIOwnership Contract의 abi, 서버 개인키, Contract address, RPC_URL 설정 파일 배치하는 곳
│ │ ├─ function.py, main.py, model.py Tx 를 대리호출 해주는 서버 구현체  
└── test/  서버 api를 테스트하기 위한 파일 존재
```
### 실행 과정
1. 프로젝트 의존성 설치 **poetry install**
2. 컨트랙트, 노드, 서버 관련 설정파일 생성 **server/config/config.py 참고**
3. 서버 실행 **pwd ./server/ poetry run uvicorn main:app**
