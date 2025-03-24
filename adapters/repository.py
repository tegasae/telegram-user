import abc
import asyncio
import json
import time
from abc import abstractmethod

import aiohttp

from domain.exceptions import DataIsNotGot, DataIsWrong
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
        self.senders = {1: Sender(id=1, name="sender1", telegram_id="telegram1", api_id=1, api_hash="hash1"),
                        2: Sender(id=2, name="sender2", telegram_id="telegram2", api_id=1, api_hash="hash2")
                        }
        self.receivers = {1: Receiver(id=1, name="Receiver1", telegram_id="telegram_receiver1"),
                          2: Receiver(id=2, name="Receiver2", telegram_id="telegram_receiver2"),
                          3: Receiver(id=3, name="Receiver3", telegram_id="telegram_receiver3")
                          }
        self.messages = {
            1: Message(id=1, message="message1"),
            2: Message(id=2, message="message2"),
        }

    def get_messages(self) -> list[Message]:
        return list(self.messages.values())

    def get_senders(self) -> list[Sender]:
        return list(self.senders.values())

    def get_receivers(self) -> list[Receiver]:
        return list(self.receivers.values())

    def get_message(self, message_id: int) -> Message:
        return self.messages.get(message_id, Message.empty_message())

    def get_sender(self, sender_id: int) -> Sender:
        return self.senders.get(sender_id, Sender.empty_sender())

    def get_receiver(self, receiver_id: int) -> Receiver:
        return self.receivers.get(receiver_id, Receiver.empty_receiver())

    def save_message(self, message: Message) -> Message:
        try:
            new_id = max(list(self.messages.keys()))
            new_id += 1
        except ValueError:
            new_id = 1
        message.id = new_id
        self.messages[message.id] = message
        return message

    def delete_message(self, message_id: int) -> bool:
        try:
            del (self.messages[message_id])
            return True
        except KeyError:
            return False


