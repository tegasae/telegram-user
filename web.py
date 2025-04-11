import sqlite3


import uvicorn
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from adapters.sender import FakeSenderService, SenderService
from domain.exceptions import AuthRequired

from service.service import Service
from service.uow import HTTPUnitOfWork, AlmostUnitOfWork
from myweb.forms import MyForm, MyFormModelOutput, MyFormModelInput, get_form_data

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Глобальные переменные
pending_message:MyFormModelInput
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
    service = Service(uow=uow, sender_service=FakeSenderService())
    receivers = service.get_receivers()
    senders = service.get_senders()
    messages = service.get_messages()
    model = MyFormModelOutput(receivers=receivers, senders=senders, messages=messages, message="")
    fh = form_handler(model=model)
    var = {'receivers': receivers, 'senders': senders, 'messages': messages}
    return HTMLResponse(content=create_template(request=request, var=var, fields=fh.fields))


@app.post("/", response_class=HTMLResponse)
async def send(request: Request, uow: HTTPUnitOfWork = Depends(get_uow), form_data: MyFormModelInput = Depends(get_form_data)):
    global pending_message
    sender_id = form_data.sender
    receivers=form_data.receivers
    message=form_data.message
    try:
        async with (uow):
            service = Service(uow=uow, sender_service=FakeSenderService())
            await service.send_new_message(sender_id=sender_id, receivers_id=receivers, message_text=message)

            #RedirectResponse(url="/auth", status_code=303)
    except AuthRequired:
        # Сохраняем сообщение и перенаправляем на авторизацию
        pending_message = form_data


        return RedirectResponse(url="/auth", status_code=303)
    else:
        return "1111"
    #except Exception:

    #    return RedirectResponse(url="/au", status_code=303)

    return RedirectResponse(url="/", status_code=303)

@app.get("/auth")
async def auth_page(request: Request):
    """Страница авторизации"""
    return templates.TemplateResponse("auth.tmpl", {"request": request})


@app.post("/auth")
async def process_auth(
        request: Request,uow: HTTPUnitOfWork = Depends(get_uow),
        phone_code: str = Form(...),
        password: str = Form(None)  # Пароль может быть None если 2FA не включен
):
    """Обработка авторизации"""
    global pending_message

    async with (uow):
        service = Service(uow=uow, sender_service=SenderService())
        r=await service.auth(sender_id=pending_message.sender, phone_code=phone_code,password=password)
        if r is False:
            raise AuthRequired()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
