import json

class WebObserverOptions:
  class StepToGetElement:
    def __init__(self,
                element_type: str | None = None,
                element_id: str | None = None,
                element_class: str | None = None,
                element_index: int | None = 0) -> None:
      self.element_type: str | None = element_type
      self.element_id: str | None = element_id
      self.element_class: str | None = element_class
      # If element_index is None it means that the step is the last one and count element must be used
      self.element_index: int | None = element_index

  def __init__(self,
               id: int,
               url: str,
               interval: int,
               accepted_response_codes: list[int] | None = None,
               track_response_codes: bool = False,
               css_selector: str | None = None,
               steps_to_get_element: list[StepToGetElement] | None = None,
               observe_images: bool = False,
               take_text: bool = False,
               generate_view: bool = False,
               count_elements: bool = False,
               cookies: dict[str, str] | None = None,
               headers: dict[str, str] | None = None,
               timeout: int | None = None) -> None:
    self.id: int = id
    self.url: str = url
    self.interval: int = interval
    # Empty list means 200s are accepted
    self.accepted_response_codes: list[int] = accepted_response_codes if accepted_response_codes is not None else []
    self.track_response_codes: bool = track_response_codes
    self.css_selector: str | None = css_selector
    self.steps_to_get_element: list[WebObserverOptions.StepToGetElement] = steps_to_get_element if steps_to_get_element is not None else []
    self.observe_images: bool = observe_images
    self.take_text: bool = take_text
    self.generate_view: bool = generate_view
    self.count_elements: bool = count_elements
    self.cookies: dict[str, str] | None = cookies
    self.headers: dict[str, str] | None = headers
    self.timeout: int | None = timeout

  def to_json(self) -> str:
    return json.dumps(self, default=lambda o: o.__dict__)

  @staticmethod
  def from_json(json_str: str):
    return json.loads(json_str, object_hook=lambda d: WebObserverOptions(**d) if 'url' in d else WebObserverOptions.StepToGetElement(**d))