class AlmostRepository(AbstractRepository):
    def __init__(self):
        self.src_str = ('[{"id": 1, "name": "Шугуров Алексей", "status": 14, "telegram_id": "960563331", "full_name": '
                        '"Шугуров Алексей Евгеньевич", "confirmed": 2, "code": "000000018"}, {"id": 2, "name": "avo", '
                        '"status": 0, "telegram_id": "1382097657", "full_name": "Олейников Алексей Владимирович", '
                        '"confirmed": 0, "code": "000000002"}, {"id": 3, "name": "Обухов Роман Николаевич ", '
                        '"status": 10, "telegram_id": "235519445", "full_name": "Обухов Роман Николаевич ", '
                        '"confirmed": 2, "code": "000000061"}, {"id": 4, "name": "Вокрячко Александр Валерьевич", '
                        '"status": 0, "telegram_id": "60032604", "full_name": "Вокрячко Александр Валерьевич", '
                        '"confirmed": 0, "code": "000000004"}, {"id": 5, "name": "Федотова Анастасия Александровна", '
                        '"status": 0, "telegram_id": "1486951166", "full_name": "Федотова Анастасия Александровна", '
                        '"confirmed": 0, "code": "000000110"}, {"id": 6, "name": "ns", "status": 0, "telegram_id": '
                        '"442825780", "full_name": "Шаталов Николай Сергеевич", "confirmed": 0, "code": "000000023"}, '
                        '{"id": 7, "name": "sae1", "status": 14, "telegram_id": "617561041", "full_name": "Шугуров", '
                        '"confirmed": 2, "code": "7"}, {"id": 8, "name": "gav", "status": 12, "telegram_id": '
                        '"1136963829", "full_name": "Горлова Анна Викторовна", "confirmed": 2, "code": "000000105"}, '
                        '{"id": 9, "name": "Иванов Евгений Васильевич", "status": 0, "telegram_id": "432392575", '
                        '"full_name": "Иванов Евгений Васильевич", "confirmed": 0, "code": "000000112"}, {"id": 10, '
                        '"name": "Крылова Алена Алексеевна", "status": 0, "telegram_id": "700181308", "full_name": '
                        '"Крылова Алена Алексеевна", "confirmed": 0, "code": "000000114"}, {"id": 11, "name": "Борисов '
                        'Денис Борисович", "status": 2, "telegram_id": "753809465", "full_name": "Борисов Денис '
                        'Борисович", "confirmed": 2, "code": "000000067"}, {"id": 12, "name": "Мурашов Дмитрий '
                        'Алексеевич", "status": 2, "telegram_id": "67874098", "full_name": "Мурашов Дмитрий '
                        'Алексеевич", "confirmed": 2, "code": "000000062"}, {"id": 13, "name": "kaa", "status": 8, '
                        '"telegram_id": "97576734", "full_name": "Кузнецова Виктория Олеговна", "confirmed": 2, '
                        '"code": "000000088"}, {"id": 14, "name": "Токарев Алексей Александрович", "status": 2, '
                        '"telegram_id": "345929732", "full_name": "Токарев Алексей Александрович", "confirmed": 2, '
                        '"code": "000000031"}, {"id": 15, "name": "Милых Владимир", "status": 0, "telegram_id": '
                        '"405911703", "full_name": "Милых Владимир Александрович", "confirmed": 0, '
                        '"code": "000000066"}, {"id": 16, "name": "Текутьева Татьяна Владимировна", "status": 12, '
                        '"telegram_id": "1316056783", "full_name": "Текутьева Татьяна Владимировна", "confirmed": 2, '
                        '"code": "000000035"}, {"id": 17, "name": "Кобяков Евгений Станиславович", "status": 2, '
                        '"telegram_id": "436114653", "full_name": "Кобяков Евгений Станиславович", "confirmed": 2, '
                        '"code": "000000116"}, {"id": 18, "name": "Лалакина Виктория Сергеевна", "status": 0, '
                        '"telegram_id": "840277747", "full_name": "Лалакина Виктория Сергеевна", "confirmed": 0, '
                        '"code": "000000111"}, {"id": 19, "name": "Мезин Сергей Валериевич", "status": 0, '
                        '"telegram_id": "1513898544", "full_name": "Мезин Сергей Валериевич", "confirmed": 0, '
                        '"code": "000000091"}, {"id": 20, "name": "Куликова Алина", "status": 0, "telegram_id": '
                        '"407841143", "full_name": "Куликова Алина", "confirmed": 0, "code": "20"}, {"id": 21, '
                        '"name": "Романов Александр Владимирович", "status": 2, "telegram_id": "1792850094", '
                        '"full_name": "Романов Александр Владимирович", "confirmed": 2, "code": "000000131"}, '
                        '{"id": 22, "name": "Агапов Данил Альвинович", "status": 2, "telegram_id": "2056489800", '
                        '"full_name": "Агапов Данил Альвинович", "confirmed": 2, "code": "000000129"}, {"id": 23, '
                        '"name": "Чирков Алексей Александрович", "status": 0, "telegram_id": "617561041_1", '
                        '"full_name": "Чирков Алексей Александрович", "confirmed": 0, "code": "000000095"}, {"id": 24, '
                        '"name": "Киселева Ангелина Геннадьевна", "status": 12, "telegram_id": "5132775548", '
                        '"full_name": "Киселева Ангелина Геннадьевна", "confirmed": 2, "code": "000000094"}, {"id": 25,'
                        '"name": "Барышников Игорь Викторович", "status": 0, "telegram_id": "", "full_name": '
                        '"Барышников Игорь Викторович", "confirmed": 0, "code": "000000026"}, {"id": 26, "name": "Струц'
                        'Михаил Владимирович", "status": 0, "telegram_id": "", "full_name": "Струц Михаил '
                        'Владимирович", "confirmed": 0, "code": "000000012"}, {"id": 27, "name": "Дуденков Владимир '
                        'Михайлович", "status": 0, "telegram_id": "", "full_name": "Дуденков Владимир Михайлович", '
                        '"confirmed": 0, "code": "000000068"}, {"id": 28, "name": "Лейчинский Роберт Вадимович", '
                        '"status": 0, "telegram_id": "", "full_name": "Лейчинский Роберт Вадимович", "confirmed": 0, '
                        '"code": "000000108"}, {"id": 29, "name": "Виников Илья Анатольевич", "status": 0, '
                        '"telegram_id": "", "full_name": "Виников Илья Анатольевич", "confirmed": 0, '
                        '"code": "000000106"}, {"id": 30, "name": "Трушина Ирина Анатольевна", "status": 0, '
                        '"telegram_id": "", "full_name": "Трушина Ирина Анатольевна", "confirmed": 0, '
                        '"code": "000000017"}, {"id": 31, "name": "Кузнецов Александр Александрович", "status": 0, '
                        '"telegram_id": "", "full_name": "Кузнецов Александр Александрович", "confirmed": 0, '
                        '"code": "000000016"}, {"id": 32, "name": "Некрасов Андрей", "status": 0, "telegram_id": "", '
                        '"full_name": "Некрасов Андрей", "confirmed": 0, "code": "000000113"}, {"id": 33, "name": "Куку'
                        'Роман Русланович", "status": 0, "telegram_id": "", "full_name": "Куку Роман Русланович", '
                        '"confirmed": 0, "code": "000000115"}, {"id": 34, "name": "Колчугин Олег Александрович", '
                        '"status": 0, "telegram_id": "", "full_name": "Колчугин Олег Александрович", "confirmed": 0, '
                        '"code": "000000119"}, {"id": 35, "name": "Темирязев Дмитрий Алексеевич", "status": 0, '
                        '"telegram_id": "", "full_name": "Темирязев Дмитрий Алексеевич", "confirmed": 0, '
                        '"code": "000000124"}, {"id": 36, "name": "Дементьев Артем Александрович", "status": 0, '
                        '"telegram_id": "", "full_name": "Дементьев Артем Александрович", "confirmed": 0, '
                        '"code": "000000125"}, {"id": 37, "name": "Чирков Алексей Александрович", "status": 2, '
                        '"telegram_id": "1828959946", "full_name": "Чирков Алексей Александрович", "confirmed": 2, '
                        '"code": "000000130"}, {"id": 38, "name": "Ватаман Владислав Юрьевич", "status": 0, '
                        '"telegram_id": "", "full_name": "Ватаман Владислав Юрьевич", "confirmed": 0, '
                        '"code": "000000121"}, {"id": 39, "name": "Косенко Александр Борисович", "status": 0, '
                        '"telegram_id": "", "full_name": "Косенко Александр Борисович", "confirmed": 0, '
                        '"code": "000000128"}, {"id": 40, "name": "Губин Игорь Алексеевич", "status": 0, "telegram_id":'
                        '"", "full_name": "Губин Игорь Алексеевич", "confirmed": 0, "code": "000000098"}, {"id": 41, '
                        '"name": "Брюханов Алексей Владимирович", "status": 0, "telegram_id": "", "full_name": '
                        '"Брюханов Алексей Владимирович", "confirmed": 0, "code": "000000132"}, {"id": 42, '
                        '"name": "Егоров Дмитрий Олегович", "status": 0, "telegram_id": "", "full_name": "Егоров '
                        'Дмитрий Олегович", "confirmed": 0, "code": "000000109"}, {"id": 43, "name": "Иванова Оксана '
                        'Николаевна", "status": 0, "telegram_id": "", "full_name": "Иванова Оксана Николаевна", '
                        '"confirmed": 0, "code": "000000117"}, {"id": 45, "name": "Бузоверов Евгений  Юрьевич", '
                        '"status": 0, "telegram_id": "", "full_name": "Бузоверов Евгений  Юрьевич", "confirmed": 0, '
                        '"code": "УТ0000003"}, {"id": 46, "name": "Рязанцев Максим Сергеевич", "status": 0, '
                        '"telegram_id": "", "full_name": "Рязанцев Максим Сергеевич", "confirmed": 0, '
                        '"code": "УТ0000004"}, {"id": 47, "name": "Крылов Данил Олегович", "status": 0, "telegram_id": '
                        '"", "full_name": "Крылов Данил Олегович", "confirmed": 0, "code": "УТ0000005"}, {"id": 48, '
                        '"name": "Талагаев Максим Юрьевич", "status": 0, "telegram_id": "", "full_name": "Талагаев '
                        'Максим Юрьевич", "confirmed": 0, "code": "УТ0000006"}, {"id": 49, "name": "Чернышов Артем '
                        'Сергеевич", "status": 2, "telegram_id": "432692180", "full_name": "Чернышов Артем Сергеевич", '
                        '"confirmed": 2, "code": "УТ0000008"}, {"id": 50, "name": "Киселев Денис Витальевич", '
                        '"status": 0, "telegram_id": "6266929550", "full_name": "Киселев Денис Витальевич", '
                        '"confirmed": 0, "code": "УТ0000009"}, {"id": 51, "name": "Артем", "status": 0, "telegram_id": '
                        '"432692180_1", "full_name": "", "confirmed": 0, "code": ""}, {"id": 52, "name": "Бойченко '
                        'Сергей Васильевич", "status": 2, "telegram_id": "59324888", "full_name": "Бойченко Сергей '
                        'Васильевич", "confirmed": 2, "code": "УТ0000012"}, {"id": 53, "name": "Черников Николай", '
                        '"status": 0, "telegram_id": "", "full_name": "Черников Николай", "confirmed": 0, '
                        '"code": "УТ0000011"}, {"id": 54, "name": "Ершов Георгий", "status": 0, "telegram_id": "", '
                        '"full_name": "Ершов Георгий", "confirmed": 0, "code": "УТ0000014"}, {"id": 55, '
                        '"name": "Шугурова Нина Ивановна", "status": 0, "telegram_id": "", "full_name": "Шугурова Нина '
                        'Ивановна", "confirmed": 0, "code": "000000013"}, {"id": 56, "name": "Кудаев Евгений '
                        'Геннадьевич", "status": 2, "telegram_id": "978959624", "full_name": "Кудаев Евгений '
                        'Геннадьевич", "confirmed": 2, "code": "УТ0000015"}, {"id": 57, "name": "Исаев Вадим '
                        'Валерьевич", "status": 0, "telegram_id": "", "full_name": "Исаев Вадим Валерьевич", '
                        '"confirmed": 0, "code": "УТ0000017"}, {"id": 58, "name": "Сысоева Ксения Владимировна", '
                        '"status": 0, "telegram_id": "", "full_name": "Сысоева Ксения Владимировна", "confirmed": 0, '
                        '"code": "УТ0000010"}, {"id": 59, "name": "Сайфутдинов Руслан Марселевич", "status": 0, '
                        '"telegram_id": "", "full_name": "Сайфутдинов Руслан Марселевич", "confirmed": 0, '
                        '"code": "УТ0000019"}, {"id": 60, "name": "Ермаков Виктор", "status": 0, "telegram_id": "", '
                        '"full_name": "Ермаков Виктор", "confirmed": 0, "code": "УТ0000020"}, {"id": 61, '
                        '"name": "Дементьев Павел", "status": 2, "telegram_id": "1295330656", "full_name": "Дементьев '
                        'Павел", "confirmed": 2, "code": "УТ0000021"}, {"id": 62, "name": "Шубин Данил", "status": 0, '
                        '"telegram_id": "", "full_name": "Шубин Данил", "confirmed": 0, "code": "УТ0000022"}, '
                        '{"id": 63, "name": "Морозов Владислав Павлович", "status": 0, "telegram_id": "", "full_name": '
                        '"Морозов Владислав Павлович", "confirmed": 0, "code": "УТ0000023"}, {"id": 64, "name": "Смагин'
                        'Илья", "status": 0, "telegram_id": "", "full_name": "Смагин Илья", "confirmed": 0, '
                        '"code": "УТ0000026"}]')
        self.src = json.loads(self.src_str)
        self.messages = {
            1: Message(id=1, message="message1"),
            2: Message(id=2, message="message2"),
        }

        self.auth_senders = {
            '960563331': {'api_id': 28172272, 'api_hash': 'd06bd430d4b4ee0a6e9d08b2fd9d68e7'}
        }

    def get_messages(self) -> list[Message]:
        return list(self.messages.values())

    def get_senders(self) -> list[Sender]:
        senders = []
        for s in self.src:
            if (s['confirmed'] == 2) and (s['status'] & 8):
                auth = self.auth_senders.get(s['telegram_id'], {})
                if len(auth) == 2:
                    senders.append(
                        Sender(id=s['id'], name=s['name'], telegram_id=s['telegram_id'], api_id=auth['api_id'],
                               api_hash=auth['api_hash']))
        return senders

    def get_receivers(self) -> list[Receiver]:
        receivers = []
        for r in self.src:
            if (r['confirmed'] == 2) and (r['status'] == 2):
                receivers.append(Receiver(id=r['id'], name=r['name'], telegram_id=r['telegram_id']))
        return receivers

    def get_message(self, message_id: int) -> Message:
        return self.messages.get(message_id, Message.empty_message())

    def get_sender(self, sender_id: int) -> Sender:
        for s in self.src:
            if s['id'] == sender_id:
                auth = self.auth_senders.get(s['telegram_id'], {})
                if len(auth) == 2:
                    return Sender(name=s['name'], id=s['id'], telegram_id=s['telegram_id'],
                                  api_id=auth['api_id'], api_hash=auth['api_hash'])
        return Sender.empty_sender()

    def get_receiver(self, receiver_id: int) -> Receiver:
        for r in self.src:
            if (r['id'] == receiver_id) and (r['confirmed'] == 2) and (r['status'] == 2):
                return Receiver(id=r['id'], name=r['name'], telegram_id=r['telegram_id'])
        return Receiver.empty_receiver()

    def save_message(self, message: Message) -> Message:
        try:
            new_id = max(list(self.messages.keys()))
            new_id += 1
        except ValueError:
            new_id = 1
        message.id = new_id
        self.messages[message.id] = message
        return message

    def delete_message(self, message_id: int) -> bool:
        try:
            del (self.messages[message_id])
            return True
        except KeyError:
            return False


