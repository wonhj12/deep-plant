# DB Model Config File
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Sequence,
    Float,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
    Boolean,
    CheckConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from utils import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


# Texonomy Table
class SpeciesInfo(Base):
    __tablename__ = "species_info"
    id = Column(Integer, primary_key=True)  # 종 ID
    value = Column(String(255))  # 종명(ex. cattle, pig)
    categories = relationship("CategoryInfo", backref="species_info")


class CategoryInfo(Base):
    __tablename__ = "category_info"
    id = Column(Integer, primary_key=True)  # 카테고리 ID
    speciesId = Column(Integer, ForeignKey("species_info.id"))
    primalValue = Column(String(255), nullable=False)
    secondaryValue = Column(String(255), nullable=False)
    meats = relationship("Meat", backref="category_info")


class GradeInfo(Base):
    """
    0: 1++
    1: 1+
    2: 1
    3: 2
    4: 3
    5: None(Null)
    """

    __tablename__ = "grade_info"
    id = Column(Integer, primary_key=True)  # 등급 ID
    value = Column(String(255))  # 등급


class SexInfo(Base):
    """
    0: 수
    1: 암
    2: 거세
    3: null
    """

    __tablename__ = "sex_info"
    id = Column(Integer, primary_key=True)  # 성별 ID
    value = Column(String(255))  # 성별 값


class StatusInfo(Base):
    """
    0: 대기중
    1: 반려
    2: 승인
    """

    __tablename__ = "status_info"
    id = Column(Integer, primary_key=True)  # 승인 ID
    value = Column(String(255))  # 승인 정보


class UserTypeInfo(Base):
    """
    0: Normal
    1: Researcher
    2: Manager
    3: None
    """

    __tablename__ = "userType_info"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class DeepAgingInfo(Base):
    __tablename__ = "deepAging_info"
    # 1. 기본키
    deepAgingId = Column(String(255), primary_key=True)

    # 2. 딥에이징 데이터
    date = Column(DateTime, nullable=False)  # 딥에이징 실시 날짜
    minute = Column(Integer, nullable=False)  # 딥에이징 진행 시간 (분)


# Main Table


class User(Base):
    __tablename__ = "user"
    userId = Column(String(255), primary_key=True)  # 유저 ID(이메일)
    createdAt = Column(DateTime, nullable=False)  # 유저 ID 생성 시간
    updatedAt = Column(DateTime)  # 유저 정보 최근 수정 시간
    loginAt = Column(DateTime)  # 유저 로그인 시간
    password = Column(String(255), nullable=False)  # 유저 비밀번호(해시화)
    name = Column(String(255), nullable=False)  # 유저명
    company = Column(String(255))  # 직장명
    jobTitle = Column(String(255))  # 직위명
    homeAddr = Column(String(255))  # 유저 주소
    alarm = Column(Boolean, default=False)  # 유저 알람 허용 여부
    type = Column(Integer, ForeignKey("userType_info.id"), nullable=False)  # 유저 타입 ID


class Meat(Base):
    __tablename__ = "meat"
    # 1. 기본 정보
    id = Column(String(255), primary_key=True)  # 육류 관리번호
    userId = Column(String(255), ForeignKey("user.userId"), nullable=False)  # 생성한 유저 ID
    sexType = Column(Integer, ForeignKey("sex_info.id"))  # 성별 ID
    categoryId = Column(
        Integer, ForeignKey("category_info.id"), nullable=False
    )  # 육종 ID
    gradeNum = Column(Integer, ForeignKey("grade_info.id"))  # 등급 ID
    statusType = Column(Integer, ForeignKey("status_info.id"), default=0)  # 승인 여부 ID

    # 2. 육류 Open API 정보
    createdAt = Column(DateTime, nullable=False)  # 육류 관리번호 생성 시간
    traceNum = Column(String(255), nullable=False)  # 이력번호(혹은 묶은 번호)
    farmAddr = Column(String(255))  # 농장 주소
    farmerNm = Column(String(255))  # 농장주 이름
    butcheryYmd = Column(DateTime, nullable=False)  # 도축 일자
    birthYmd = Column(DateTime)  # 출생일자

    # 3. 이미지 Path
    imagePath = Column(String(255))  # QR 이미지 S3 경로


