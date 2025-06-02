from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from .web_observer import WebObserver
from typing import Any

class WebObserverScheduler:
  def __init__(self, cores: int = 10):
    self.executor = ThreadPoolExecutor(cores)
    self.scheduler = BackgroundScheduler(executors={'default': self.executor})
    self.scheduler.start()

  def add_observer(self, observer: WebObserver) -> None:
    job = self.scheduler.add_job(observer.check, observer.get_interval(), id=observer.get_id())
    job.coalesce = True

  def remove_observer(self, observer: WebObserver | Any) -> None:
    if isinstance(observer, WebObserver):
      observer = observer.get_id()
    self.scheduler.remove_job(observer)
