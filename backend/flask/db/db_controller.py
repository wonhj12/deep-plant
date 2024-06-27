from flask import jsonify
import requests
from utils import *
from db.db_model import *
import uuid
import hashlib
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import os
import json


# SET UP CONTROLLER
def load_initial_data(db_session):
    """
    초기 데이터 셋업 function
    """
    # 1. Specie
    for id, specie in enumerate(species):
        if not SpeciesInfo.query.get(id):
            temp = SpeciesInfo(id=id, value=specie)  # 0: Cattle, 1: Pig
            db_session.add(temp)
    db_session.commit()

    # 2. Cattle
    for id, large in enumerate(cattleLarge):
        for s_id, small in enumerate(cattleSmall[id]):
            index = calId(id, s_id, CATTLE)
            if not CategoryInfo.query.get(index):
                temp = CategoryInfo(
                    id=index,
                    speciesId=CATTLE,
                    primalValue=large,
                    secondaryValue=small,
                )
                db_session.add(temp)
    db_session.commit()

    # 3. Pig
    for id, large in enumerate(pigLarge):
        for s_id, small in enumerate(pigSmall[id]):
            index = calId(id, s_id, PIG)
            if not CategoryInfo.query.get(index):
                temp = CategoryInfo(
                    id=index,
                    speciesId=PIG,
                    primalValue=large,
                    secondaryValue=small,
                )
                db_session.add(temp)
    db_session.commit()

    # 4. User
    for id, Type in usrType.items():
        if not UserTypeInfo.query.get(id):
            temp = UserTypeInfo(id=id, name=Type)
            db_session.add(temp)
    db_session.commit()

    # 5. GradeNum
    for id, Type in gradeNum.items():
        if not GradeInfo.query.get(id):
            temp = GradeInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()

    # 6. SexType
    for id, Type in sexType.items():
        if not SexInfo.query.get(id):
            temp = SexInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()

    # 7. StatusType
    for id, Type in statusType.items():
        if not StatusInfo.query.get(id):
            temp = StatusInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()


def initialize_db(app):
    db_session = None
    try:
        # 1. DB Engine 생성
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        # 2. 생성한 DB 엔진에 세션 연결
        db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        # 3. Default 쿼리 설정
        Base.query = db_session.query_property()
        # 4. 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        # 5. DB 초기 데이터 설정
        load_initial_data(db_session)
    except Exception as e:
        print(e)
    else:
        print("Connect DB OKAY")
    # 6. db_session을 반환해 DB 세션 관리
    return db_session


def find_id(species_value, primal_value, secondary_value, db_session):
    """
    category id 지정 function
    Params
    1. specie_value: "cattle" or "pig
    2. primal_value: "대분할 부위"
    3. secondary_value: "소분할 부위"
    4. db: 세션 db

    Return
    1. Category.id
    """
    # Find specie using the provided specie_value
    specie = db_session.query(SpeciesInfo).filter_by(value=species_value).first()

    # If the specie is not found, return an appropriate message
    if not specie:
        raise Exception("Invalid species data")

    # Find category using the provided primal_value, secondary_value, and the specie id
    category = (
        db_session.query(CategoryInfo)
        .filter_by(
            primalValue=primal_value,
            secondaryValue=secondary_value,
            speciesId=specie.id,
        )
        .first()
    )

    # If the category is not found, return an appropriate message
    if not category:
        raise Exception("Invalid primal or secondary value")

    # If everything is fine, return the id of the found category
    return category.id


def decode_id(id, db_session):
    result = {"specie_value": None, "primal_value": None, "secondary_value": None}
    category = db_session.query(CategoryInfo).filter_by(id=id).first()
    specie = db_session.query(SpeciesInfo).filter_by(id=category.speciesId).first()
    result["specie_value"] = specie.value
    result["primal_value"] = category.primalValue
    result["secondary_value"] = category.secondaryValue
    return result["specie_value"], result["primal_value"], result["secondary_value"]


# CREATE
def create_meat(meat_data: dict, db_session):
    if meat_data is None:
        raise Exception("Invalid Meat Data")
    # 1. Get the ID of the record in the SexType table
    sex_type = (
        db_session.query(SexInfo).filter_by(value=meat_data.get("sexType")).first()
    )
    # 2. Get the ID of the record in the GradeNum table
    grade_num = (
        db_session.query(GradeInfo).filter_by(value=meat_data.get("gradeNum")).first()
    )
    # 3. meat_data에 없는 필드 추가

    # 4, meat_data에 있는 필드 수정
    for field in list(meat_data.keys()):
        if field == "sexType":
            try:
                item_encoder(meat_data, field, sex_type.id)
            except Exception as e:
                raise Exception("Invalid sex_type id")
        elif field == "gradeNum":
            try:
                item_encoder(meat_data, field, grade_num.id)
            except Exception as e:
                raise Exception("Invalid grade_num id")
        elif (
            field == "specieValue"
            or field == "primalValue"
            or field == "secondaryValue"
        ):
            item_encoder(
                meat_data,
                "categoryId",
                find_id(
                    meat_data.get("specieValue"),
                    meat_data.get("primalValue"),
                    meat_data.get("secondaryValue"),
                    db_session,
                ),
            )
        else:
            item_encoder(meat_data, field)

    # 5. meat_data에 없어야 하는 필드 삭제
    meat_data.pop("specieValue")
    meat_data.pop("primalValue")
    meat_data.pop("secondaryValue")

    # Create a new Meat object
    try:
        new_meat = Meat(**meat_data)
    except Exception as e:
        raise Exception("Wrong meat DB field items" + str(e))
    return new_meat


