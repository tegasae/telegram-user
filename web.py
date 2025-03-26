from contextlib import asynccontextmanager, contextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from service.uow import HTTPUnitOfWork

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#    return {"q": q, "skip": skip, "limit": limit}

@contextmanager
def get_uow():
    uow = HTTPUnitOfWork(url='http://192.168.100.147:8080/api/v1/n/user/')
    try:
        yield uow
    finally:
        uow.close()  # Предполагая, что у вас есть метод close()



@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, uow: HTTPUnitOfWork = Depends(get_uow)):
    print(uow)
    return templates.TemplateResponse(request=request, name="index.tmpl")


if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
