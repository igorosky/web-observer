from .observer import Observer
from .web_observer_options import WebObserverOptions
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from bs4 import BeautifulSoup, PageElement, ResultSet
from hashlib import sha256
import requests
import uuid
import sys
import imgkit
import os

DEFAULT_ACCEPRED_RESPONSE_CODES = [200]

class Notification:
  observer_id: int
  new_value: str | None = None
  image: str | None = None
  response_code: int | None = None
  response_code_not_accepted: bool = False
  response_code_changed: bool = False
  
  def __init__(self, observer_id: int) -> None:
    self.observer_id = observer_id

def notify(notification: Notification) -> None:
  """
  `Notify` the user about the change in the observed element.
  This is a placeholder function that should be implemented to send notifications.
  """
  if notification.image is not None:
    print(f"Notification for observer {notification.observer_id}: Change detected with image {notification.image}")
  else:
    print(f"Notification for observer {notification.observer_id}: Change detected without image")

def update_digest(id: str, new_digest: str) -> None:
  """
  Update the current digest for the observer with the given id.
  This is a placeholder function that should be implemented to update the digest in a database or cache.
  """
  print(f"Updating digest for observer {id} to {new_digest}")

class SimpleObserver(Observer):
  def __init__(self, options: WebObserverOptions, current_digest: str | None = None,
               last_response_code: int | None = None, path_to_images: str | None = None) -> None:
    if len(options.steps_to_get_element) > 0: 
      if options.steps_to_get_element[-1].element_index is None and not options.count_elements:
        raise ValueError("Last step must have element_index set to None if count_elements is False.")
      if any(x.element_index is None for x in options.steps_to_get_element[:-1]):
        raise ValueError("All steps except the last one must have element_index set.")
    self.options = options
    self.id = uuid.uuid4().hex
    self.current_digest = current_digest
    self.last_response_code = last_response_code
    if path_to_images is None:
      path_to_images = os.getcwd()
    os.makedirs(path_to_images, exist_ok=True)
    self.path_to_images = path_to_images

  @staticmethod
  def get_elements(soup: BeautifulSoup, steps: list[WebObserverOptions.StepToGetElement]
                   ) -> ResultSet[PageElement] | PageElement:
    for i, step in enumerate(steps):
      kwargs = {}
      if step.element_type is not None:
        kwargs['name'] = step.element_type
      if step.element_class is not None:
        kwargs['class_'] = step.element_class
      if step.element_id is not None:
        kwargs['id'] = step.element_id
      if step.element_index is not None:
        kwargs['limit'] = step.element_index
      elements = soup.find_all(**kwargs)
      if step.element_index is not None:
        if step.element_index < 0 or step.element_index >= len(elements):
          raise IndexError(f"Element index {step.element_index} out of range for elements of length: {len(elements)}")
        if i != len(steps) - 1 and step.element_index is None:
          raise ValueError("Element index must be set for all steps except the last one where it is not required.")
        soup = elements[step.element_index]
    return soup

  @staticmethod
  def substitute_imgs(soup: BeautifulSoup, base_url: str) -> callable:
    replacements = []
    for img in soup.find_all('img'):
      src = img['src']
      if not src.startswith('http'):
        src = requests.compat.urljoin(base_url, src)
      replacements.append((img, src))
      image = requests.get(src)
      img['src'] = sha256(image.content).hexdigest()
    def revert():
      for img, src in replacements:
        img['src'] = src
    return revert

  def generate_view(self, soup: BeautifulSoup, target: str | None = None) -> str:
    if target is None:
      target = os.path.join(self.path_to_images , f"{uuid.uuid4().hex}.jpg")
    imgkit.from_string(soup.string, target, options={'format': 'jpg', 'quiet': ''})
    return target

  def request_site(self) -> requests.Response:
    session = requests.session()
    if self.options.headers is not None:
      session.headers.update(self.options.headers)
    if self.options.cookies is not None:
      session.cookies.update(self.options.cookies)
    if self.options.timeout is not None:
      session.timeout = self.options.timeout
    return session.get(self.options.url)

  def check(self) -> None:
    print(f"Checking URL: {self.options.url} with id: {self.id}")
    notification = Notification(self.options.id)
    do_notify = False

    try:
      response = self.request_site()
    except requests.exceptions.RequestException as e:
      print(f"Error checking URL {self.options.url}: {e}")

    notification.response_code = response.status_code
    if self.options.track_response_codes and \
      (self.last_response_code is None or self.last_response_code != response.status_code):
      do_notify = True
      notification.response_code_changed = True

    if (len(self.options.accepted_response_codes) != 0 or response.status_code not in DEFAULT_ACCEPRED_RESPONSE_CODES) \
      and response.status_code not in self.options.accepted_response_codes:
      notification.response_code_not_accepted = True
      notify(notification)
      return

    soup = BeautifulSoup(response.content, 'html.parser')
    if self.options.css_selector is not None:
      content = soup.select(self.options.css_selector)
    else:
      try:
        content = SimpleObserver.get_elements(soup, self.options.steps_to_get_element)
      except IndentationError as e:
        print(f"Error parsing HTML content from {self.options.url}: {e}", file=sys.stderr)
        return
      except IndexError as e:
        # Imposible since constructor checks this
        print(f"Error accessing element: {e}", file=sys.stderr)
        return

    if self.options.count_elements:
      digest = sha256(str(len(content)).encode('utf-8')).hexdigest()
    else:
      # At this point content should be a single element
      element: PageElement = content

      # You ask why not to omit this when we not observe images?
      # Because imgkit would not handle relative URLs correctly
      # This simply replaces them with sha256 hashes
      # And during reverse we restore URLs with base path
      reverse = SimpleObserver.substitute_imgs(element, self.options.url)
      if self.options.observe_images:
        reverse()
        reverse = None

      element.get_text(strip=True)
      digest = sha256(element.encode('utf-8')).hexdigest()

      reverse() if reverse is not None else None

    if self.current_digest is None or self.current_digest != digest:
      do_notify = True
      if self.options.take_text:
        notification.new_value = element.get_text(strip=True)
      if self.options.observe_images:
        notification.image = self.generate_view(element)
      update_digest(self.id, digest)
      self.current_digest = digest

    if do_notify:
      notify(notification)

  def get_interval(self) -> IntervalTrigger:
    return IntervalTrigger(seconds=self.options.interval, start_date=datetime.now())

  def get_id(self) -> str:
    return self.id
