import abc
import logging

from domain.exceptions import AuthRequired
from domain.model import Aggregate, Sender
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
logger = logging.getLogger(__name__)

class AbstractSenderService(abc.ABC):
    @abc.abstractmethod
    async def send(self, aggregate: Aggregate):
        raise NotImplemented

    @abc.abstractmethod
    async def auth(self,*args,**kwargs)->bool:
        raise NotImplemented

class FakeSenderService(AbstractSenderService):
    async def send(self, aggregate: Aggregate):
        print(aggregate.sender.name)
        print(aggregate.message.message)
        for r in aggregate.receivers:
            print(r.name)
            print(r.id)
            print(" ")

    async def auth(self,*args,**kwargs)->bool:
        return True


class SenderService(AbstractSenderService):

    async def send(self, aggregate: Aggregate):
        API_ID = 28172272
        API_HASH = 'd06bd430d4b4ee0a6e9d08b2fd9d68e7'
        PHONE = '+79204695225'
        LOGIN = 'Thisismeornotme'

        #client = Client(name=aggregate.sender.telegram_name,
        #                api_id=aggregate.sender.api_id,
        #                api_hash=aggregate.sender.api_hash,
        #                phone_number=aggregate.sender.phone)

        client = Client(name=LOGIN,
                        api_id=API_ID,
                        api_hash=API_HASH,
                        phone_number=PHONE)

        try:
            # Подключаемся и получаем статус авторизации
            is_authorized = await client.connect()

            if not is_authorized:
                logger.info("Требуется авторизация")

                # Отправляем код
                sent_code = await client.send_code(client.phone_number)
                raise AuthRequired()
                #phone_code = input("Введите код из Telegram: ")

                try:
                    await client.sign_in(
                        phone_number=client.phone_number,
                        phone_code_hash=sent_code.phone_code_hash,
                        phone_code=phone_code
                    )
                except SessionPasswordNeeded:
                    password = input("Введите пароль 2FA: ")
                    await client.check_password(password)
                except PhoneCodeInvalid:
                    logger.error("Неверный код!")
                    return

            # Проверяем подключение (дополнительная страховка)
            if client.is_connected:
                await client.send_message("me", "Тестовое сообщение")
                logger.info("Сообщение отправлено в Избранное!")
            else:
                logger.error("Нет подключения к серверу")


        finally:
            if client.is_connected:
                await client.disconnect()

    async def auth(self,sender:Sender,phone_code:str,password:str) ->bool:

        async with Client(name=sender.name,api_id=sender.api_id, api_hash=sender.api_hash,
                          phone_number=sender.phone) as client:
            try:
                await client.connect()
                if await client.is_connected():
                    return True
                sent_code = await client.send_code(client.phone_number)
                try:
                    signed_in = await client.sign_in(client.phone_number, sent_code.phone_code_hash, phone_code)
                except SessionPasswordNeeded as e:
                    await client.check_password(password)
                return True
            except AuthRequired as e:
                return False

            finally:
                await client.disconnect()
