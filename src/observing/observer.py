from abc import ABC, abstractmethod
from apscheduler.triggers.interval import IntervalTrigger
from typing import Any

class Observer(ABC):
  @abstractmethod
  def check(self) -> None:
    pass

  @abstractmethod
  def get_interval(self) -> IntervalTrigger:
    pass

  @abstractmethod
  def get_id(self) -> Any:
    pass
