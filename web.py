import sqlite3
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from adapters.sender import FakeSenderService
from service.service import Service
from service.uow import HTTPUnitOfWork, AlmostUnitOfWork

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#    return {"q": q, "skip": skip, "limit": limit}
def create_template(request: Request, var: dict):
    template = templates.get_template("index.tmpl")

    # 3. Рендерим в строку (если нужно дополнительно обработать)
    html_content = template.render(var)
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


@app.get("/", response_class=HTMLResponse)
async def read(request: Request, uow: HTTPUnitOfWork = Depends(get_uow)):
    async with uow:
        service = Service(uow=uow, sender_service=FakeSenderService())
        receivers = service.get_receivers()
        senders = service.get_senders()
        messages = service.get_messages()
        var = {'receivers': receivers, 'senders': senders, 'messages': messages}
    return HTMLResponse(content=create_template(request=request, var=var))


@app.post("/", response_class=HTMLResponse)
async def send(request: Request, uow: HTTPUnitOfWork = Depends(get_uow)):
    print(request)
    return HTMLResponse(content="{}")


if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
