from .observer import Observer
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from bs4 import BeautifulSoup
import requests

class SimpleObserver(Observer):
  def __init__(self, url: str, interval: int, id: str):
    self.url = url
    self.interval = interval
    self.last_check = None
    self.id = id

  def check(self) -> None:
    try:
      response = requests.get(self.url)
      if response.status_code != 200:
        print(f"URL {self.url} returned status code {response.status_code}.")
        return
      print(f"URL {self.url} is reachable.")
      soup = BeautifulSoup(response.content, 'html.parser')
      element = soup.find(id=self.id)
      if element is None:
        print(f"Element with id {self.id} not found on {self.url}.")
        return
      print(f"Element with id {self.id} found on {self.url}: {element.text}")
    except requests.exceptions.RequestException as e:
      print(f"Error checking URL {self.url}: {e}")
  
  def get_interval(self) -> IntervalTrigger:
    return IntervalTrigger(seconds=self.interval, start_date=datetime.now())
  
  def get_id(self) -> str:
    return '1'
