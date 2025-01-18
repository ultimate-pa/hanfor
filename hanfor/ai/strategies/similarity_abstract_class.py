from abc import ABC, abstractmethod
from typing import Tuple


class SimilarityAlgorithm(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the similarity algorithm (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def standard_threshold(self) -> float:
        """Standard similarity threshold (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the similarity algorithm (visible in Hanfor)"""
        pass

    @property
    @abstractmethod
    def threshold_interval(self) -> Tuple[float, float]:
        """Threshold interval of the similarity algorithm"""
        pass

    @abstractmethod
    def compare(self, str1: str, str2: str, threshold: float) -> (bool, float):
        """
        Compares two strings and determines their similarity based on the given threshold.
        return: ([bool] if meets or exceeds the threshold && [float] the calculated similarity score)
        """
        pass
