import asyncio

from adapters.sender import FakeSenderService
from service.service import Service
from service.uow import HTTPUnitOfWork


async def get_data():
    async with HTTPUnitOfWork(url='http://192.168.100.147:8080/api/v1/n/user/') as uow:
        service = Service(uow=uow, sender_service=FakeSenderService())
        receivers = service.get_receivers()
        ids = [receiver.id for receiver in receivers]
        sender_id = service.get_senders()[0].id

    return sender_id, ids


async def put_data(sender_id: int, receivers: list[int]):
    async with HTTPUnitOfWork(url='http://192.168.100.147:8080/api/v1/n/user/') as uow:
        service = Service(uow=uow, sender_service=FakeSenderService())
        service.send_message(sender_id=sender_id, receivers_id=receivers, message_id=1)

async def main():
    data=await get_data()
    await put_data(sender_id=data[0],receivers=data[1])


if __name__ == "__main__":
    asyncio.run(main())
