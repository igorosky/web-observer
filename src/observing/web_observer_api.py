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
