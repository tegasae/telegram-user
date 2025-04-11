from fastapi import Form, HTTPException
from pydantic import BaseModel, field_validator, ValidationError
from typing import List

from domain.model import Sender, Receiver, Message


class MyFormModelOutput(BaseModel):
    senders: List[Sender]
    receivers: List[Receiver]
    messages: List[Message]
    message: str = ""
    value_field: dict = {'senders': 'senders', 'receivers': 'receivers', 'messages': 'messages', 'message': 'message'}


class MyFormModelInput(BaseModel):
    sender: int
    receivers: List[int]
    message: str  # Обязательное поле

    @field_validator('sender')
    @classmethod
    def validate_sender(cls, v: int) -> int:
        if type(v) is not int and v <= 0:
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
        first_error = e.errors()[0]
        field = first_error['loc'][0]
        msg = first_error['msg']
        raise FormValidationError(field=field, message=msg)


class FormValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(message)


if __name__ == "__main__":
    mf = MyFormModelInput(sender=1, receivers=[], message="")
