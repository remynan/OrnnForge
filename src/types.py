from datetime import datetime
from typing import List, Optional, Union, Annotated, Any
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator


# 定义 ObjectId 转换函数
def convert_objectid(v):
    if isinstance(v, ObjectId):
        return str(v)
    return v

# 在字段中使用
ObjectIdStr = Annotated[str, BeforeValidator(convert_objectid)]

def parse_datetime(v: datetime) -> str:
    if isinstance(v, str):
        return v.replace('Z', '').replace('T', '')
    elif isinstance(v, datetime):
        # 处理 ISO 格式
        datetime_str = v.strftime('%Y-%m-%d %H:%M:%S')
        return datetime_str
    raise ValueError(f"无法解析时间格式: {v}")

DateTimeField = Annotated[str, BeforeValidator(parse_datetime)]


class FormForCreationGenerate(BaseModel):
    html: str
    type: str
    idea: str


class ResultForCreationGenerate(BaseModel):
    to: str
    content: str

class CreationItem(BaseModel):
    _id: str
    source: str
    status: int = 0
    top_id: str
    title: str
    cover: Union[str, None] = None
    desc: Union[str, None] = None
    author: Union[str, None] = None
    timestamp: Union[str, None] = None
    hot: Union[int, None] = None
    url: Union[str, None] = None
    mobileUrl: Union[str, None] = None
    formForGenerate: Union[FormForCreationGenerate, None] = None
    result: dict = {}
    del_flag: bool = False
    create_time: datetime

class CreationRowInfo(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id")
    source: str
    title: str
    cover: Optional[str] = None
    desc: Optional[str] = None
    # author: Optional[str] = None
    timestamp: Optional[str] = None
    hot: Optional[int] = None
    url: Optional[str] = None
    create_time: DateTimeField
    status: Optional[int] = 0

class CreationData(BaseModel):
    items: List[CreationRowInfo]
    total: int
    page: int
    size: int

class CreationDetailInfo(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id")
    source: str
    title: str
    cover: Optional[str] = None
    desc: Optional[str] = None
    author: Optional[str] = None
    timestamp: Optional[str] = None
    hot: Optional[int] = None
    url: Optional[str] = None
    mobileUrl: Optional[str] = None
    result: List[ResultForCreationGenerate] = []
    status: Optional[int] = 0

class CreationGenerateForm(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id")
    source: str
    title: str
    cover: Optional[str] = None
    desc: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    mobileUrl: Union[str, None] = None
    formForGenerate: Union[FormForCreationGenerate, None] = None
    status: Optional[int] = 0


class CreationDataResponse(BaseModel):
    code: int
    message: str
    data: Union[CreationData | CreationDetailInfo | CreationGenerateForm]


class CreationGenerateFormUpdateRequest(BaseModel):
    id: str
    form: FormForCreationGenerate

class OnlyIdRequest(BaseModel):
    id: str

class StatusUpdateRequest(BaseModel):
    ids: List[str]
    status: str

class IdsUpdateRequest(BaseModel):
    ids: List[str]