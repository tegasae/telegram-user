import abc

from domain.model import Aggregate
from pyrogram import Client

class AbstractSenderService(abc.ABC):
    @abc.abstractmethod
    def send(self,aggregate:Aggregate):
        raise NotImplemented


class FakeSenderService(AbstractSenderService):

    def send(self, aggregate: Aggregate) -> bool:
        print(aggregate.sender.name)
        print(aggregate.message.message)
        for r in aggregate.receivers:
            print(r.name)
            print(r.id)
            print(" ")
        return True


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

        print(f"{aggregate.sender.telegram_name} {aggregate.sender.api_id} {aggregate.sender.api_hash} {aggregate.sender.phone}")

        #await client.start()
        auth=await client.connect()
        #for r in aggregate.receivers:
        #client.send_message(chat_id='obukhovrn', text='Нет, это не я набирал')
        #    print(f"{r.name} {r.telegram_id} {aggregate.message.message}")
        await client.stop()
        #async with client:
        #    print(await client.get_me())