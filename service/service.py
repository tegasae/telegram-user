from adapters.sender import AbstractSenderService
from domain.exceptions import SenderNotFound, MessageNotFound
from domain.model import Sender, Receiver, Message, Aggregate
from service.uow import FakeUnitOfWork, AbstractUnitOfWork


class Service:
    def __init__(self, uow: AbstractUnitOfWork, sender_service: AbstractSenderService):
        self.uow = uow
        self.sender_service = sender_service

    @staticmethod
    def check_id(item_id: int) -> bool:
        if type(item_id) is int and item_id > 0:
            return True
        else:
            return False

    def get_messages(self) -> list[Message]:
        return self.uow.repository.get_messages()

    def get_senders(self) -> list[Sender]:
        return self.uow.repository.get_senders()

    def get_sender(self,sender_id:int) -> Sender:
        return self.uow.repository.get_sender(sender_id=sender_id)


    def get_receivers(self) -> list[Receiver]:
        return self.uow.repository.get_receivers()

    async def send_message(self, sender_id: int, receivers_id: list[int], message_id: int):

        message: Message = Message.empty_message()

        if self.check_id(message_id):
            message = self.uow.repository.get_message(message_id)
            if message_id != message.id:
                raise MessageNotFound()
        await self._send(sender_id=sender_id, receivers_id=receivers_id, message=message)

    async def send_new_message(self, sender_id: int, receivers_id: list[int], message_text: str):
        message: Message = Message(id=0, message=message_text)
        await self._send(sender_id=sender_id, receivers_id=receivers_id, message=message)

    async def auth(self,sender_id: int,*args,**kwargs)->bool:
        sender: Sender = Sender.empty_sender()
        if self.check_id(sender_id):
            sender = self.uow.repository.get_sender(sender_id=sender_id)
            if sender_id != sender.id:
                raise SenderNotFound()

        r= await self.sender_service.auth(sender,phone_code=kwargs['phone_code'],password=kwargs['password'])
        return r

    async def _send(self, sender_id: int, receivers_id: list[int], message: Message):
        receivers = []
        sender: Sender = Sender.empty_sender()
        if self.check_id(sender_id):
            sender = self.uow.repository.get_sender(sender_id=sender_id)
            if sender_id != sender.id:
                raise SenderNotFound()

        for r in receivers_id:
            if self.check_id(r):
                receiver = self.uow.repository.get_receiver(r)
                if r == receiver.id:
                    receivers.append(receiver)

        aggregate = Aggregate(sender=sender, receivers=receivers, message=message)
        await self.sender_service.send(aggregate)
