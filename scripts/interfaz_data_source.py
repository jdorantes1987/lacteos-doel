from abc import ABC, abstractmethod

class IDataSource(ABC):
    @abstractmethod
    def get_celulas_activas(self):
        pass
    
    @abstractmethod
    def get_liderazgo(self):
        pass