def create_DeepAging(meat_data: dict):
    if meat_data is None:
        raise Exception("Invalid Deep Aging meat_data")
    for field in meat_data.keys():
        item_encoder(meat_data, field)
    meat_data["deepAgingId"] = str(uuid.uuid4())
    try:
        new_deepAging = DeepAgingInfo(**meat_data)
    except Exception as e:
        raise Exception("Wrong DeepAging DB field items: " + str(e))


def create_SensoryEval(meat_data: dict, seqno: int, id: str, deepAgingId: int):
    """
    db: SQLAlchemy db
    freshmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    freshmeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid Sensory_Evaluate data")
    # 1. freshmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)
    item_encoder(meat_data, "deepAgingId", deepAgingId)
    # 2. freshmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "freshmeatId":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "deepAgingId":
            pass
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_SensoryEval = SensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong sensory eval DB field items" + str(e))
    return new_SensoryEval


def create_HeatemeatSensoryEval(meat_data: dict, seqno: int, id: str):
    """
    db: SQLAlchemy db
    heatedmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    heatedMeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid Heatedmeat Sensory Evaluate data")
    # 1. heatedmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)
    # 2. heatedmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":
            pass
        elif field == "id":
            pass
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_heatedmeat = HeatedmeatSensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong heatedmeat sensory eval DB field items" + str(e))
    return new_heatedmeat


