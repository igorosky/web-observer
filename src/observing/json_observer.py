from .web_observer import WebObserver
from .web_observer_options import WebObserverOptions
from .web_observer_api import Notification
from typing import Any, Callable
from hashlib import sha256
import requests
import sys

class JsonObserver(WebObserver):
  def __init__(self, options: WebObserverOptions, notify: Callable[[Notification], None],
               current_digest: str | None = None, last_response_code: int | None = None) -> None:
    if len(options.steps_to_get_element) > 0:
      if options.steps_to_get_element[-1].element_index is None and not options.count_elements:
        raise ValueError("Last step must have element_index set to None if count_elements is False.")
      if any(x.element_index is None for x in options.steps_to_get_element[:-1]):
        raise ValueError("All steps except the last one must have element_index set.")
    super().__init__(options, notify, last_response_code)
    self.type = 'json'
    self.current_digest = current_digest

  @staticmethod
  def get_elements(data: dict[str, Any] | list[Any], steps: list[WebObserverOptions.StepToGetElement]
                   ) -> dict[str, Any] | list[Any]:
    for i, step in enumerate(steps):
      if step.element_id is not None:
        if isinstance(data, list):
          raise ValueError("Cannot use element_id on a list.")
        data = data.get(step.element_id)
      elif step.element_index is not None:
        if not isinstance(data, list):
          raise ValueError("Cannot use element_index on a dict.")
        if step.element_index < 0 or step.element_index >= len(data):
          raise IndexError(f"Element index {step.element_index} out of range for elements of length: {len(data)}")
        data = data[step.element_index]
      else:
        raise ValueError("Either element_id or element_index must be set for each step.")
    return data

  def check(self) -> None:
    print(f"Checking URL: {self.options.url} with id: {self.id}")
    notification = Notification(self.options.id)

    try:
      response, do_notify = super().get_site(notification)
    except requests.exceptions.Timeout as e:
      print(f"Timeout requesting site {self.options.url}: {e}", file=sys.stderr)
      notification.error = f"Timeout requesting site: {e}"
      self.notify(notification)
      return
    except requests.exceptions.ConnectionError as e:
      print(f"Couldn't Connect to a page {self.options.url}: {e}", file=sys.stderr)
      notification.error = f"Couldn't connect to page: {e}"
      self.notify(notification)
      return
    except requests.exceptions.RequestException as e:
      print(f"Error requesting site {self.options.url}: {e}", file=sys.stderr)
      notification.error = f"Error requesting site: {e}"
      self.notify(notification)
      return

    if do_notify is None:
      self.notify(notification)
      return

    content_type = response.headers.get('Content-Type', '<undefined>').lower()
    if not content_type.startswith('application/json'):
      print(f"Response from {self.options.url} is not JSON ({content_type}), skipping.", file=sys.stderr)
      notification.error = f"Response is not JSON: {content_type}"
      self.notify(notification)
      return

    try:
      content = response.json()
    except ValueError as e:
      print(f"Error parsing JSON from {self.options.url}: {e}", file=sys.stderr)
      notification.error = f"Invalid JSON: {e}"
      self.notify(notification)
      return
    
    try:
      content = JsonObserver.get_elements(content, self.options.steps_to_get_element)
    except (IndexError, ValueError) as e:
      print(f"Error getting elements from JSON: {e}", file=sys.stderr)
      notification.error = f"Error getting elements: {e}"
      self.notify(notification)
      return

    if self.options.count_elements:
      if not isinstance(content, list):
        print("Count elements option is set but content is not a list.", file=sys.stderr)
        notification.error = "Count elements option is set but content is not a list."
        self.notify(notification)
        return
      digest = sha256(str(len(content)).encode('utf-8')).hexdigest()
    else:
      # At this point content should be a single element
      element = content

      digest = sha256(element.encode('utf-8')).hexdigest()

    if self.current_digest is None or self.current_digest != digest:
      do_notify = True
      if self.options.take_text:
        notification.new_value = str(element)
      self.current_digest = digest

    if do_notify:
      self.notify(notification)
