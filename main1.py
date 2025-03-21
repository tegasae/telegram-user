from adapters.sender import FakeSenderService
from service.service import Service
from service.uow import FakeUnitOfWork

if __name__=="__main__":
    uow=FakeUnitOfWork()
    sender_service=FakeSenderService()
    print(uow.repository.get_messages())
    service=Service(uow=uow,sender_service=sender_service)
    service.send(sender_id=1,receivers_id=[1,2],message_id=1)
    print(service.get_senders())