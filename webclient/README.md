# IMEIOwnership webclient Project
IMEIOwnership Web3 Project에 Contract와 Server의 동작을 확인해보기 위한 webclient 프로젝트이다.
## 프로젝트 소개
> meta-transaction을 지원하는 서버의 API를 호출해볼 수 있는 웹 클라이언트이다. 실제 metamask와 연동하여 연결 계정의 메시지 서명을 만들어 IMEIOwnership Contract의 IMEI 소유권 시스템을 이용해볼 수 있다.
### 주요 파일 소개
```
현재 루트 폴더인 webclient는 vue로 관리된다.
webclient
├── src/      
│ │ ├─ api/api.js 서버의 API 스펙에 맞춘 JSON 포맷의 body를 받아 서버 API를 호출하는 함수
│ │ ├─ composable/ contract.js 연결된 메타마스크 계정 또는 RPC_URL로 컨트랙트 정보를 직접 호출하기 위한 설정
│ │ │ │ │ │ │ │ └─ function.js 연결된 메타마스크 계정에 서명 요청 또는 RPC_URL로 컨트랙트 상태 조회를 정의한 함수들
│ │ ├─ router/index.js 존재하는 페이지의 경로를 결정하는 라우터
│ │ ├─ views/ 클라이언트 기능 지원을 위해 라우터에 등록된 페이지들이 존재하는 폴더
│ ├─ App.vue 페이지의 사이드바와 메타마스크 연결 UI가 정의된 페이지
│ └─ main.js vue.app을 정의하는 파일
```

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
