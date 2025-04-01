from pyrogram import Client
from pyrogram.raw import functions, types
import qrcode
import asyncio
import time

api_id = 28172272
api_hash = "d06bd430d4b4ee0a6e9d08b2fd9d68e7"


async def qr_auth():
    client = Client(":memory:", api_id, api_hash)

    await client.connect()

    try:
        # Первый запрос для получения токена
        qr_result = await client.invoke(
            functions.auth.ExportLoginToken(
                api_id=api_id,
                api_hash=api_hash,
                except_ids=[]
            )
        )

        if isinstance(qr_result, types.auth.LoginToken):
            # Формируем URL для QR-кода
            token_hex = qr_result.token.hex()
            qr_url = f"tg://login?token={token_hex}"

            # Выводим QR-код в консоль
            qr = qrcode.QRCode()
            qr.add_data(qr_url)
            qr.print_ascii()
            print("Отсканируйте QR-код в мобильном приложении Telegram")

            # Ожидаем подтверждения (таймаут 60 секунд)
            start_time = time.time()
            while time.time() - start_time < 60:
                # Повторный запрос для проверки статуса
                check_result = await client.invoke(
                    functions.auth.ExportLoginToken(
                        api_id=api_id,
                        api_hash=api_hash,
                        except_ids=[]
                    )
                )

                if isinstance(check_result, types.auth.LoginTokenSuccess):
                    print("Авторизация успешна!")
                    await client.storage.save()
                    return

                await asyncio.sleep(2)

            print("Время ожидания истекло")

        elif isinstance(qr_result, types.auth.LoginTokenMigrateTo):
            print("Требуется миграция на другой DC")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await client.disconnect()


asyncio.run(qr_auth())