import logging
from abc import abstractmethod, ABC


class Observer(ABC):
    @abstractmethod
    def update(self, message: str):
        pass

class LoggerObserver(Observer):
    def update(self, message: str):
        logging.info(message)

class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def notify(self, message: str):
        for observer in self._observers:
            observer.update(message)