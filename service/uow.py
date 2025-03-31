from __future__ import annotations
import abc
import sqlite3

from adapters.repository import AbstractRepository, FakeRepository, AlmostRepository, HTTPRepository


class AbstractUnitOfWork(abc.ABC):
    repository: AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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

    @abc.abstractmethod
    def close(self):
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

    def close(self):
        print("close")


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.repository = FakeRepository()

    def _commit(self):
        print("Fake commit")

    def rollback(self):
        print("Fake rollback")

    def close(self):
        print("Fake close")


class AlmostUnitOfWork(AbstractUnitOfWork):
    repository:AlmostRepository
    def __init__(self,conn:sqlite3.Connection):
        self.repository = AlmostRepository(conn=conn)

    def _commit(self):
        print("Almost commit")

    def rollback(self):
        print("Almost rollback")

    def close(self):
        print("Almost close")


class HTTPUnitOfWork(AbstractUnitOfWork):
    repository: HTTPRepository

    def __init__(self, url,conn:sqlite3.Connection):
        self.repository = HTTPRepository(url,conn=conn)
        self._initialized = False

    async def _initialize(self):
        """Явная инициализация"""
        if not self._initialized:
            await self.repository.initialize()
            self._initialized = True

    async def __aenter__(self):
        if hasattr(self, '_initialize'):
            await self._initialize()
        return self


    def _commit(self):
        print("HTTP commit")

    def rollback(self):
        print("HTTP rollback")

    def close(self):
        print("HTTP close")
