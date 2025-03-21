import abc

from domain.model import Aggregate


class AbstractSenderService(abc.ABC):
    @abc.abstractmethod
    def send(self,aggregate:Aggregate)->bool:
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
