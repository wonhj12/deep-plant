# Base Python Image
FROM python:3.10.11-slim
RUN apt-get update && apt-get install -y gcc libffi-dev musl-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Build Arguments 정의

# 라이브러리 설치
COPY . /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너 포트 설정
EXPOSE 8080

# Define Environment Var
ENV NAME World

# Flask 앱 실행
CMD ["gunicorn","-c","gunicorn.conf.py","app:app"]