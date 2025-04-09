from fastapi import Form
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Type
from enum import Enum

from domain.model import Sender, Receiver, Message


class FormField:
    def __init__(self, field_type: str, label: str, required: bool = True, options: Dict[str, Any] = None,name:str="", values:Any=None):
        self.field_type = field_type
        self.label = label
        self.required = required
        self.options = options or {}
        self.name = name
        self.values=values


class MyFormModel(BaseModel):
    senders: List[Sender]
    receivers:List[Receiver]
    messages: List[Message]
    message:str

    #@field_validator('interests')
    #@classmethod
    #def validate_interests(cls, v: List[str]) -> List[str]:
    #    if not v:
    #        raise ValueError("Должен быть выбран хотя бы один интерес")
    #    return v


class MyFormModelOutput(BaseModel):
    sender: int
    receivers: List[int]
    message: str


async def get_form_data(
        message: str = Form(str),
        receivers: List[int] = Form([int]),
        senders: str = Form(str)
) -> MyFormModelOutput:
    return MyFormModelOutput(
        message=message,
        receivers=receivers,
        sender=senders
    )


class MyForm:
    def __init__(self,model:MyFormModel):
        self.model = model
        self.fields = {
            "senders": FormField("checkbox", "Имя отправителей",name="senders", values=model.senders),
            "receivers": FormField("checkbox", "Имя получателей",name="receivers",values=model.receivers),
            "messages": FormField("radiobutton", "Сообщения",name="messages",values=model.messages),
            "message":FormField(field_type="textarea",label="Сообщение",name="message", values=model.message)
        }

    #def get_form_data(self, **kwargs):
    #    return self.model(**kwargs)