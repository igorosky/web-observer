from .web_observer import WebObserver
from .web_observer_options import WebObserverOptions
from .web_observer_api import Notification
from typing import Callable
from hashlib import sha256
from uuid import uuid4
import requests
import sys
import os

class ImageObserver(WebObserver):
  def __init__(self, options: WebObserverOptions, notify: Callable[[Notification], None],
               current_digest: str | None = None, last_response_code: int | None = None,
               path_to_images: str | None = None) -> None:
    if len(options.steps_to_get_element) > 0:
      if options.steps_to_get_element[-1].element_index is None and not options.count_elements:
        raise ValueError("Last step must have element_index set to None if count_elements is False.")
      if any(x.element_index is None for x in options.steps_to_get_element[:-1]):
        raise ValueError("All steps except the last one must have element_index set.")
    super().__init__(options, notify, last_response_code)
    self.type = 'img'
    self.current_digest = current_digest
    if path_to_images is None:
      path_to_images = os.getcwd()
    os.makedirs(path_to_images, exist_ok=True)
    self.path_to_images = path_to_images

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
    if not content_type.lower().startswith('image/'):
      print(f"Response from {self.options.url} is not na image ({content_type}), skipping.", file=sys.stderr)
      notification.error = f"Response is not an image: {content_type}"
      self.notify(notification)
      return

    digest = sha256(response.content).hexdigest()
    if self.current_digest is None or self.current_digest != digest:
      self.current_digest = digest
      if self.options.observe_images:
        img_path = os.path.join(self.path_to_images, f"{uuid4().hex}.{content_type.split('/')[-1]}")
        with open(img_path, 'wb') as img_file:
          img_file.write(response.content)
        notification.image_path = img_path

    if do_notify:
      self.notify(notification)
