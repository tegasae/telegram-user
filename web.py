import sqlite3
from typing import List

import uvicorn
from aiohttp.web_exceptions import HTTPError, HTTPMethodNotAllowed, HTTPNotAcceptable
from fastapi import FastAPI, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.responses import RedirectResponse

from adapters.sender import FakeSenderService, SenderService, AbstractSenderService
from domain.exceptions import AuthRequired
from myweb.forms import MyFormModelOutput, MyFormModelInput
from service.service import Service
from service.uow import HTTPUnitOfWork, AlmostUnitOfWork

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def create_template(request: Request, var: dict, form: MyFormModelOutput, events: list):
    template = templates.get_template("index.tmpl")

    # 3. Рендерим в строку (если нужно дополнительно обработать)
    html_content = template.render(var=var, form=form, current_events=events)
    # 4. Возвращаем как HTMLResponse
    return html_content


def get_uow():
    use_fake = False
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


def get_sender_service() -> AbstractSenderService:
    use_fake = True

    if use_fake:
        sender_service = FakeSenderService()
    else:
        sender_service = SenderService()
    return sender_service


@app.get("/", response_class=HTMLResponse)
async def read(request: Request, events: str = Query(default=None, description="Must be integer"),
               uow: HTTPUnitOfWork = Depends(get_uow), sender_service=Depends(get_sender_service)):

    sender_cookie = request.cookies.get("sender", "")
    api_hash_cookie=request.cookies.get("api_hash","")

    try:
        sender_cookie=int(sender_cookie)
    except (TypeError,ValueError):
        sender_cookie=0

    try:
        list_of_events: List[int] = [int(events)]
    except ValueError:
        list_of_events: List[int] = [2]
    except TypeError:
        list_of_events: List[int] = []

    service = Service(uow=uow, sender_service=sender_service)

    receivers = await service.get_receivers()
    senders = await service.get_senders()
    messages = await service.get_messages()
    model = MyFormModelOutput(receivers=receivers, senders=senders, messages=messages, message="")
    content = create_template(request=request, var={"set_sender":sender_cookie,"api_hash":api_hash_cookie}, form=model, events=list_of_events)
    return HTMLResponse(content=content)


@app.post("/", response_class=HTMLResponse)
async def send(
        request: Request,
        uow: HTTPUnitOfWork = Depends(get_uow),
        sender_id: int = Form(..., alias="senders"),
        receivers: List[int] = Form([]),
        message: str = Form(...),
        api_hash: str = Form(...),
        sender_service=Depends(get_sender_service)
):
    set_sender=0
    set_api_hash=api_hash
    sender_cookie = request.cookies.get("sender", "")
    api_hash_cookie = request.cookies.get("api_hash", "")
    try:
        sender_cookie = int(sender_cookie)
    except (TypeError, ValueError):
        sender_cookie = 0


    if sender_id:
        set_sender = sender_id
    error=0
    try:
        form_data = MyFormModelInput(
            sender=sender_id,
            receivers=receivers,
            message=message
        )
        service = Service(uow=uow, sender_service=sender_service)
        sender = await service.get_sender(sender_id=form_data.sender)

        if sender_cookie != sender_id and api_hash_cookie == api_hash:
            set_api_hash = ""

        sender.api_hash=set_api_hash
        await service.send_new_message(
            sender_id=sender_id,
            receivers_id=form_data.receivers,
            message_text=form_data.message
        )
        error = 1
        set_sender=form_data.sender
        #response=RedirectResponse(url=f"/?events={error}", status_code=303)
        #response.set_cookie(key="sender", value=str(form_data.sender),max_age=360000, expires=360000)

        #return response

    except ValidationError as e:
        first_error = e.errors()[0]
        error = 0
        for i in e.errors():

            if i['loc'][0] == 'message':
                error = 2
            if i['loc'][0] == 'receivers':
                error = 3
            if i['loc'][0] == 'senders':
                error = 4

        field = first_error['loc'][0]
        msg = first_error['msg']
        #return RedirectResponse(
        #    url=f"/?events={error}",
        #    status_code=303
        #)
    except AuthRequired:
        error=5
        raise HTTPNotAcceptable()

        # return RedirectResponse(
        #    url=f"/auth?sender_id={sender}",
        #    status_code=303
        # )
    except Exception as e:
        # Логирование для разработчика
        print(f"Unhandled error: {str(e)}")
        error = 5
        #return RedirectResponse(
        #    url=f"/?events={error}",
        #    status_code=303
        #)
    finally:
        response = RedirectResponse(url=f"/?events={error}", status_code=303)
        response.set_cookie(key="sender", value=str(set_sender), max_age=360000, expires=360000)
        response.set_cookie(key="api_hash", value=set_api_hash, max_age=360000, expires=360000)
        return response

@app.get("/auth")
async def auth_page(request: Request, uow: HTTPUnitOfWork = Depends(get_uow), sender_id: int = Query(default=0),
                    sender_service=Depends(get_sender_service)):
    """Страница авторизации"""
    number = await sender_service.get_number(sender=uow.repository.get_sender(sender_id=sender_id))
    sender_id = sender_id
    return templates.TemplateResponse("auth.tmpl", {"request": request, "number": number, "sender_id": sender_id})


@app.post("/auth")
async def process_auth(
        request: Request, uow: HTTPUnitOfWork = Depends(get_uow),
        phone_code: str = Form(...),
        number: str = Form(...),
        password: str = Form(None),  # Пароль может быть None если 2FA не включен,
        sender_id: int = Form(...),

        sender_service=Depends(get_sender_service)
):
    """Обработка авторизации"""
    sender = uow.repository.get_sender(sender_id=sender_id)
    r = await sender_service.auth(sender=sender, phone_code=phone_code, password=password, code=number)
    if r:
        return RedirectResponse(url="/", status_code=303)
    else:
        return RedirectResponse(url="/123", status_code=303)


if __name__ == "__main__":
    uvicorn.run("web:app", host="0.0.0.0", port=8010, reload=True)
