import logging

import requests


def send_gotify_message(url, token, title, message, priority=5):
    """
    Send notification via Gotify.
    Args:
      url (str): Gotify server URL
      token (str): Gotify app token
      title (str): Notification title
      message (str): Notification body
      priority (int): Notification priority (default=5)
    """
    endpoint = f"{url}/message"

    params = {
        "token": token
    }

    data = {
        "title": title,
        "message": message,
        "priority": priority
    }

    try:
        response = requests.post(endpoint, params=params, json=data)

        if response.status_code == 200:
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        logging.info(f"Connection error: {e}")
        return False


