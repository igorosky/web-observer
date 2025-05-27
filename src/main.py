from observing.image_observer import ImageObserver
from observing.web_observer_scheduler import WebObserverScheduler
from observing.html_observer import HtmlObserver
from observing.web_observer_options import WebObserverOptions

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
  web_observer.add_observer(observer)
  web_observer.add_observer(img_observer)
  while True:
    pass

if __name__ == "__main__":
  main()
