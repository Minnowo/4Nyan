import requests
from requests.exceptions import Timeout

import base64
from urllib.parse import urlencode, parse_qsl

from core import aNyanData

env: dict = aNyanData.get_envvars()

SERVER_PORT = 721
SERVER_IP = env.get("server_ip", "0.0.0.0")
SERVER_ADDRESS = f"http://{SERVER_IP}:{SERVER_PORT}/"


def fetch_raw(url, method, **kwargs):

    try:
        return requests.request(method, url, **kwargs)

    except (ConnectionError, Timeout) as exc:

        raise exc

    except Exception as exc:

        raise Exception("Fatal error making a request to {}. {}".format(url, exc))


def fetch_json(url, method, **kwargs):

    response = fetch_raw(url, method, **kwargs)

    if response.status_code not in (200, 202):

        print(f"response status code: {response.status_code}\nreason: {response.reason}")

        return {}

    try:
        if "application/json" in response.headers.get("Content-Type", "").lower():
            return response.json()

        print("no json content type response")
        return {}
    except Exception as e:
        print(e)


def get_yt_playlist(playlist_url: list[str] = None, playlist_id: list[str] = None, encode_b64: bool = False):

    if playlist_id is None:
        playlist_id = []

    if playlist_url is None:
        playlist_url = []

    QUERY_PARAM_URL = "playlist_url"
    QUERY_PARAM_ID = "playlist_id"
    QUERY_PARAM_B64 = "b64"

    query_encoded = [(QUERY_PARAM_B64, str(encode_b64))]

    for i in playlist_url:

        if encode_b64:
            query_encoded.append((QUERY_PARAM_URL, base64.b64encode(i.encode()).decode()))

        else:
            query_encoded.append((QUERY_PARAM_URL, i))

    for i in playlist_id:

        if encode_b64:
            query_encoded.append((QUERY_PARAM_ID, base64.b64encode(i.encode()).decode()))

        else:
            query_encoded.append((QUERY_PARAM_ID, i))

    url = f"{SERVER_ADDRESS}svc/get-yt-playlist?{urlencode(query_encoded)}"

    return fetch_json(url, "get")


def get_test_single_job(print_str: str):

    url = f"{SERVER_ADDRESS}tst/single_job/{print_str}"

    fetch_raw(url, "get")


def get_test_repeating_job(print_str: str):

    url = f"{SERVER_ADDRESS}tst/repeating_job/{print_str}"

    fetch_raw(url, "get")


def get_cancel_test_jobs():
    url = f"{SERVER_ADDRESS}tst/cancel_all/"
    fetch_raw(url, "get")


import time

print(get_yt_playlist(encode_b64=True, playlist_id=["PLD4r6M35XTXPeC3vhz6w34_5ndzp0R2q4"]))
get_test_single_job("hello world")
get_test_repeating_job("Nyah OWO")

time.sleep(62)
get_cancel_test_jobs()
