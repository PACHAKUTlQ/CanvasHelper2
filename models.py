from pydantic import BaseModel
"""
Models
"""


class Check(BaseModel):
    type: int


class Course(BaseModel):
    id: int
    name: str
    type: int
    maxshow: int = -1
    order: str = "normal"
    msg: str = ""


class RequestForm(BaseModel):
    username: str
    password: str
    url: str
    bid: str
