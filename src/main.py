from observing.web_observer_scheduler import WebObserver
from observing.simple_observer import SimpleObserver

def main() -> None:
  web_observer = WebObserver(cores=10)
  observer = SimpleObserver(url="https://abc.com", interval=5, id="live tv")
  web_observer.add_observer(observer)
  while True:
    pass

if __name__ == "__main__":
  main()
