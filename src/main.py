from observing.web_observer_scheduler import WebObserver
from observing.simple_observer import SimpleObserver
from observing.web_observer_options import WebObserverOptions

def main() -> None:
  print("Starting web observer...")
  web_observer = WebObserver(cores=10)
  observer = SimpleObserver(WebObserverOptions(url="https://abc.com", interval=5, steps_to_get_element=[
    WebObserverOptions.StepToGetElement(element_type="span", element_class="navButton__text ttc tc dib", element_index=0),
  ]))
  web_observer.add_observer(observer)
  while True:
    pass

if __name__ == "__main__":
  main()
