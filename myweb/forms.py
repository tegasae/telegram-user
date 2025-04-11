from fastapi import Form, HTTPException
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Dict, Any


from domain.model import Sender, Receiver, Message


class FormField:
    def __init__(self, field_type: str, label: str, required: bool = True, options: Dict[str, Any] = None,name:str="", values:Any=None):
        self.field_type = field_type
        self.label = label
        self.required = required
        self.options = options or {}
        self.name = name
        self.values=values


class MyFormModelOutput(BaseModel):
    senders: List[Sender]
    receivers:List[Receiver]
    messages: List[Message]
    message:str=""


    #@classmethod
    #@field_validator('senders')
    #def validate_interests(cls, v: List[str]) -> List[str]:
    #    if not v:
    #        raise ValueError("Должен быть выбран хотя бы один интерес")
    #    return v


class MyFormModelInput(BaseModel):
    sender: int
    receivers: List[int]
    message: str  # Обязательное поле

    @field_validator('sender')
    @classmethod
    def validate_sender(cls, v: int) -> int:
        if type(v) is not int and v<=0:
            raise ValueError("Должно быть больше 0")
        return v

    @field_validator('message')
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Сообщение не может быть пустым")
        return v.strip()

    @field_validator('receivers')
    @classmethod
    def validate_receivers_not_empty(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("Должен быть выбран хотя бы один получатель")
        return v


async def get_form_data(
    sender: int = Form(..., alias="senders"),
    receivers: List[int] = Form([]),
    message: str = Form(...)
) -> MyFormModelInput:
    try:
        return MyFormModelInput(
            sender=sender,
            receivers=receivers,
            message=message
        )
    except ValidationError as e:
        # Берем первое сообщение об ошибке
        first_error = e.errors()[0]
        field = first_error['loc'][0]
        msg = first_error['msg']
        error_msg = f"Ошибка в поле '{field}': {msg}"
        raise HTTPException(status_code=400, detail=error_msg)
    except ValueError as e:
        error_msg = f"Ошибка в данных: {str(e)}"
        raise HTTPException(status_code=400, detail=error_msg)


class MyForm:
    def __init__(self, model:MyFormModelOutput):
        self.model = model
        self.fields = {
            "senders": FormField("checkbox", "Имя отправителей",name="senders", values=model.senders),
            "receivers": FormField("checkbox", "Имя получателей",name="receivers",values=model.receivers),
            "messages": FormField("radiobutton", "Сообщения",name="messages",values=model.messages),
            "message":FormField(field_type="textarea",label="Сообщение",name="message", values=model.message)
        }

    #def get_form_data(self, **kwargs):
    #    return self.model(**kwargs)

if __name__=="__main__":
    mf=MyFormModelInput(sender=1,receivers=[],message="")