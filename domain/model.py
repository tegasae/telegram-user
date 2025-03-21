from dataclasses import dataclass


@dataclass
class Receiver:
    id: int
    name: str
    telegram_id: str

    @classmethod
    def empty_receiver(cls):
        return cls(id=0, name="", telegram_id="")


@dataclass
class Sender:
    id: int
    name: str
    telegram_id: str
    api_id: int
    api_hash: str

    @classmethod
    def empty_sender(cls):
        return cls(id=0, name="", telegram_id="", api_id=0, api_hash="")


@dataclass
class Message:
    id: int
    message: str

    @classmethod
    def empty_message(cls):
        return cls(id=0, message="")


@dataclass
class Aggregate:
    sender: Sender
    receivers: list[Receiver]
    message: Message