def create_ProbexptData(meat_data: dict, seqno: int, id: str):
    """
    db: SQLAlchemy db
    heatedmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    heatedMeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid Heatedmeat Sensory Evaluate data")
    # 1. heatedmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)
    # 2. heatedmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":
            pass
        elif field == "id":
            pass
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_heatedmeat = HeatedmeatSensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong heatedmeat sensory eval DB field items" + str(e))
    return new_heatedmeat


# API MiddleWare
def create_specific_std_meat_data(db_session, s3_conn, firestore_conn, data):
    id = data.get("id")
    meat = db_session.query(Meat).get(id)
    if meat.statusType == 2:
        raise Exception("No Id in Request Data")
    try:
        # 1. DB merge
        new_meat = create_meat(meat_data=data, db_session=db_session)
        new_meat.statusType = 0
        db_session.merge(new_meat)

        # 2. Firestore -> S3
        transfer_folder_image(
            s3_conn=s3_conn,
            firestore_conn=firestore_conn,
            db_session=db_session,
            id=id,
            new_meat=new_meat,
            folder="qr_codes",
        )
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id), 200


def create_specific_deep_aging_meat_data(db_session, data):
    # 2. 기본 데이터 받아두기
    id = data.get("id")
    seqno = data.get("seqno")
    deepAging_data = data.get("deepAging")
    data.pop("deepAging", None)
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No Id in Request Data")
    sensory_eval = (
        db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).first()
    )  # DB에 있는 육류 정보
    try:
        if deepAging_data is not None:
            if meat:  # 승인 정보 확인
                if meat.statusType != 2:
                    raise Exception("Not Confirmed Meat Data")
            if sensory_eval:  # 기존 Deep Aging을 수정하는 경우
                deepAgingId = sensory_eval.deepAgingId
                existing_DeepAging = db_session.query(DeepAgingInfo).get(deepAgingId)
                if existing_DeepAging:
                    for key, value in deepAging_data.items():
                        setattr(existing_DeepAging, key, value)
                else:
                    raise Exception("No Deep Aging Data found for update")
            else:  # 새로운 Deep aging을 추가하는 경우
                new_DeepAging = create_DeepAging(deepAging_data)
                deepAgingId = new_DeepAging.deepAgingId
                db_session.add(new_DeepAging)
                db_session.commit()
                new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                db_session.merge(new_SensoryEval)
            db_session.commit()
        else:
            raise Exception("No deepaging data in request")
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id), 200


def create_specific_sensoryEval(db_session, s3_conn, firestore_conn, data):
    # 2. 기본 데이터 받아두기
    id = safe_str(data.get("id"))
    seqno = safe_int(data.get("seqno"))
    deepAging_data = data.get("deepAging")
    data.pop("deepAging", None)
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No ID data sent for update")

    sensory_eval = (
        db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).first()
    )  # DB에 있는 육류 정보
    try:
        if seqno != 0:  # 가공육 관능검사
            if sensory_eval:  # 기존 Deep Aging을 수정하는 경우
                deepAgingId = sensory_eval.deepAgingId
                new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                db_session.merge(new_SensoryEval)
            else:  # 새로운 Deep aging을 추가하는 경우
                new_DeepAging = create_DeepAging(deepAging_data)
                deepAgingId = new_DeepAging.deepAgingId
                db_session.add(new_DeepAging)
                db_session.commit()
                new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                db_session.merge(new_SensoryEval)
        else:  # 신선육 관능검사
            if meat:  # 수정하는 경우
                if meat.statusType == 2:
                    raise Exception("Already confirmed meat data")
            deepAgingId = None
            new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
            db_session.merge(new_SensoryEval)
            meat.statusType = 0
            db_session.merge(meat)

        transfer_folder_image(
            s3_conn,
            firestore_conn,
            db_session,
            f"{id}-{seqno}",
            new_SensoryEval,
            "sensory_evals",
        )
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id)


def create_specific_heatedmeat_seonsory_data(db_session, data):
    # 2. 기본 데이터 받아두기
    id = data.get("id")
    seqno = data.get("seqno")
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat:  # 승인 정보 확인
        if meat.statusType != 2:
            raise Exception("Not confirmed meat data")
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No ID data sent for update")
    try:
        new_HeatedmeatSensoryEval = create_HeatemeatSensoryEval(data, seqno, id)
        db_session.merge(new_HeatedmeatSensoryEval)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id)


def create_specific_probexpt_data(db_session, data):
    # 2. 기본 데이터 받아두기
    id = data.get("id")
    seqno = data.get("seqno")
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat:  # 승인 정보 확인
        if meat.statusType != 2:
            raise Exception("Not confirmed meat data")
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No ID data sent for update")
    try:
        new_ProbexptData = create_ProbexptData(data, seqno, id)
        db_session.merge(new_ProbexptData)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id)


# GET
def get_meat(db_session, id):
    # 1. 육류데이터 가져오기
    meat = db_session.query(Meat).filter(Meat.id == id).first()

    if meat is None:
        return None
    result = to_dict(meat)
    sexType = db_session.query(SexInfo).filter(SexInfo.id == result["sexType"]).first()
    gradeNum = (
        db_session.query(GradeInfo).filter(GradeInfo.id == result["gradeNum"]).first()
    )
    statusType = (
        db_session.query(StatusInfo)
        .filter(StatusInfo.id == result["statusType"])
        .first()
    )
    # 이미 있는거 변환
    result["sexType"] = sexType.value
    (
        result["specieValue"],
        result["primalValue"],
        result["secondaryValue"],
    ) = decode_id(result["categoryId"], db_session)
    result["gradeNum"] = gradeNum.value
    result["statusType"] = statusType.value
    result["createdAt"] = convert2string(result["createdAt"], 1)
    result["butcheryYmd"] = convert2string(result["butcheryYmd"], 2)
    result["birthYmd"] = convert2string(result["birthYmd"], 2)

    # 6. freshmeat , heatedmeat, probexpt
    result["rawmeat"] = {
        "sensory_eval": get_SensoryEval(db_session=db_session, id=id, seqno=0),
        "heatedmeat_sensory_eval": get_HeatedmeatSensoryEval(
            db_session=db_session, id=id, seqno=0
        ),
        "probexpt_data": get_ProbexptData(db_session=db_session, id=id, seqno=0),
    }
    sensory_data = (
        db_session.query(SensoryEval)
        .filter_by(id=id)
        .order_by(SensoryEval.seqno.desc())
        .first()
    )  # DB에 있는 육류 정보
    if sensory_data:
        N = sensory_data.seqno
    else:
        N = 0

    result["processedmeat"] = {
        f"{i}회": {
            "sensory_eval": {},
            "heatedmeat_sensory_eval": {},
            "probexpt_data": {},
        }
        for i in range(1, N + 1)
    }
    for index in range(1, N + 1):
        result["processedmeat"][f"{index}회"]["sensory_eval"] = get_SensoryEval(
            db_session, id, index
        )
        result["processedmeat"][f"{index}회"][
            "heatedmeat_sensory_eval"
        ] = get_HeatedmeatSensoryEval(db_session, id, index)
        result["processedmeat"][f"{index}회"]["probexpt_data"] = get_ProbexptData(
            db_session, id, index
        )

    # remove field
    del result["categoryId"]
    return result


def get_SensoryEval(db_session, id, seqno):
    sensoryEval_data = (
        db_session.query(SensoryEval)
        .filter(
            SensoryEval.id == id,
            SensoryEval.seqno == seqno,
        )
        .first()
    )
    if sensoryEval_data:
        sensoryEval = to_dict(sensoryEval_data)
        sensoryEval["createdAt"] = convert2string(sensoryEval["createdAt"], 1)
        if seqno != 0:  # 가공육인 경우
            sensoryEval["deepaging_data"] = get_DeepAging(
                db_session, sensoryEval["deepAgingId"]
            )
            del sensoryEval["deepAgingId"]
        return sensoryEval
    else:
        return None


def get_DeepAging(db_session, id):
    deepAging_data = (
        db_session.query(DeepAgingInfo)
        .filter(
            DeepAgingInfo.deepAgingId == id,
        )
        .first()
    )
    if deepAging_data:
        deepAging_history = to_dict(deepAging_data)
        deepAging_history["date"] = convert2string(deepAging_history.get("date"), 2)
        return deepAging_history
    else:
        return None


def get_HeatedmeatSensoryEval(db_session, id, seqno):
    heated_meat = (
        db_session.query(HeatedmeatSensoryEval)
        .filter(
            HeatedmeatSensoryEval.id == id,
            HeatedmeatSensoryEval.seqno == seqno,
        )
        .first()
    )
    if heated_meat:
        heated_meat_history = to_dict(heated_meat)
        heated_meat_history["createdAt"] = convert2string(
            heated_meat_history["createdAt"], 1
        )
        del heated_meat_history["imagePath"]
        return heated_meat_history
    else:
        return None


def get_ProbexptData(db_session, id, seqno):
    probexpt = (
        db_session.query(ProbexptData)
        .filter(
            ProbexptData.id == id,
            ProbexptData.seqno == seqno,
        )
        .first()
    )
    if probexpt:
        probexpt_history = to_dict(probexpt)
        probexpt_history["updatedAt"] = convert2string(probexpt_history["updatedAt"], 1)
        return probexpt_history
    else:
        return None


def get_range_meat_data(
    db_session,
    offset,
    count,
    start=None,
    end=None,
    farmAddr=None,
    userId=None,
    type=None,
    createdAt=None,
    statusType=None,
    company=None,
):
    offset = safe_int(offset)
    count = safe_int(count)
    start = convert2datetime(start, 1)
    end = convert2datetime(end, 1)
    # Base Query
    query = db_session.query(Meat).join(
        User, User.userId == Meat.userId
    )  # Join with User

    # Sorting and Filtering
    if farmAddr is not None:
        if farmAddr:  # true: 가나다순 정렬
            query = query.order_by(Meat.farmAddr.asc())
        else:  # false: 역순
            query = query.order_by(Meat.farmAddr.desc())
    if userId is not None:
        if userId:  # true: 알파벳 오름차순 정렬
            query = query.order_by(Meat.userId.asc())
        else:  # false: 알파벳 내림차순 정렬
            query = query.order_by(Meat.userId.desc())
    if type is not None:
        if type:  # true: 숫자 오름차순 정렬
            query = query.order_by(User.type.asc())
        else:  # false: 숫자 내림차순 정렬
            query = query.order_by(User.type.desc())
    if company is not None:
        if company:  # true: 가나다순 정렬
            query = query.order_by(User.company.asc())
        else:  # false: 역순
            query = query.order_by(User.company.desc())
    if createdAt is not None:
        if createdAt:  # true: 최신순
            query = query.order_by(Meat.createdAt.desc())
        else:  # false: 역순
            query = query.order_by(Meat.createdAt.asc())
    if statusType is not None:
        if statusType:  # true: 숫자 오름차순 정렬
            query = query.order_by(Meat.statusType.asc())
        else:  # false: 숫자 내림차순 정렬
            query = query.order_by(Meat.statusType.desc())

    # 기간 설정 쿼리
    db_total_len = db_session.query(Meat).count()
    if start is not None and end is not None:
        query = query.filter(Meat.createdAt.between(start, end))
        db_total_len = db_session.query.filter(Meat.createdAt.between(start,end)).count()
    query = query.offset(offset * count).limit(count)

    # 탐색
    meat_data = query.all()
    meat_result = {}
    id_result = [data.id for data in meat_data]
    for id in id_result:
        meat_result[id] = get_meat(db_session, id)
        userTemp = get_user(db_session, meat_result[id].get("userId"))
        if userTemp:
            meat_result[id]["name"] = userTemp.get("name")
            meat_result[id]["company"] = userTemp.get("company")
            meat_result[id]["type"] = userTemp.get("type")
        else:
            meat_result[id]["name"] = userTemp
            meat_result[id]["company"] = userTemp
            meat_result[id]["type"] = userTemp
        del meat_result[id]["processedmeat"]
        del meat_result[id]["rawmeat"]

    result = {
        "DB Total len": db_total_len,
        "id_list": id_result,
        "meat_dict": meat_result,
    }

    return jsonify(result)


# UPDATE

# DELETE


# USER
def create_user(db_session, user_data: dict):
    try:
        for field, value in user_data.items():
            if field == "password":
                item_encoder(
                    user_data, field, hashlib.sha256(value.encode()).hexdigest()
                )
            elif field == "type":
                user_type = db_session.query(UserTypeInfo).filter_by(name=value).first()
                if user_type:  # check if user_type exists
                    item_encoder(user_data, field, user_type.id)
                else:
                    item_encoder(user_data, field, 3)
            else:
                item_encoder(user_data, field)
        new_user = User(**user_data)
        return new_user
    except Exception as e:
        raise Exception(str(e))


def update_user(db_session, user_data: dict):
    try:
        history = (
            db_session.query(User).filter_by(userId=user_data.get("userId")).first()
        )
        # 1. 기존 유저 없음
        if history == None:
            raise Exception(f"No User ID {user_data.get('userId')}")

        # 2. 기존 유저 있음
        for field, value in user_data.items():
            if field == "password":
                item_encoder(
                    user_data, field, hashlib.sha256(value.encode()).hexdigest()
                )
            elif field == "type":
                user_type = db_session.query(UserTypeInfo).filter_by(name=value).first()
                if user_type:  # check if user_type exists
                    item_encoder(user_data, field, user_type.id)
                else:
                    item_encoder(user_data, field, 3)

            else:
                item_encoder(user_data, field)

        for attr, value in user_data.items():
            setattr(history, attr, value)
        return history

    except Exception as e:
        raise Exception(str(e))


def get_user(db_session, userId):
    try:
        userData = db_session.query(User).filter(User.userId == userId).first()
        userData_dict = to_dict(userData)
        userData_dict["createdAt"] = convert2string(userData_dict.get("createdAt"), 1)
        userData_dict["updatedAt"] = convert2string(userData_dict.get("updatedAt"), 1)
        userData_dict["loginAt"] = convert2string(userData_dict.get("loginAt"), 1)
        userData_dict["type"] = (
            db_session.query(UserTypeInfo)
            .filter(UserTypeInfo.id == userData_dict.get("type"))
            .first()
            .name
        )
        return userData_dict

    except Exception as e:
        raise Exception(str(e))


def _get_users_by_type(db_session):
    try:
        # UserType 별로 분류될 유저 정보를 담을 딕셔너리
        user_dict = {}

        # 모든 유저 정보를 조회
        users = db_session.query(User).all()

        # 조회된 유저들에 대하여
        for user in users:
            # 해당 유저의 UserType을 조회
            user_type = UserTypeInfo.query.get(user.type).name

            # user_dict에 해당 UserType key가 없다면, 새로운 리스트 생성
            if user_type not in user_dict:
                user_dict[user_type] = []

            # UserType에 해당하는 key의 value 리스트에 유저 id 추가
            user_dict[user_type].append(user.userId)

        return user_dict
    except Exception as e:
        raise Exception(str(e))


def _getMeatDataByUserId(db_session, userId):
    meats = db_session.query(Meat).filter_by(userId=userId).all()
    if meats:
        result = []
        for meat in meats:
            temp = get_meat(db_session, meat.id)
            del temp["processedmeat"]
            del temp["rawmeat"]
            result.append(temp)
        return jsonify(result), 200
    else:
        return jsonify({"message": "No meats found for the given userId."}), 404


def _getMeatDataByUserType(db_session, userType):
    userType_value = db_session.query(UserTypeInfo).filter_by(name=userType).first()
    if userType_value:
        userType = userType_value.id
    else:
        return (
            jsonify({"msg": "No userType in DB  (Normal, Researcher, Manager, None)"}),
            404,
        )

    # First, get all users of the given user type
    users = db_session.query(User).filter_by(type=userType).all()
    user_ids = [user.userId for user in users]

    # Then, get all meats that were created by the users of the given user type
    meats = Meat.query.filter(Meat.userId.in_(user_ids)).all()

    if meats:
        result = []
        for meat in meats:
            temp = get_meat(db_session, meat.id)
            userTemp = get_user(db_session, temp.get("userId"))
            if userTemp:
                temp["name"] = userTemp.get("name")
            else:
                temp["name"] = userTemp
            del temp["processedmeat"]
            del temp["rawmeat"]
            result.append(temp)
        return jsonify(result), 200
    else:
        return (
            jsonify({"message": "No meats found for the given userType."}),
            404,
        )


def _getMeatDataByStatusType(db_session, varified):
    meats_db = Meat.query.all()
    meat_list = []
    if varified == 2:  # 승인
        varified = "승인"
    elif varified == 1:  # 반려
        varified = "반려"
    elif varified == 0:
        varified = "대기중"
    for meat in meats_db:
        temp = get_meat(db_session, meat.id)
        del temp["processedmeat"]
        del temp["rawmeat"]
        if temp.get("statusType") == varified:
            meat_list.append(temp)
    return jsonify({f"{varified}": meat_list}), 200


def _getMeatDataByRangeStatusType(
    db_session, varified, offset, count, start=None, end=None
):
    # Base query
    query = (
        db_session.query(Meat)
        .options()
        .filter_by(statusType=varified)
        .order_by(Meat.createdAt.desc())
    )

    # Date Filter
    if start is not None and end is not None:
        query = query.filter(Meat.createdAt.between(start, end))

    query = query.offset(offset * count).limit(count)

    result = []
    meat_data = query.all()

    for meat in meat_data:
        temp = get_meat(db_session, meat.id)
        userTemp = get_user(db_session, temp.get("userId"))
        if userTemp:
            temp["name"] = userTemp.get("name")
            temp["company"] = userTemp.get("company")
            temp["type"] = userTemp.get("type")
        else:
            temp["name"] = userTemp
            temp["company"] = userTemp
            temp["type"] = userTemp
        del temp["processedmeat"]
        del temp["rawmeat"]
        result.append(temp)
    varified_id = varified
    if varified == 2:
        varified = "승인"
    elif varified == 1:
        varified = "반려"
    else:
        varified = "대기중"
    return (
        jsonify(
            {
                "DB Total len": db_session.query(Meat)
                .filter_by(statusType=varified_id)
                .count(),
                f"{varified}": result,
            }
        ),
        200,
    )


def _getMeatDataByTotalStatusType(db_session):
    result = {}
    result["승인"] = _getMeatDataByStatusType("2")[0].get_json().get("승인")
    result["반려"] = _getMeatDataByStatusType("1")[0].get_json().get("반려")
    result["대기중"] = _getMeatDataByStatusType("0")[0].get_json().get("대기중")
    return jsonify(result), 200


def _getTexanomyData(db_session):
    species_all = db_session.query(SpeciesInfo).all()
    result = {}
    for species in species_all:
        # Use joinedload to avoid N+1 problem
        categories = (
            db_session.query(CategoryInfo)
            .options(joinedload(CategoryInfo.meats))
            .filter_by(speciesId=species.id)
            .all()
        )
        category_dict = {}
        for category in categories:
            if category.primalValue not in category_dict:
                category_dict[category.primalValue] = [category.secondaryValue]
            else:
                category_dict[category.primalValue].append(category.secondaryValue)

        result[species.value] = category_dict
    return jsonify(result), 200


def _getPredictionData(db_session, id, seqno):
    result = get_AI_SensoryEval(db_session, id, seqno)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"msg": "No data in AI Sensory Evaluate DB"}), 404


def get_AI_SensoryEval(db_session, id, seqno):
    ai_sensoryEval = (
        db_session.query(AI_SensoryEval)
        .filter(
            AI_SensoryEval.id == id,
            AI_SensoryEval.seqno == seqno,
        )
        .first()
    )
    if ai_sensoryEval:
        ai_sensoryEval_history = to_dict(ai_sensoryEval)
        ai_sensoryEval_history["createdAt"] = convert2string(
            ai_sensoryEval_history["createdAt"], 1
        )
        return ai_sensoryEval_history
    else:
        return None


def _updateConfirmData(db_session, id):
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat:
        meat.statusType = 2
        db_session.merge(meat)
        db_session.commit()
        return jsonify(id), 200
    else:
        return jsonify({"msg": "No Data In Meat DB"}), 404


def _updateRejectData(db_session, id):
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat:
        meat.statusType = 1
        db_session.merge(meat)
        db_session.commit()
        return jsonify(id), 200
    else:
        return jsonify({"msg": "No Data In Meat DB"}), 404


def _addSpecificPredictData(db_session, data):
    id = data.get("id")
    seqno = data.get("seqno")
    # Find SensoryEval data
    sensory_eval = db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).first()

    # If no SensoryEval found, abort
    if not sensory_eval:
        return jsonify({"msg": "No Sensory Eval Data In DB"}), 404

    # Call 2nd team's API
    response = requests.post(
        f"{os.getenv('ML_server_base_url')}/predict",
        data=json.dumps({"image_path": sensory_eval.imagePath}),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    # If the response was unsuccessful, abort
    if response.status_code != 200:
        return jsonify({"msg": "Failed To Get Response From Prediction Server"}), 404

    # Decode the response data
    response_data = response.json()
    # Merge the response data with the existing data
    data.update(response_data)

    # Change the key name from 'gradeNum' to 'xai_gradeNum'
    if "gradeNum" in data:
        data["xai_gradeNum"] = data.pop("gradeNum")
    data["createdAt"] = ""
    try:
        # Create a new SensoryEval
        new_sensory_eval = create_AI_SensoryEval(db_session, data, seqno, id)

        # Add new_sensory_eval to the session
        db_session.merge(new_sensory_eval)

        # Commit the session to save the changes
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    # Return the new data
    return jsonify(data), 200
    # 의문점1 : 이거 시간 오바 안 뜨려나?
    # 의문점2 : 로딩창 안 뜨나


def create_AI_SensoryEval(db_session, meat_data: dict, seqno: int, id: str):
    """
    db: SQLAlchemy db
    freshmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    freshmeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid AI_Sensory_Evaluate data")
    # 2. Get the ID of the record in the GradeNum table
    xai_grade_num = (
        db_session.query(GradeInfo)
        .filter_by(value=meat_data.get("xai_gradeNum"))
        .first()
    )
    # 1. freshmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)

    # 2. freshmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "id":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "xai_gradeNum":
            try:
                item_encoder(meat_data, field, xai_grade_num.id)
            except Exception as e:
                raise Exception("Invalid xai_grade_num id")
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_SensoryEval = AI_SensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong AI sensory eval DB field items" + str(e))
    return new_SensoryEval


