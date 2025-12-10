from abc import abstractmethod, ABC

from application.result.Error import Error
from application.result.Result import Result


class OutputPort(ABC):
    """
    Abstract class that is responsible for output.
    """
    @abstractmethod
    def send_output(self, measured: list[Result], model: list[Result], error: list[Error]) -> None:
        """
        Function that parses output from data and sends it to final location.
        :param measured: List of measured Result objects.
        :param model: List of model Result objects.
        :param error: List of Error objects for each Result object.
        """
        pass
