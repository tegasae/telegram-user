import abc
import logging
from domain.model import Aggregate
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
logger = logging.getLogger(__name__)

class AbstractSenderService(abc.ABC):
    @abc.abstractmethod
    def send(self, aggregate: Aggregate):
        raise NotImplemented


class FakeSenderService(AbstractSenderService):

    async def send(self, aggregate: Aggregate):
        print(aggregate.sender.name)
        print(aggregate.message.message)
        for r in aggregate.receivers:
            print(r.name)
            print(r.id)
            print(" ")



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

        print(
            f"{aggregate.sender.telegram_name} {aggregate.sender.api_id} {aggregate.sender.api_hash} {aggregate.sender.phone}")

        try:
            c=await client.connect()  # Подключаемся к серверам Telegram
            client.start()
            # Проверяем, авторизован ли клиент
            if not c:
                logger.info("Авторизация...")

                # Пытаемся войти
                sent_code = await client.send_code(aggregate.sender.phone)

                # Если требуется код подтверждения
                phone_code = input("Введите код подтверждения из Telegram: ")

                try:
                    await client.sign_in(
                        aggregate.sender.phone,
                        sent_code.phone_code_hash,
                        phone_code
                    )
                except SessionPasswordNeeded:
                    # Если включена 2FA, запрашиваем пароль
                    password = input("Введите пароль двухфакторной аутентификации: ")
                    await client.check_password(password)
                except PhoneCodeInvalid:
                    logger.error("Неверный код подтверждения!")
                    return

            # Отправляем сообщение
            await client.send_message("me", aggregate.message.message)
            #logger.info(f"Сообщение отправлено в {target_chat}!")

        #except Exception as e:
        #    logger.error(f"Ошибка: {e}")
        finally:
            if client.is_connected:
                await client.disconnect()  # Закрываем соединение

        # await client.start()
        #auth = await client.connect()
        # for r in aggregate.receivers:
        # client.send_message(chat_id='obukhovrn', text='Нет, это не я набирал')
        #    print(f"{r.name} {r.telegram_id} {aggregate.message.message}")
        #await client.stop()
        # async with client:
        #    print(await client.get_me())
