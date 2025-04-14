import sqlite3
from contextvars import ContextVar
from typing import List

import uvicorn
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.responses import RedirectResponse

from adapters.sender import FakeSenderService, SenderService
from domain.exceptions import AuthRequired
from domain.model import Sender

from service.service import Service
from service.uow import HTTPUnitOfWork, AlmostUnitOfWork
from myweb.forms import MyFormModelOutput, MyFormModelInput, get_form_data
from urllib.parse import quote


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Глобальные переменные
pending_message: MyFormModelInput
auth_step = 1  # 1 - запрос кода, 2 - ввод кода, 3 - ввод пароля

global_events: ContextVar[List[int]] = ContextVar('global_events', default=[])


def create_template(request: Request, var: dict, form: dict,events:list):
    template = templates.get_template("index.tmpl")

    # 3. Рендерим в строку (если нужно дополнительно обработать)
    html_content = template.render(var=var, form=form,current_events=events)
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
async def read(request: Request, events:str=Query(default=None, description="Must be integer"),uow: HTTPUnitOfWork = Depends(get_uow)):
    try:
        list_of_events:List[int]= [int(events)]
    except ValueError:
        list_of_events: List[int]=[2]
    except TypeError:
        list_of_events: List[int] = []

    service = Service(uow=uow, sender_service=FakeSenderService())

    receivers = service.get_receivers()
    senders = service.get_senders()
    messages = service.get_messages()
    model = MyFormModelOutput(receivers=receivers, senders=senders, messages=messages, message="")
    content = create_template(request=request, var={}, form=model, events=list_of_events)
    return HTMLResponse(content=content)



@app.post("/", response_class=HTMLResponse)
async def send(
        request: Request,
        uow: HTTPUnitOfWork = Depends(get_uow),
        sender: int = Form(..., alias="senders"),
        receivers: List[int] = Form([]),
        message: str = Form(...)
):

    try:
        form_data = MyFormModelInput(
            sender=sender,
            receivers=receivers,
            message=message
        )
        service = Service(uow=uow, sender_service=FakeSenderService())
        await service.send_new_message(
                sender_id=form_data.sender,
                receivers_id=form_data.receivers,
                message_text=form_data.message
            )
        error=1
        return RedirectResponse(url=f"/?events={error}", status_code=303)

    except ValidationError as e:
        first_error = e.errors()[0]
        error = 0
        for i in e.errors():

            if i['loc'][0]=='message':
                error=2
            if i['loc'][0]=='receivers':
                error=3
            if i['loc'][0]=='senders':
                error=4

        field = first_error['loc'][0]
        msg = first_error['msg']
        return RedirectResponse(
            url=f"/?events={error}",
            status_code=303
        )
    except Exception as e:
        # Логирование для разработчика
        print(f"Unhandled error: {str(e)}")
        error=5
        return RedirectResponse(
            url=f"/?events={error}",
            status_code=303
        )

@app.get("/auth")
async def auth_page(request: Request):
    """Страница авторизации"""
    request.state.code = Sender(id=100,name="111",telegram_name="1",phone="1",api_id=0,api_hash="1",telegram_id="1")
    return templates.TemplateResponse("auth.tmpl", {"request": request})


@app.post("/auth")
async def process_auth(
        request: Request, uow: HTTPUnitOfWork = Depends(get_uow),
        phone_code: str = Form(...),
        password: str = Form(None)  # Пароль может быть None если 2FA не включен
):
    """Обработка авторизации"""
    sender = getattr(request.state, 'code', None)
    print(sender)

    return RedirectResponse(url="/", status_code=303)


#@app.exception_handler(FormValidationError)
#async def form_validation_exception_handler(request: Request, exc: FormValidationError):
#    return RedirectResponse(
#        url=f"/global_handler_error",
#        status_code=303
#    )




if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
