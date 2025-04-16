import asyncio

from pyrogram import Client, types
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.utils import ainput

API_ID=28172272
API_HASH='d06bd430d4b4ee0a6e9d08b2fd9d68e7'
PHONE='+79204695225'
LOGIN='Thisismeornotme'


async def try_to_send():
    client = Client(name=LOGIN,
             api_id=API_ID,
             api_hash=API_HASH,
             phone_number=PHONE)

    auth=await client.connect()

    code_hash=""

#    if not auth:
#        sent_code = await client.send_code(PHONE)
#        code_hash=sent_code.phone_code_hash

    await client.disconnect()

    client = Client(name=LOGIN,
             api_id=API_ID,
             api_hash=API_HASH,
             phone_number=PHONE)

    auth=await client.connect()
    if not auth:
        print('not auth')
        try:

            sent_code = await client.send_code(PHONE)
            code_hash = sent_code.phone_code_hash

            code=await ainput("Enter confirmation code: ")
            signed_in = await client.sign_in(PHONE, code_hash, code)
        except SessionPasswordNeeded as e:
            password = await ainput("Enter password: ")
            await client.check_password(password)

        finally:
            await client.send_message("me", "Тестовое сообщение")
            if client.is_connected:
                await client.disconnect()


if __name__=='__main__':
    asyncio.run(try_to_send())
