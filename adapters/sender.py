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
    async def get_number(self, sender: Sender) -> str:
        raise NotImplemented

    @abc.abstractmethod
    async def auth(self, *args, **kwargs) -> bool:
        raise NotImplemented


class FakeSenderService(AbstractSenderService):
    async def send(self, aggregate: Aggregate):
        require_auth = True

        if not require_auth:
            print(aggregate.sender.name)
            print(aggregate.message.message)

            for r in aggregate.receivers:
                print(r.name)
                print(r.id)
                print(" ")
        else:
            raise AuthRequired()

    async def get_number(self, sender: Sender) -> str:
        return "123"

    async def auth(self, *args, **kwargs) -> bool:
        if kwargs['phone_code'] == kwargs['code']:
            return True
        else:
            return False


class SenderService(AbstractSenderService):

    async def send(self, aggregate: Aggregate):
        API_ID = 28172272
        API_HASH = 'd06bd430d4b4ee0a6e9d08b2fd9d68e7'
        PHONE = '+79204695225'
        LOGIN = 'Thisismeornotme'

        client = Client(name=aggregate.sender.telegram_name,
                        api_id=aggregate.sender.api_id,
                        api_hash=aggregate.sender.api_hash,
                        phone_number=aggregate.sender.phone)

        # client = Client(name=LOGIN,
        #                api_id=API_ID,
        #                api_hash=API_HASH,
        #                phone_number=PHONE)

        try:
            # Подключаемся и получаем статус авторизации
            is_authorized = await client.connect()

            if not is_authorized:
                logger.info("Требуется авторизация")

                # Отправляем код
                raise AuthRequired()
                # phone_code = input("Введите код из Telegram: ")

            # Проверяем подключение (дополнительная страховка)
            if client.is_connected:
                await client.send_message("me", "Тестовое сообщение")
                logger.info("Сообщение отправлено в Избранное!")
            else:
                logger.error("Нет подключения к серверу")
        finally:
            if client.is_connected:
                await client.disconnect()

    async def get_number(self, sender: Sender) -> str:
        client = Client(name=sender.telegram_name,
                        api_id=sender.api_id,
                        api_hash=sender.api_hash,
                        phone_number=sender.phone)
        is_authorized = await client.connect()

        sent_code = await client.send_code(client.phone_number)
        if client.is_connected:
            await client.disconnect()
        return sent_code.phone_code_hash

    async def auth(self, sender: Sender, *args, **kwargs) -> bool:

        client = Client(name=sender.telegram_name,
                        api_id=sender.api_id,
                        api_hash=sender.api_hash,
                        phone_number=sender.phone

                        )
        #phone_code = kwargs['phone_code'],
        #password = kwargs['password']

        try:
            is_auth=await client.connect()
            signed_in = await client.sign_in(sender.phone,kwargs['code'],phone_code=kwargs['phone_code'])

        except SessionPasswordNeeded as e:
            await client.check_password(kwargs['password'])
            return True
        finally:
            if client.is_connected:
                await client.disconnect()

        if signed_in is True:
            return True
        else:
            return False
