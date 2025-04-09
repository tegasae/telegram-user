import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import Annotated, List, Optional

import uvicorn
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, validator
from pyrogram import Client
from starlette.responses import RedirectResponse

from adapters.sender import FakeSenderService
from service.service import Service
from service.uow import HTTPUnitOfWork, AlmostUnitOfWork
from myweb.forms import MyForm, MyFormModel, MyFormModelOutput, get_form_data

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Глобальные переменные
pending_message = None
auth_step = 1  # 1 - запрос кода, 2 - ввод кода, 3 - ввод пароля

form_handler = MyForm





def create_template(request: Request, var: dict, fields: dict):
    template = templates.get_template("index.tmpl")

    # 3. Рендерим в строку (если нужно дополнительно обработать)
    html_content = template.render(var=var, fields=fields)
    # 4. Возвращаем как HTMLResponse
    return html_content


def get_uow():
    use_fake = True
    conn = sqlite3.connect('./db/telegram-user.db', check_same_thread=False)  # Важно: отключаем проверку потоков
    if use_fake:
        uow = AlmostUnitOfWork(conn=conn)
    else:
        uow = HTTPUnitOfWork(url='http://192.168.100.147:8080/api/v1/n/user/', conn=conn)
    try:
        yield uow
    finally:
        conn.close()
        uow.close()  # Предполагая, что у вас есть метод close()


@app.get("/", response_class=HTMLResponse)
async def read(request: Request, uow: HTTPUnitOfWork = Depends(get_uow)):
    async with uow:
        service = Service(uow=uow, sender_service=FakeSenderService())
        receivers = service.get_receivers()
        senders = service.get_senders()
        messages = service.get_messages()
        model = MyFormModel(receivers=receivers, senders=senders, messages=messages, message="")
        fh = form_handler(model=model)
        var = {'receivers': receivers, 'senders': senders, 'messages': messages}
    return HTMLResponse(content=create_template(request=request, var=var, fields=fh.fields))


@app.post("/", response_class=HTMLResponse)
async def send(request: Request, uow: HTTPUnitOfWork = Depends(get_uow), form_data: MyFormModelOutput = Depends(get_form_data)):
    print(form_data)
    try:
        # Проверяем авторизацию
        async with (uow):

            service = Service(uow=uow, sender_service=FakeSenderService())
            sender = service.get_sender(sender_id=form_data.sender)
            receivers = service.get_receivers()
            ids = [receiver.id for receiver in receivers if receiver.id in form_data.receivers]

            await service.send_message(sender_id=1, receivers_id=ids, message_id=1)
    except Exception:
        # Сохраняем сообщение и перенаправляем на авторизацию
        pending_message = f"Сообщение 1\nДата и время: {datetime.now()}"
        return RedirectResponse(url="/auth", status_code=303)

    return HTMLResponse(content="{1}")


if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