def _deleteSpecificMeatData(db_session, s3_conn, firebase_conn, id):
    # 1. 육류 DB 체크
    meat = db_session.query(Meat).get(id)

    if meat is None:
        return jsonify({"msg": f"No meat data found with the given ID: {id}"}), 404
    try:
        sensory_evals = db_session.query(SensoryEval).filter_by(id=id).all()
        heatedmeat_evals = (
            db_session.query(HeatedmeatSensoryEval).filter_by(id=id).all()
        )
        probexpt_datas = db_session.query(ProbexptData).filter_by(id=id).all()
        # 가열육 데이터 삭제
        for heatedmeat_eval in heatedmeat_evals:
            seqno = heatedmeat_eval.seqno
            db_session.delete(heatedmeat_eval)
            s3_conn.delete_image("heatedmeat_sensory_evals", f"{id}-{seqno}")
            db_session.commit()

        # 실험 데이터 삭제
        for probexpt_data in probexpt_datas:
            db_session.delete(probexpt_data)
        db_session.commit()

        # 관능 데이터 삭제 및 관능 이미지 삭제
        for sensory_eval in sensory_evals:
            seqno = sensory_eval.seqno
            db_session.delete(sensory_eval)
            s3_conn.delete_image("sensory_evals", f"{id}-{seqno}")
            db_session.commit()

        # 육류 데이터 삭제
        db_session.delete(meat)

        # 큐알 삭제
        s3_conn.delete_image("qr_codes", f"{id}")
        db_session.commit()
        return jsonify({"delete Id": id}), 200
    except Exception as e:
        db_session.rollback()
        raise e


