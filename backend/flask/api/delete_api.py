from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    redirect,
    url_for,
    render_template_string,
    current_app,
)
from db.db_controller import _deleteSpecificMeatData, _deleteSpecificDeepAgingData
from api.user_api import get_user
from utils import *

delete_api = Blueprint("delete_api", __name__)

# 전체 육류 데이터 삭제
@delete_api.route("/", methods=["GET", "POST"])
def deleteTotalMeatData():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            s3_conn = current_app.s3_conn
            firebase_conn = current_app.firebase_conn
            data = request.get_json()
            if data:
                delete_list = list(data.get("delete_id"))
                for case in delete_list:
                    result = _deleteSpecificMeatData(
                        db_session, s3_conn, firebase_conn, case
                    )
                return jsonify({"delete_success": delete_list}), 200
            else:
                return jsonify("No Data in Request"), 404
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

# 특정 육류 데이터 삭제
@delete_api.route("/by-id", methods=["GET", "POST"])
def deleteSpecificMeatData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            s3_conn = current_app.s3_conn
            firebase_conn = current_app.firebase_conn
            id = safe_str(request.args.get("id"))
            if id:
                return _deleteSpecificMeatData(db_session, s3_conn, firebase_conn, id)
            else:
                return jsonify("No id parameter"), 401

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

# 특정 딥에이징 이력 삭제
@delete_api.route("/deep-aging", methods=["GET", "POST"])
def deleteDeepAgingData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            s3_conn = current_app.s3_conn
            firebase_conn = current_app.firebase_conn
            id = safe_str(request.args.get("id"))
            seqno = safe_str(request.args.get("seqno"))
            if id and seqno:
                return _deleteSpecificDeepAgingData(
                    db_session, s3_conn, firebase_conn, id, seqno
                )
            else:
                return jsonify("No id parameter"), 401

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
