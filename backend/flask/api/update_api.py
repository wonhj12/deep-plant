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
from db.db_controller import _updateConfirmData, _updateRejectData
from utils import *

update_api = Blueprint("update_api", __name__)

# 육류 데이터 승인 API
@update_api.route("/confirm", methods=["GET", "POST"])
def updateConfirmData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = safe_str(request.args.get("id"))
            if id:
                return _updateConfirmData(db_session, id)
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

# 육류 데이터 반려 API
@update_api.route("/reject", methods=["GET", "POST"])
def updateRejectData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = safe_str(request.args.get("id"))
            if id:
                return _updateRejectData(db_session, id)
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
