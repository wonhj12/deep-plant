# Deeplant1

<div align="center">
<img width="300" alt="image" src="https://raw.githubusercontent.com/SincerityHun/Deep_Plant1_Final/main/web/images/l_deeplant.png">

</div>

# Deeplant1 Web Page

> **고려대학교 산학협력프로젝트 딥플랜트1 Web** <br/> **개발기간: 2023.04 ~ 2023.12**

## 배포 주소

> **프론트 서버(배포방법1)** : [http://43.202.4.18:8080/](http://43.202.4.18:8080/) <br>
> **프론트 서버(배포방법2)** : [http://43.202.217.225:3000/](http://43.202.217.225:3000/)<br>

## 웹개발팀 

| 김성중 (Kim Seongjung) | 박수현 (Park Suhyun) |
| :---------------------: | :------------------: |
| <img width="160px" src="https://avatars.githubusercontent.com/u/102349883?s=400&v=4" alt="Kim Seongjung" /> | <img width="160px" src="https://avatars.githubusercontent.com/u/73726272?v=4" alt="Park Suhyun" /> |
| [GitHub: @qpwozxc](https://github.com/qpwozxc) | [GitHub: @claspsh](https://github.com/clapsh) |
| 성균관대학교 소프트웨어학과 2학년 | 성균관대학교 소프트웨어학과 4학년 |


## 프로젝트 소개
육류 및 유저 데이터의 입력/수정/조회/통계 기능이 탑재된 관리자 도메인

---
## 주요 기능

### 대시보드
- 목록 - 육류데이터 조회, 삭제, 엑셀 import/export 가능
- 통계 - 육류데이터의 원육 및 숙성육 비율, 부위 별 데이터 수, 지역 별 데이터 수에 대한 통계 조회 가능
- 반려 - 반려 상태 육류데이터 조회, 삭제 가능

### 상세조회
- 개별적인 육류 데이터가 승인 상태인 경우, 해당 육류 데이터에 대해 상세한 정보 조회, 수정 가능
- 개별적인 육류 데이터가 대기 및 반려 상태인 경우, 상세한 정보 조회, 승인 또는 반려로 상태 변경 가능

### 통계 분석
- 맛/관능, 원육/처리육/가열육 별 통계, 빈도수, 상관관계, 시계열 등을 날짜 별로 조회

### 데이터 예측
- 예측할 육류데이터 조회 가능
- 개별적인 육류 데이터의 상세한 정보 조회 가능, 데이터 및 등급 예측 가능


### 사용자 관리
- 사용자 검색, 신규 회원 등록, 권한 변경, 사용자 삭제 기능

### 프로필
- 프로필 정보 수정 및 회원 탈퇴 기능
---

## 시작 가이드-로컬
### Requirements

- [Node.js 20.9.0](https://nodejs.org/en/blog/release/v20.9.0/)
- [Npm 10.1.0](https://www.npmjs.com/package/npm/v/10.1.0)

### Installation
``` bash
$ git clone https://github.com/SincerityHun/Deep_Plant1_Final.git
$ cd Deep_Plant1_Final
```
### Start Web 
```
# web 폴더에서 진행
$ cd web
$ npm run start
```
### Start Web (using docker-compose)
```
# web 폴더에서 진행
$ cd web

# 이미지 빌드
$ docker-compose build

# 컨테이너 포함 전체 서비스 실행
$ docker-compose up 

# 전체 서비스 정지 및 컨테이너 삭제
$ docker-compose down 
```
---

## 시작 가이드-자동배포

### Installation
``` bash
$ git clone https://github.com/SincerityHun/Deep_Plant1_Final.git
$ cd Deep_Plant1_Final
```
### Set secrets for a repository
 "Settings>Security>Secrets>Actions" 탭에 접근해 나오는 secrets로 환경변수 관리
#### 환경변수
  ##### DOCKERHUB_TOKEN
   - docker hub 계정 비밀번호
  ##### DOCKERHUB_USERNAME
   - docker hub 계정 username
  ##### HOST
   - EC2 서버 IP 주소
  ##### PEM_KEY
   - AWS ssh 접속을 위한 키 파일 (.pem)
  ##### USER
   - EC2 USER 이름 (default: ec2-user)

### Start Web 
```
# web 폴더에서 진행
$ cd web

...

# main branch에 변경 내용 push
$ git push origin main
```
---
## 화면 구성
| 로그인 페이지  |  홈페이지   |
| :-------------------------------------------: | :------------: |
|  <img width="400" src="https://github.com/SincerityHun/Deep_Plant1_Final/blob/main/web/images/s_login.png?raw=true"/> |  <img width="400" src="https://github.com/SincerityHun/Deep_Plant1_Final/blob/main/web/images/s_home.png?raw=true"/>| 
| 대시보드 페이지   |  데이터 예측 페이지   |  
| <img width="400" src="https://github.com/SincerityHun/Deep_Plant1_Final/blob/main/web/images/s_dashboard.png?raw=true"/>   |  <img width="400" src="https://github.com/SincerityHun/Deep_Plant1_Final/blob/main/web/images/s_data_predict.png?raw=true"/>     |
| 통계 페이지    |   유저 관리 페이지   |
| <img width="400" src="https://github.com/SincerityHun/Deep_Plant1_Final/blob/main/web/images/s_statistics.png?raw=true"/>   |  <img width="400" src="https://github.com/SincerityHun/Deep_Plant1_Final/blob/main/web/images/s_user_management.png?raw=true"/>     |

<!-- ---
### EC2 인스턴스 접속 후 배포
```
$ cd web
$ ssh -i DeeplantWebkey.pem ubuntu@43.202.4.18
$ cd DP_Admin/frontend
$ npm run build
``` -->

## Stacks

### Environment
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)             

### Config
![npm](https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white)
![node](https://img.shields.io/badge/node.js-339933?style=for-the-badge&logo=Node.js&logoColor=white)        

### Development
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=Javascript&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=Bootstrap&logoColor=white)
![Material UI](https://img.shields.io/badge/Material%20UI-007FFF?style=for-the-badge&logo=MUI&logoColor=white)

### Communication
![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=Slack&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white)

