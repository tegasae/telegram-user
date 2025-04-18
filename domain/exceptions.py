class CommonException(Exception):
    base_message = f''

    def __init__(self, message=''):
        self.m = message
        self.create_message()
        super().__init__(self.base_message)

    def create_message(self):
        self.base_message = f'{self.m}'


class SenderNotFound(CommonException):
    def create_message(self):
        self.base_message = f'The sender isn\'t found{self.m}'

class MessageNotFound(CommonException):
    def create_message(self):
        self.base_message = f'The message isn\'t found{self.m}'


class DataIsNotGot(CommonException):
    def create_message(self):
        self.base_message = f'The data is not got {self.m}'

class DataIsWrong(CommonException):
    def create_message(self):
        self.base_message = f'The data is wrong {self.m}'


class AuthRequired(CommonException):
    def create_message(self):
        self.base_message = f'Auth required'





