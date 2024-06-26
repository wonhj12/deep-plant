from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_model import User
from db.db_controller import create_user, get_user, _get_users_by_type, update_user
import hashlib
import uuid
from datetime import datetime
from utils import logger

user_api = Blueprint("user_api", __name__)


# 유저 등록 API
@user_api.route("/register", methods=["GET", "POST"])
def register_user_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            user = create_user(db_session, data)

            db_session.add(user)
            db_session.commit()
            return jsonify({"msg": f"{data['userId']}"}), 200
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

# 유저 정보 반환 API
@user_api.route("/get", methods=["GET", "POST"])
def read_user_data():
    try:
        db_session = current_app.db_session
        if request.method == "GET":
            userId = request.args.get("userId")
            if userId:
                result = get_user(db_session, userId)
            else:
                result = _get_users_by_type(db_session)
            return jsonify(result), 200
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

# 유저 정보 수정 API
@user_api.route("/update", methods=["GET", "POST"])
def update_user_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            user = update_user(db_session, data)

            db_session.merge(user)
            db_session.commit()
            return jsonify(get_user(db_session, data.get("userId"))), 200
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

# 유저 아이디 중복 체크 API
@user_api.route("/id-check", methods=["GET", "POST"])
def check_duplicate():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = request.args.get("userId")
            user = db_session.query(User).filter_by(userId=id).first()
            if user is None:
                return jsonify({"msg": "None Duplicated Id"}), 200
            else:
                return jsonify({"msg": "Duplicated Id"}), 401
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

# 유저 비밀번호 체크 API
@user_api.route("/pwd-check", methods=["GET", "POST"])
def check_pwd():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            id = data.get("userId")
            password = data.get("password")
            user = db_session.query(User).filter_by(userId=id).first()
            if user is None:
                return (
                    jsonify(
                        {
                            "msg": f"No user data in Database",
                            "userId": id,
                        }
                    ),
                    404,
                )
            if user.password != hashlib.sha256(password.encode()).hexdigest():
                return (
                    jsonify(
                        {
                            "msg": f"Invalid password for userId",
                            "userId": id,
                        }
                    ),
                    401,
                )

            return jsonify(get_user(db_session, id)), 200
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

# 유저 정보 삭제 API
@user_api.route("/delete", methods=["GET", "POST"])
def delete_user():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = request.args.get("userId")
            user = db_session.query(User).filter_by(userId=id).first()
            if user is None:
                return (
                    jsonify(
                        {
                            "msg": f"No user data in Database",
                            "userId": id,
                        }
                    ),
                    404,
                )
            try:
                db_session.delete(user)
                db_session.commit()
                return (
                    jsonify(
                        {
                            f"msg": f"User with userId has been deleted",
                            "userId": id,
                        }
                    ),
                    200,
                )
            except:
                db_session.rollback()
                raise Exception("Deleted Failed")

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 401
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )
