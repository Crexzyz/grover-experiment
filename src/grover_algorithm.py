from abc import (
    ABC,
    abstractmethod
)

class GroverAlgorithm(ABC):
    @abstractmethod
    def PrepareStates(self):
        pass

    @abstractmethod
    def Oracle(self):
        pass

    @abstractmethod
    def Diffuser(self):
        pass

    @abstractmethod
    def Measure(self):
        pass

    @abstractmethod
    def Build(self):
        pass