class SensoryEval(Base):  # Assuming Base is defined and imported appropriately
    __tablename__ = "sensory_eval"

    # 1. 복합키 설정
    id = Column(
        String(255),
        ForeignKey("meat.id"),
        primary_key=True,
    )  # 육류 관리번호
    seqno = Column(Integer, primary_key=True)  # 가공 횟수
    __table_args__ = (PrimaryKeyConstraint("id", "seqno"),)

    # 2. 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)  # 관능검사 생성 시간
    userId = Column(
        String(255), ForeignKey("user.userId"), nullable=False
    )  # 관능검사 생성한 유저 ID
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    imagePath = Column(String(255))  # 관능검사 이미지 경로
    deepAgingId = Column(
        String(255), ForeignKey("deepAging_info.deepAgingId")
    )  # 원육이면 null, 가공육이면 해당 딥에이징 정보 ID

    # 3. 관능검사 측정 데이터
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)


class AI_SensoryEval(Base):
    __tablename__ = "ai_sensory_eval"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], ["sensory_eval.id", "sensory_eval.seqno"]
        ),
    )

    # 2. AI 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    userId = Column(String(255), ForeignKey("user.userId"), nullable=False)
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    xai_imagePath = Column(String(255))  # 예측 관능검사 이미지 경로
    xai_gradeNum = Column(Integer, ForeignKey("grade_info.id"))  # 예측 등급
    xai_gradeNum_imagePath = Column(String(255))  # 예측 등급 image path

    # 3. 관능검사 AI 예측 데이터
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)


class HeatedmeatSensoryEval(Base):
    __tablename__ = "heatedmeat_sensory_eval"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], ["sensory_eval.id", "sensory_eval.seqno"]
        ),
    )

    # 2. 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    userId = Column(String(255), ForeignKey("user.userId"), nullable=False)
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    imagePath = Column(String(255))  # 가열육 관능검사 이미지 경로

    # 3. 관능검사 측정 데이터
    flavor = Column(Float)
    juiciness = Column(Float)
    tenderness = Column(Float)
    umami = Column(Float)
    palability = Column(Float)


class AI_HeatedmeatSeonsoryEval(Base):
    __tablename__ = "ai_heatedmeat_sensory_eval"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], ["sensory_eval.id", "sensory_eval.seqno"]
        ),
    )

    # 2. AI 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    userId = Column(String(255), ForeignKey("user.userId"), nullable=False)
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    imagePath = Column(String(255))  # 가열육 관능검사 이미지 경로
    xai_imagePath = Column(String(255))  # 예측 관능검사 이미지 경로

    # 3. 관능검사 AI 예측 데이터
    flavor = Column(Float)
    juiciness = Column(Float)
    tenderness = Column(Float)
    umami = Column(Float)
    palability = Column(Float)


class ProbexptData(Base):
    __tablename__ = "probexpt_data"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], ["sensory_eval.id", "sensory_eval.seqno"]
        ),
        CheckConstraint('0 <= "DL" AND "DL" <= 100', name="check_DL_percentage"),
        CheckConstraint('0 <= "CL" AND "CL" <= 100', name="check_CL_percentage"),
        CheckConstraint('0 <= "RW" AND "RW" <= 100', name="check_RW_percentage"),
    )

    # 2. 연구실 메타 데이터
    updatedAt = Column(DateTime, nullable=False)
    userId = Column(String(255), ForeignKey("user.userId"), nullable=False)
    period = Column(Integer, nullable=False)

    # 3. 실험 데이터
    L = Column(Float)
    a = Column(Float)
    b = Column(Float)
    DL = Column(Float)
    CL = Column(Float)
    RW = Column(Float)
    ph = Column(Float)
    WBSF = Column(Float)
    cardepsin_activity = Column(Float)
    MFI = Column(Float)
    Collagen = Column(Float)

    # 4. 전자혀 데이터
    sourness = Column(Float)
    bitterness = Column(Float)
    umami = Column(Float)
    richness = Column(Float)
