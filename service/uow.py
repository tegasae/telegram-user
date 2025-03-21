from __future__ import annotations
import abc

from adapters.repository import AbstractRepository, FakeRepository


class AbstractUnitOfWork(abc.ABC):
    repository: AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        print("commit")

        self._commit()
        # Simulate publishing events

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        print("rollback")

        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, connection, url):
        super().__init__()
        self.connection = connection
        self.url = url

    def _commit(self):
        print("commit")

    def rollback(self):
        print("rollback")


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.repository = FakeRepository()

    def _commit(self):
        print("Fake commit")

    def rollback(self):
        print("Fake rollback")
