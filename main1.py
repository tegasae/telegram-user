from adapters.sender import FakeSenderService
from service.service import Service
from service.uow import AlmostUnitOfWork

if __name__=="__main__":
    uow=AlmostUnitOfWork()
    sender_service=FakeSenderService()

    service=Service(uow=uow,sender_service=sender_service)
    service.send(sender_id=1,receivers_id=[],message_id=1)
    #print(service.get_senders())