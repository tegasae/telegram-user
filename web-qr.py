import base64
import logging
from io import BytesIO

import qrcode
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
from pyrogram.raw import functions
from starlette.responses import RedirectResponse

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pyrogram import Client
from pyrogram.raw import functions, types
import qrcode
from io import BytesIO
import base64

#
qr_auth_data = {}

app = FastAPI()
templates = Jinja2Templates(directory="templates")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_template(request: Request, var: dict):
    template = templates.get_template("start-qr.tmpl")

    # 3. Рендерим в строку (если нужно дополнительно обработать)
    html_content = template.render(var)
    # 4. Возвращаем как HTMLResponse
    return html_content


async def generate_qr_code():
    """Генерация QR кода для авторизации"""
    async with Client(name="Thisismeornotme", api_id=8172272, api_hash="d06bd430d4b4ee0a6e9d08b2fd9d68e7",
                      phone_number="+79204695225",
                      password="chcp47") as temp_client:
        await temp_client.connect()
        qr_result = await temp_client.invoke(
            functions.auth.ExportLoginToken(
                api_id=8172272,
                api_hash="d06bd430d4b4ee0a6e9d08b2fd9d68e7",
                except_ids=[],

            )
        )

        if isinstance(qr_result, types.auth.LoginToken):
            token_hex = qr_result.token.hex()
            qr_url = f"tg://login?token={token_hex}"

            # Генерация QR кода в base64
            img = qrcode.make(qr_url)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            qr_auth_data["token"] = token_hex
            qr_auth_data["client"] = temp_client

            return img_str
        return None




@app.get("/", response_class=HTMLResponse)
async def read(request: Request):
    return HTMLResponse(content=create_template(request=request, var={}))


@app.post("/", response_class=HTMLResponse)
async def send(request: Request):
    client = Client(
        name="Thisismeornotme",
        api_id=8172272,  # Ваш api_id
        api_hash="d06bd430d4b4ee0a6e9d08b2fd9d68e7",  # Ваш api_hash
        phone_number="+79204695225", # Ваш номер
        password="chpc47",

    )

    try:
        # Подключаемся и получаем статус авторизации
        is_authorized = await client.connect()

        if not is_authorized:
            logger.info("Требуется авторизация")
            return RedirectResponse(url="/auth", status_code=303)
            #raise Exception("Требуется авторизация")

            # Отправляем код
            #sent_code = await client.send_code(client.phone_number)
            #phone_code = input("Введите код из Telegram: ")

            #try:
            #    await client.sign_in(
            #        phone_number=client.phone_number,
            #        phone_code_hash=sent_code.phone_code_hash,
            #        phone_code=phone_code
            #    )
            #except SessionPasswordNeeded:
            #    password = input("Введите пароль 2FA: ")
            #    await client.check_password(password)
            #except PhoneCodeInvalid:
            #    logger.error("Неверный код!")
            #    return

        # Проверяем подключение (дополнительная страховка)
        if client.is_connected:
            await client.send_message("me", "Тестовое сообщение")
            logger.info("Сообщение отправлено в Избранное!")
        else:
            logger.error("Нет подключения к серверу")
            raise Exception("Нет подключения")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise Exception("Исключение")
    finally:
        if client.is_connected:
            await client.disconnect()

    return "{}"


@app.get("/auth")
async def auth_page(request: Request):
    """Страница авторизации с QR кодом"""
    qr_img = await generate_qr_code()
    if not qr_img:
        raise HTTPException(status_code=500, detail="Ошибка генерации QR кода")

    return templates.TemplateResponse("auth.html", {
        "request": request,
        "qr_img": qr_img
    })


if __name__ == "__main__":
    uvicorn.run("web-qr:app", host="127.0.0.1", port=8001, reload=True)
