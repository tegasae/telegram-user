import abc
from abc import abstractmethod

from domain.model import Message, Sender, Receiver


class AbstractRepository(abc.ABC):
    @abstractmethod
    def get_messages(self) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def get_senders(self) -> list[Sender]:
        raise NotImplementedError

    @abstractmethod
    def get_receivers(self) -> list[Receiver]:
        raise NotImplementedError

    @abstractmethod
    def get_message(self, message_id: int) -> Message:
        raise NotImplementedError

    @abstractmethod
    def get_sender(self, sender_id: int) -> Sender:
        raise NotImplementedError

    @abstractmethod
    def get_receiver(self, receiver_id: int) -> Receiver:
        raise NotImplementedError

    @abstractmethod
    def save_message(self, message: Message) -> Message:
        raise NotImplementedError

    @abstractmethod
    def delete_message(self, message_id: int) -> bool:
        raise NotImplementedError


class FakeRepository(AbstractRepository):
    def __init__(self):
        self.senders={1:Sender(id=1,name="sender1",telegram_id="telegram1",api_id=1,api_hash="hash1"),
                      2: Sender(id=2, name="sender2", telegram_id="telegram2", api_id=1, api_hash="hash2")
                      }
        self.receivers={1:Receiver(id=1,name="Receiver1",telegram_id="telegram_receiver1"),
                        2: Receiver(id=2, name="Receiver2", telegram_id="telegram_receiver2"),
                        3: Receiver(id=3, name="Receiver3", telegram_id="telegram_receiver3")
        }
        self.messages={
            1:Message(id=1,message="message1"),
            2: Message(id=2, message="message2"),
        }

    def get_messages(self) -> list[Message]:
        return list(self.messages.values())

    def get_senders(self) -> list[Sender]:
        return list(self.senders.values())

    def get_receivers(self) -> list[Receiver]:
        return list(self.receivers.values())

    def get_message(self, message_id: int) -> Message:
        return self.messages.get(message_id,Message.empty_message())

    def get_sender(self, sender_id: int) -> Sender:
        return self.senders.get(sender_id, Sender.empty_sender())

    def get_receiver(self, receiver_id: int) -> Receiver:
        return self.receivers.get(receiver_id, Receiver.empty_receiver())

    def save_message(self, message: Message) -> Message:
        try:
            new_id=max(list(self.messages.keys()))
            new_id+=1
        except ValueError:
            new_id=1
        message.id=new_id
        self.messages[message.id]=message
        return message

    def delete_message(self, message_id: int) -> bool:
        try:
            del(self.messages[message_id])
            return True
        except KeyError:
            return False