def _deleteSpecificDeepAgingData(db_session, s3_conn, firebase_conn, id, seqno):
    # 1. 육류 DB 체크
    meat = db_session.query(Meat).get(id)

    if meat is None:
        return jsonify({"msg": f"No meat data found with the given ID: {id}"}), 404
    try:
        sensory_evals = (
            db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).all()
        )
        heatedmeat_evals = (
            db_session.query(HeatedmeatSensoryEval).filter_by(id=id, seqno=seqno).all()
        )
        probexpt_datas = (
            db_session.query(ProbexptData).filter_by(id=id, seqno=seqno).all()
        )
        for heatedmeat_eval in heatedmeat_evals:
            db_session.delete(heatedmeat_eval)
            s3_conn.delete_image("heatedmeat_sensory_evals", f"{id}-{seqno}")
            db_session.commit()

        for probexpt_data in probexpt_datas:
            db_session.delete(probexpt_data)
        db_session.commit()

        for sensory_eval in sensory_evals:
            db_session.delete(sensory_eval)
            s3_conn.delete_image("sensory_evals", f"{id}-{seqno}")
            db_session.commit()
        return jsonify({"delete Id": id, "delete Seqno": seqno}), 200
    except Exception as e:
        db_session.rollback()
        return e


def get_num_of_processed_raw(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # Subquery to find meats which have processed data
    processed_meats_subquery = (
        db_session.query(Meat.id)
        .join(SensoryEval)
        .filter(SensoryEval.seqno > 0)
        .subquery()
    )
    processed_meats_select = processed_meats_subquery.select()

    # 1. Category.specieId가 0이면서 SensoryEval.seqno 값이 0인 데이터, 1인 데이터
    fresh_cattle_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 0,
            ~Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    processed_cattle_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 0,
            Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )

    # 2. Category.specieId가 1이면서 SensoryEval.seqno 값이 0인 데이터, 1인 데이터
    fresh_pig_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 1,
            ~Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    processed_pig_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 1,
            Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )

    # 3. 전체 데이터에서 SensoryEval.seqno 값이 0인 데이터, 1인 데이터
    fresh_meat_count = Meat.query.filter(
        ~Meat.id.in_(processed_meats_select),
        Meat.createdAt.between(start, end),
        Meat.statusType == 2,
    ).count()

    processed_meat_count = Meat.query.filter(
        Meat.id.in_(processed_meats_select),
        Meat.createdAt.between(start, end),
        Meat.statusType == 2,
    ).count()

    # Returning the counts in JSON format
    return (
        jsonify(
            {
                "cattle_counts": {
                    "raw": fresh_cattle_count,
                    "processed": processed_cattle_count,
                },
                "pig_counts": {
                    "raw": fresh_pig_count,
                    "processed": processed_pig_count,
                },
                "total_counts": {
                    "raw": fresh_meat_count,
                    "processed": processed_meat_count,
                },
            }
        ),
        200,
    )


