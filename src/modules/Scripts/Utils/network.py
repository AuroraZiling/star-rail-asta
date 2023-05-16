import requests


def is_connected():
    try:
        requests.get("https://bing.com")
    except requests.exceptions.ConnectionError:
        return False
    return True
