class Notification:
  observer_id: int
  new_value: str | None = None
  image: str | None = None
  response_code: int | None = None
  response_code_not_accepted: bool = False
  response_code_changed: bool = False
  error: str | None = None
  
  def __init__(self, observer_id: int) -> None:
    self.observer_id = observer_id

  def __repr__(self) -> str:
    return (f"Notification(observer_id={self.observer_id}, new_value={self.new_value}, "
            f"image={self.image}, response_code={self.response_code}, "
            f"response_code_not_accepted={self.response_code_not_accepted}, "
            f"response_code_changed={self.response_code_changed}, error={self.error})")