def get_num_of_cattle_pig(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    cow_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 0,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    pig_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 1,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    return jsonify({"cattle_count": cow_count, "pig_count": pig_count}), 200


def get_num_of_primal_part(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404
    # 1. Category.specieId가 0일때 해당 Category.primalValue 별로 육류의 개수를 추출
    count_by_primal_value_beef = (
        db_session.query(CategoryInfo.primalValue, func.count(Meat.id))
        .join(Meat, Meat.categoryId == CategoryInfo.id)
        .filter(
            CategoryInfo.speciesId == 0,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .group_by(CategoryInfo.primalValue)
        .all()
    )

    # 2. Category.specieId가 1일때 해당 Category.primalValue 별로 육류의 개수를 추출
    count_by_primal_value_pork = (
        db_session.query(CategoryInfo.primalValue, func.count(Meat.id))
        .join(Meat, Meat.categoryId == CategoryInfo.id)
        .filter(
            CategoryInfo.speciesId == 1,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .group_by(CategoryInfo.primalValue)
        .all()
    )

    # Returning the counts in JSON format
    return (
        jsonify(
            {
                "beef_counts_by_primal_value": dict(count_by_primal_value_beef),
                "pork_counts_by_primal_value": dict(count_by_primal_value_pork),
            }
        ),
        200,
    )


def get_num_by_farmAddr(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404
    regions = [
        "강원",
        "경기",
        "경남",
        "경북",
        "광주",
        "대구",
        "대전",
        "부산",
        "서울",
        "세종",
        "울산",
        "인천",
        "전남",
        "전북",
        "제주",
        "충남",
        "충북",
    ]
    result = {}

    for speciesId in [0, 1]:  # 0 for cattle, 1 for pig
        region_counts = {}
        for region in regions:
            region_like = "%".join(list(region))
            count = (
                db_session.query(Meat)
                .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
                .filter(
                    CategoryInfo.speciesId == speciesId,
                    Meat.farmAddr.like(f"%{region_like}%"),
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .count()
            )
            region_counts[region] = count
        if speciesId == 0:
            result["cattle_counts_by_region"] = region_counts
        else:
            result["pig_counts_by_region"] = region_counts

    # For total data
    total_region_counts = {}
    for region in regions:
        count = (
            db_session.query(Meat)
            .filter(
                Meat.farmAddr.like(f"%{region}%"),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .count()
        )
        total_region_counts[region] = count
    result["total_counts_by_region"] = total_region_counts

    return jsonify(result), 200


def get_probexpt_of_rawmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404
    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["sourness", "bitterness", "umami", "richness"]:
        avg = (
            db_session.query(func.avg(getattr(ProbexptData, field)))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        max_value = (
            db_session.query(func.max(getattr(ProbexptData, field)))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        min_value = (
            db_session.query(func.min(getattr(ProbexptData, field)))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )

        # 실제로 존재하는 값들 찾기
        unique_values_query = (
            db_session.query(getattr(ProbexptData, field))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .distinct()
        )
        unique_values = [value[0] for value in unique_values_query.all()]

        stats[field] = {
            "avg": avg,
            "max": max_value,
            "min": min_value,
            "unique_values": unique_values,
        }

    return jsonify(stats)


def get_probexpt_of_processedmeat(db_session, seqno, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    seqno = safe_int(seqno)
    if seqno:
        for field in ["sourness", "bitterness", "umami", "richness"]:
            avg = (
                db_session.query(func.avg(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(ProbexptData, field))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [value[0] for value in unique_values_query.all()]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": unique_values,
            }
    else:
        for field in ["sourness", "bitterness", "umami", "richness"]:
            avg = (
                db_session.query(func.avg(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(ProbexptData, field))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [value[0] for value in unique_values_query.all()]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": unique_values,
            }

    return jsonify(stats)


def get_sensory_of_rawmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
        avg = (
            db_session.query(func.avg(getattr(SensoryEval, field)))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        max_value = (
            db_session.query(func.max(getattr(SensoryEval, field)))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        min_value = (
            db_session.query(func.min(getattr(SensoryEval, field)))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )

        # 실제로 존재하는 값들 찾기
        unique_values_query = (
            db_session.query(getattr(SensoryEval, field))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .distinct()
        )
        unique_values = [value[0] for value in unique_values_query.all()]

        stats[field] = {
            "avg": avg,
            "max": max_value,
            "min": min_value,
            "unique_values": sorted(unique_values),
        }

    return jsonify(stats)


def get_sensory_of_processedmeat(db_session, seqno, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    stats = {}
    seqno = safe_int(seqno)
    if seqno:
        # 각 필드의 평균값, 최대값, 최소값 계산
        for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
            avg = (
                db_session.query(func.avg(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(SensoryEval, field))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [
                value[0] for value in unique_values_query.all() if value[0] is not None
            ]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": sorted(unique_values)
                if unique_values
                else unique_values,
            }
    else:
        # 각 필드의 평균값, 최대값, 최소값 계산
        for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
            avg = (
                db_session.query(func.avg(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(SensoryEval, field))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [
                value[0] for value in unique_values_query.all() if value[0] is not None
            ]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": sorted(unique_values),
            }

    return jsonify(stats)


def get_sensory_of_raw_heatedmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["flavor", "juiciness", "tenderness", "umami", "palability"]:
        avg = (
            db_session.query(func.avg(getattr(HeatedmeatSensoryEval, field)))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        max_value = (
            db_session.query(func.max(getattr(HeatedmeatSensoryEval, field)))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        min_value = (
            db_session.query(func.min(getattr(HeatedmeatSensoryEval, field)))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )

        # 실제로 존재하는 값들 찾기
        unique_values_query = (
            db_session.query(getattr(HeatedmeatSensoryEval, field))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .distinct()
        )
        unique_values = [
            value[0] for value in unique_values_query.all() if value[0] is not None
        ]

        stats[field] = {
            "avg": avg,
            "max": max_value,
            "min": min_value,
            "unique_values": sorted(unique_values),
        }

    return jsonify(stats)

def get_sensory_of_processed_heatedmeat(db_session,seqno, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    seqno = safe_int(seqno)
    if seqno:
        for field in ["flavor", "juiciness", "tenderness", "umami", "palability"]:
            avg = (
                db_session.query(
                    func.avg(getattr(HeatedmeatSensoryEval, field))
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(
                    func.max(getattr(HeatedmeatSensoryEval, field))
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(
                    func.min(
                        getattr(HeatedmeatSensoryEval, field),
                        Meat.createdAt.between(start, end),
                        Meat.statusType == 2,
                    )
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(HeatedmeatSensoryEval.seqno == seqno)
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(HeatedmeatSensoryEval, field))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [
                value[0]
                for value in unique_values_query.all()
                if value[0] is not None
            ]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": sorted(unique_values),
            }
    else:
        for field in ["flavor", "juiciness", "tenderness", "umami", "palability"]:
            avg = (
                db_session.query(
                    func.avg(getattr(HeatedmeatSensoryEval, field))
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(
                    func.max(getattr(HeatedmeatSensoryEval, field))
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(
                    func.min(getattr(HeatedmeatSensoryEval, field))
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(HeatedmeatSensoryEval, field))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [
                value[0]
                for value in unique_values_query.all()
                if value[0] is not None
            ]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": sorted(unique_values),
            }

    return jsonify(stats)

def get_probexpt_of_processed_heatedmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # Get all SensoryEval records
    sensory_evals = (
        SensoryEval.query.join(Meat, Meat.id == SensoryEval.id)
        .filter(
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .order_by(SensoryEval.id, SensoryEval.seqno)
        .all()
    )

    result = {}

    # Keep track of the accumulated minutes for each id
    accumulated_minutes = {}

    for sensory_eval in sensory_evals:
        deep_aging = db_session.query(DeepAgingInfo).filter_by(
            deepAgingId=sensory_eval.deepAgingId
        ).first()

        # If no matching DeepAging record was found, skip this SensoryEval

        # Get the corresponding ProbexptData record
        probexpt_data = ProbexptData.query.filter_by(
            id=sensory_eval.id, seqno=sensory_eval.seqno
        ).first()

        # If no matching ProbexptData record was found, skip this SensoryEval
        if not probexpt_data:
            continue

        # Create a dictionary of ProbexptData fields
        probexpt_data_dict = {
            "sourness": probexpt_data.sourness,
            "bitterness": probexpt_data.bitterness,
            "umami": probexpt_data.umami,
            "richness": probexpt_data.richness,
        }

        # If the seqno is 0, set the minute to 0, otherwise, add the current DeepAging minute to the accumulated minutes
        if sensory_eval.seqno == 0:
            accumulated_minutes[sensory_eval.id] = 0
        else:
            # If the id is not yet in the accumulated_minutes dictionary, initialize it to the current minute
            if sensory_eval.id not in accumulated_minutes:
                accumulated_minutes[sensory_eval.id] = deep_aging.minute
            else:
                accumulated_minutes[sensory_eval.id] += deep_aging.minute

        # Add the ProbexptData fields to the result under the accumulated minutes
        if accumulated_minutes[sensory_eval.id] not in result:
            result[accumulated_minutes[sensory_eval.id]] = {}

        result[accumulated_minutes[sensory_eval.id]][
            f"({sensory_eval.id},{sensory_eval.seqno})"
        ] = probexpt_data_dict

    return result
