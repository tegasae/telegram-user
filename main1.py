from adapters.sender import FakeSenderService
from service.service import Service
from service.uow import AlmostUnitOfWork, HTTPUnitOfWork

if __name__=="__main__":
    #uow=AlmostUnitOfWork()
    uow=HTTPUnitOfWork(url='http://192.168.100.147:8080/api/v1/n/user/')
    #uow = HTTPUnitOfWork(url='http://www.vrn.r')
    sender_service=FakeSenderService()

    service=Service(uow=uow,sender_service=sender_service)
    receivers = service.get_receivers()
    ids = [receiver.id for receiver in receivers]
    sender_id=service.get_senders()[0].id
    service.send_message(sender_id=sender_id, receivers_id=ids, message_id=1)
    service.send_new_message(sender_id=sender_id, receivers_id=[], message_text="a new message")
    print(service.get_senders())