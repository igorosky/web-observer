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

def notify(id, image: str | None = None) -> None:
  """
  Notify the user about the change in the observed element.
  This is a placeholder function that should be implemented to send notifications.
  """
  if image is not None:
    print(f"Notification for observer {id}: Change detected with image {image}")
  else:
    print(f"Notification for observer {id}: Change detected without image")

class SimpleObserver(Observer):
  def __init__(self, options: WebObserverOptions, current_digest: str | None = None) -> None:
    if len(options.steps_to_get_element) > 0: 
      if options.steps_to_get_element[-1].element_index is None and not options.count_elements:
        raise ValueError("Last step must have element_index set to None if count_elements is False.")
      if any(x.element_index is None for x in options.steps_to_get_element[:-1]):
        raise ValueError("All steps except the last one must have element_index set.")
    self.options = options
    self.id = uuid.uuid4().hex
    self.current_digest = current_digest

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

  @staticmethod
  def generate_view(soup: BeautifulSoup, base_url: str, target: str | None = None) -> str:
    if target is None:
      target = f"{uuid.uuid4().hex}.html"
    imgkit.from_string(soup.string, target, options={'format': 'jpg', 'quiet': ''})
    return target

  def check(self) -> None:
    print(f"Checking URL: {self.options.url} with id: {self.id}")
    try:
      response = requests.get(self.options.url)
    except requests.exceptions.RequestException as e:
      print(f"Error checking URL {self.options.url}: {e}")
    if self.options.track_response_codes:
      pass  # TODO(@Igor Zaworski)
      print('self.options.track_response_codes')
      return
    if (len(self.options.accepted_response_codes) != 0 or response.status_code != 200) \
      and response.status_code not in self.options.accepted_response_codes:
      pass  # TODO(@Igor Zaworski)
      print(f"Response code {response.status_code} not accepted for {self.options.url}.")
      return

    try:
      content = SimpleObserver.get_elements(BeautifulSoup(response.content, 'html.parser'),
                                            self.options.steps_to_get_element)
    except IndentationError as e:
      print(f"Error parsing HTML content from {self.options.url}: {e}", file=sys.stderr)
      return
    except IndexError as e:
      # Imposible since constructor checks this
      print(f"Error accessing element: {e}", file=sys.stderr)
      return

    if self.options.count_elements:
      pass  # TODO(@Igor Zaworski)
      print(f"Count elements is not implemented for {self.options.url}.")
      return
    
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
    if self.current_digest is None or self.current_digest != digest:
      self.current_digest = digest
    
    reverse() if reverse is not None else None

    if element is None:
      print(f"Element with id {self.id} not found on {self.options.url}.")
      return
    print(f"Element with id {self.id} found on {self.options.url}: {element.text}")

  def get_interval(self) -> IntervalTrigger:
    return IntervalTrigger(seconds=self.options.interval, start_date=datetime.now())

  def get_id(self) -> str:
    return self.id
