from abc import ABC, abstractmethod
from typing import Callable
from apscheduler.triggers.interval import IntervalTrigger
from .web_observer_api import Notification
from .web_observer_options import WebObserverOptions
from uuid import uuid4
from datetime import datetime, timedelta
import requests

DEFAULT_ACCEPRED_RESPONSE_CODES = [200]

class WebObserver(ABC):
  def __init__(self, options: WebObserverOptions,
               notify: Callable[[Notification], None], last_response_code: int | None = None) -> None:
    self.id = uuid4().hex
    self.options = options
    self.last_response_code = last_response_code
    self.notify = notify

  def request_site(self) -> requests.Response:
    session = requests.session()
    if self.options.headers is not None:
      session.headers.update(self.options.headers)
    if self.options.cookies is not None:
      session.cookies.update(self.options.cookies)
    if self.options.timeout is not None:
      session.timeout = self.options.timeout
    return session.get(self.options.url)
  
  def get_site(self, notification: Notification) -> tuple[requests.Response, bool | None]:
    ans = False

    response = self.request_site()

    notification.response_code = response.status_code
    if self.options.track_response_codes and \
      (self.last_response_code is None or self.last_response_code != response.status_code):
      ans = True
      notification.response_code_changed = True

    if (len(self.options.accepted_response_codes) != 0 or response.status_code not in DEFAULT_ACCEPRED_RESPONSE_CODES) \
      and response.status_code not in self.options.accepted_response_codes:
      notification.response_code_not_accepted = True
      ans = None
    return response, ans
  
  @abstractmethod
  def check(self) -> None:
    pass

  def get_interval(self) -> IntervalTrigger:
    return IntervalTrigger(seconds=self.options.interval, start_date=datetime.now() + timedelta(seconds=1))

  def get_id(self) -> str:
    return self.id
