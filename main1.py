import asyncio
import sqlite3
from typing import Union

from adapters.sender import FakeSenderService, SenderService
from service.service import Service
from service.uow import HTTPUnitOfWork, AlmostUnitOfWork


def create_uow(use_fake: bool = False) -> Union[HTTPUnitOfWork, AlmostUnitOfWork]:
    conn = sqlite3.Connection('./db/telegram-user.db')
    if use_fake:
        return AlmostUnitOfWork(conn=conn)
    return HTTPUnitOfWork(url='http://192.168.100.147:8080/api/v1/n/user/', conn=conn)


async def get_data(use_fake: bool = False):
    async with create_uow(use_fake=use_fake) as uow:
        service = Service(uow=uow, sender_service=FakeSenderService())
        receivers = service.get_receivers()
        ids = [receiver.id for receiver in receivers]
        sender = service.get_sender(sender_id=1)

    return sender, ids


async def put_data(sender_id: int, receivers: list[int], use_fake: bool = False):
    async with create_uow(use_fake=use_fake) as uow:
        service = Service(uow=uow, sender_service=FakeSenderService())
        await service.send_message(sender_id=sender_id, receivers_id=receivers, message_id=1)


async def main():
    data = await get_data(use_fake=True)
    await put_data(sender_id=data[0].id, receivers=data[1], use_fake=False)


if __name__ == "__main__":
    asyncio.run(main())
