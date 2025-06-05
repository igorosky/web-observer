from .web_observer import WebObserver
from .web_observer_options import WebObserverOptions
from .web_observer_api import Notification
from typing import Callable
from bs4 import BeautifulSoup, PageElement, ResultSet
from hashlib import sha256
import requests
import uuid
import sys
import imgkit
import os

class HtmlObserver(WebObserver):
  def __init__(self, options: WebObserverOptions, notify: Callable[[Notification], None],
               current_digest: str | None = None, last_response_code: int | None = None,
               path_to_images: str | None = None) -> None:
    if len(options.steps_to_get_element) > 0:
      if options.steps_to_get_element[-1].element_index is None and not options.count_elements:
        raise ValueError("Last step must have element_index set to None if count_elements is False.")
      if any(x.element_index is None for x in options.steps_to_get_element[:-1]):
        raise ValueError("All steps except the last one must have element_index set.")
    super().__init__(options, notify, last_response_code)
    self.type = 'html'
    self.current_digest = current_digest
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
      if step.element_attributes is not None:
        kwargs['attrs'] = step.element_attributes
      elements = soup.find_all(**kwargs)
      if step.element_index is not None:
        if step.element_index < 0 or step.element_index >= len(elements):
          raise IndexError(f"Element index {step.element_index} out of range for elements of length: {len(elements)}")
        if i != len(steps) - 1 and step.element_index is None:
          raise ValueError("Element index must be set for all steps except the last one where it is not required.")
        soup = elements[step.element_index]
    return soup

  @staticmethod
  def substitute_imgs(soup: BeautifulSoup, base_url: str) -> Callable[[], None]:
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
    if not content_type.startswith('text/html'):
      print(f"Response from {self.options.url} is not HTML ({content_type}), skipping.", file=sys.stderr)
      notification.error = f"Response is not HTML: {content_type}"
      self.notify(notification)
      return

    soup = BeautifulSoup(response.content, 'html.parser')
    if self.options.css_selector is not None:
      content = soup.select(self.options.css_selector)
    else:
      try:
        content = HtmlObserver.get_elements(soup, self.options.steps_to_get_element)
      except IndentationError as e:
        print(f"Error parsing HTML content from {self.options.url}: {e}", file=sys.stderr)
        return
      except IndexError as e:
        # Imposible since constructor checks this
        print(f"Error accessing element: {e}", file=sys.stderr)
        return

    if self.options.count_elements:
      if not isinstance(content, ResultSet):
        print("Count elements option is set but content is not a list.", file=sys.stderr)
        notification.error = "Count elements option is set but content is not a list."
        self.notify(notification)
        return
      digest = sha256(str(len(content)).encode('utf-8')).hexdigest()
    else:
      # At this point content should be a single element
      if not isinstance(content, ResultSet):
        element = content
      else:
        element = content[0]

      # You ask why not to omit this when we not observe images?
      # Because imgkit would not handle relative URLs correctly
      # This simply replaces them with sha256 hashes
      # And during reverse we restore URLs with base path
      reverse = HtmlObserver.substitute_imgs(element, self.options.url)
      if not self.options.observe_images:
        reverse()
        reverse = None

      digest = sha256(element.encode('utf-8')).hexdigest()

      reverse() if reverse is not None else None

    if self.current_digest is None or self.current_digest != digest:
      do_notify = True
      if self.options.take_text:
        notification.new_value = element.get_text(strip=True)
      if self.options.observe_images:
        notification.image = self.generate_view(element)
      self.current_digest = digest

    if do_notify:
      self.notify(notification)
