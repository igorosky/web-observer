from observing.image_observer import ImageObserver
from observing.web_observer_scheduler import WebObserverScheduler
from observing.html_observer import HtmlObserver
from observing.web_observer_options import WebObserverOptions
from observing.json_observer import JsonObserver

def main() -> None:
  print("Starting web observer...")
  web_observer = WebObserverScheduler(cores=10)

  observer = HtmlObserver(WebObserverOptions(id=1, url="https://abc.com", interval=5, steps_to_get_element=[
    WebObserverOptions.StepToGetElement(element_type="span", element_class="navButton__text ttc tc dib", element_index=0),
  ]), notify=lambda notification: print(f"Notification: {notification}"))

  img_observer = ImageObserver(WebObserverOptions(id=2,
    url='https://i.natgeofe.com/n/548467d8-c5f1-4551-9f58-6817a8d2c45e/NationalGeographic_2572187_16x9.jpg?w=1200',
    interval=15, observe_images=True),
    notify=lambda notification: print(f"Image Notification: {notification}"), path_to_images='imgs')

  json_observer = JsonObserver(WebObserverOptions(id=3, url="https://jsonplaceholder.typicode.com/posts/1",
      interval=10, steps_to_get_element=[
      WebObserverOptions.StepToGetElement(element_id="body"),
    ], take_text=True), notify=lambda notification: print(f"JSON Notification: {notification}"))

  web_observer_not_found = HtmlObserver(WebObserverOptions(id=4,
    url="https://example.com/nonexistentpage", interval=7), lambda notification: print(f"Not-found page notification: {notification}"))

  web_observer_not_exists = HtmlObserver(WebObserverOptions(id=5,
    url="https://thispagedoesnotexist.com", interval=10), lambda notification: print(f"Non-existent page notification: {notification}"))

  web_observer_not_exists_ip = HtmlObserver(WebObserverOptions(id=5,
    url="http://12.12.12.3/", interval=10), lambda notification: print(f"Non-existent page notification: {notification}"))

  web_observer.add_observer(observer)
  web_observer.add_observer(img_observer)
  web_observer.add_observer(json_observer)
  web_observer.add_observer(web_observer_not_found)
  web_observer.add_observer(web_observer_not_exists)
  web_observer.add_observer(web_observer_not_exists_ip)
  while True:
    pass

if __name__ == "__main__":
  main()
