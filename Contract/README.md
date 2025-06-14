# IMEIOwnership Contract
IMEIOwnership Web3 Project의 Contract 프로젝트이다. 블록체인상에서 IMEI의 소유권을 기록, 관리, 전송, 교환과 같은 실제 로직이 구현되어있다.
## 프로젝트 소개
### 주요 파일 소개
```
현재 루트 폴더인 Contract 폴더는 기본적으로 foundry로 관리된다.
Contract
├── script/    IMEICurrency와 IMEIOwnership Contract 배포를 요청하는 스크립트가 포함되어있다.
├── src/       IMEICurrency와 IMEIOwnership Contract의 실제 구현체
└── test/      IMEIOwnershipContract의 함수들의 동작을 테스트하기 위한 스크립트
```
### 실행 과정
1. foundryup 설치 확인
2. 프로젝트 의존성 설치 및 Contract 컴파일 진행 **forge build**
3. 로컬 블록체인 실행 **anvil --dump-state state.json**
4. 컨트랙트 배포 **forge script script/IMEIOwnership.s.sol --rpc-url 127.0.0.1:8545 --broadcast --private-key $PRIVATE_KEY**
