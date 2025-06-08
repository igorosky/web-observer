import logging

import requests


def send_gotify_message(url, token, title, message, priority=5):
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
            logging.info(f"Wiadomość wysłana pomyślnie: {title}")
            return True
        else:
            logging.info(f"Błąd wysyłania: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logging.info(f"Błąd połączenia: {e}")
        return False


