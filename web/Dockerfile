FROM node:14

# container 내부에 working directory 설정
WORKDIR /usr/src/app

# package.json과 package-lock.json파일 working directory에 복사 
COPY package*.json ./

# project dependencies 설치
RUN npm install

# 전체 project working directory에 복사
COPY . .

# Build the React app for production
RUN npm run build

# app이 실행될 port 노출
EXPOSE 3000

# application 실행 명령어
CMD ["npm", "start"]