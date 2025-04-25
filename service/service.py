from adapters.sender import AbstractSenderService
from domain.exceptions import SenderNotFound, MessageNotFound, InvalidApiHashError
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

    async def get_messages(self) -> list[Message]:
        async with self.uow:
            return self.uow.repository.get_messages()

    async  def get_senders(self) -> list[Sender]:
        async with self.uow:
            return self.uow.repository.get_senders()

    async def get_sender(self, sender_id: int) -> Sender:
        async with self.uow:
            return self.uow.repository.get_sender(sender_id=sender_id)

    async def get_receivers(self) -> list[Receiver]:
        async with self.uow:
            return self.uow.repository.get_receivers()

    async def send_message(
            self,
            sender_id: int,
            receivers_id: list[int],
            message_id: int,
            api_hash: str | None = None
    ):
        async with self.uow:
            message: Message = Message.empty_message()
            if self.check_id(message_id):
                message = self.uow.repository.get_message(message_id)
                if message_id != message.id:
                    raise MessageNotFound()
            await self._send(
                sender_id=sender_id,
                receivers_id=receivers_id,
                message=message,
                api_hash=api_hash
            )

    async def send_new_message(
            self,
            sender_id: int,
            receivers_id: list[int],
            message_text: str,
            api_hash: str | None = None
    ):
        message: Message = Message(id=0, message=message_text)
        async with self.uow:
            await self._send(
                sender_id=sender_id,
                receivers_id=receivers_id,
                message=message,
                api_hash=api_hash
            )

    async def _validate_participants(
            self,
            sender_id: int,
            receivers_id: list[int],
            api_hash: str | None = None  # Новый параметр для входящего хэша
    ) -> tuple[Sender, list[Receiver]]:
        """Проверяет валидность отправителя (включая api_hash) и получателей"""
        sender = Sender.empty_sender()
        if self.check_id(sender_id):
            sender = self.uow.repository.get_sender(sender_id=sender_id)
            if sender_id != sender.id:
                raise SenderNotFound()

            # Проверка api_hash, если он требуется
            if api_hash is not None:
                if sender.api_hash != api_hash:
                    raise InvalidApiHashError("Неверный API-хэш отправителя")

        receivers = []
        for receiver_id in receivers_id:
            if self.check_id(receiver_id):
                receiver = self.uow.repository.get_receiver(receiver_id)
                if receiver_id == receiver.id:
                    receivers.append(receiver)

        if not receivers:
            raise ValueError("Должен быть хотя бы один валидный получатель")

        return sender, receivers

    async def _send(
            self,
            sender_id: int,
            receivers_id: list[int],
            message: Message,
            api_hash: str | None = None
    ):
        sender, receivers = await self._validate_participants(
            sender_id=sender_id,
            receivers_id=receivers_id,
            api_hash=api_hash
        )
        aggregate = Aggregate(sender=sender, receivers=receivers, message=message)
        await self.sender_service.send(aggregate)



