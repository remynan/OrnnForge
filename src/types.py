from datetime import datetime
from pydantic import BaseModel
from typing import Union

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
    del_flag: bool = False
    create_time: datetime