class HTTPRepository(AlmostRepository):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.src_str = ""
        self.src = []

        self.start_time = time.time()
        self.delta_time = 1
        # self._initialized = False

        # asyncio.run(self.m())
        asyncio.run(self._get_data_http())
        # self._initialized = True

    #   async def m(self):
    #       await asyncio.gather(self._get_data_http(url='http://192.168.100.148:8080/api/v1/n/user/'),
    #       self._get_data_http(url='http://192.168.100.147:8080/api/v1/n/user/'))
    #       #task_a =asyncio.create_task(self._get_data_http(url='http://192.168.100.148:8080/api/v1/n/user/'))
    #       #task_b = asyncio.create_task(self._get_data_http(url='http://192.168.100.147:8080/api/v1/n/user/'))
    #       #await task_a
    #       #await task_b

    def _check_stale(self):
        if time.time() - self.start_time >= self.delta_time:
            asyncio.run(self._get_data_http())

    async def _get_data_http(self):
        try:
            async with aiohttp.ClientSession() as session:
                # async with session.get('http://192.168.100.148:8080/api/v1/n/user/') as response:
                async with session.get(self.url) as response:
                    response.raise_for_status()  # Raise exception for bad status
                    self.src = await response.json()  # Directly parse JSON
                    self.start_time = time.time()  # Reset refresh timer
        except aiohttp.ClientError as e:
            print(f"HTTP request failed: {e}")
            raise DataIsNotGot(e)
            # You might want to keep old data or raise an exception here
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            raise DataIsWrong(e)


if __name__ == "__main__":
    # repository = AlmostRepository()
    # print(repository.get_senders())
    # print(repository.get_receivers())
    # print(repository.get_messages())
    repository = HTTPRepository(url='http://192.168.100.147:8080/api/v1/n/user/')
    print(repository.src)
