# 서버 메인 파일
from flask import Flask, current_app
from contextlib import closing
from flask_cors import CORS
from dotenv import load_dotenv
import os
from db.db_controller import initialize_db

from connection.firebase_connect import FireBase_
from connection.s3_connect import S3_
from utils import logger
import json
import base64

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


def initialize_services():
    # 환경변수 다운로드
    load_dotenv()
    # RDS DB 연결
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Using Flask Application
    with app.app_context():
        # 1. DB Session Connection
        current_app.db_session = initialize_db(app)

        # 2. S3 Connection
        current_app.s3_conn = S3_(
            s3_bucket_name=os.getenv("S3_BUCKET_NAME"),
            service_name="s3",
            region_name=os.getenv("S3_REGION_NAME"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # 3. Firebase Connection
        current_app.firestore_conn = FireBase_("serviceAccountKey.json")


initialize_services()
CORS(app)
#  API Blueprint Connection
from api.user_api import user_api
from api.create_api import create_api
from api.get_api import get_api
from api.update_api import update_api
from api.delete_api import delete_api
from api.statistic_api import statistic_api

app.register_blueprint(user_api, url_prefix="/user")  # user 관련 API
app.register_blueprint(create_api, url_prefix="/meat/create")  # 육류 정보 조회 API
app.register_blueprint(get_api, url_prefix="/meat/get")  # 육류 정보 조회 API
app.register_blueprint(update_api, url_prefix="/meat/update")  # 육류 정보 수정 API
app.register_blueprint(delete_api, url_prefix="/meat/delete")  # 육류 정보 삭제 API
app.register_blueprint(statistic_api, url_prefix="/statistic")  # 통계 데이터 조회 API
# Flask 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
