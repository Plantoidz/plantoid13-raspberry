## HTTP fake-feed via counter on feed.plantoid.org - mirrors a blockchain Deposit

import os
import requests

HTTP_FEED_AMOUNT =  1_000_000_000_000_000 # 0.001 ETH -> 20s at the testnet rate in activatePlantoid
SERVER_URL = "https://feed.plantoid.org"
PLANTOID_N = "13"

HTTP_TOKEN_OFFSET = 100000

_last_counter = None


def _get_counter():

    r = requests.get(SERVER_URL + "/counter.php",
                    params={"n": PLANTOID_N}, 
                    timeout=10)
    r.raise_for_status()

    body = r.text.strip()

    if not body: 
        return 0
    else: 
        return int(body)


def setup():
    # baseline to current counter so we only react to feeds arriving after startup
    global _last_counter
    try:
        _last_counter = _get_counter()
    except Exception:
        _last_counter = 0
    print(f"[http feed] ready, server={SERVER_URL}, baseline={_last_counter}")


def check_for_deposits():

    # return (token_Id, amount) like the indexer/RPC path, or None

    global _last_counter
    count = _get_counter()

    if _last_counter is None:
        _last_counter = count
        return None

    if count <= _last_counter:
        return None

    _last_counter = count # advance baseline - react to one feed

    token_Id = str(HTTP_TOKEN_OFFSET + count)
    print(f"[http feed] tokenId #{token_Id} has been fed  (counter={count})")

    return (str(token_Id), HTTP_FEED_AMOUNT)


def publish_video(token_Id, movie_path):

    # post the finished video to plantoid.org, return the public URL to QR

    if not movie_path or not os.path.isfile(movie_path):
        print("[http feed] no movie to publish")
        return None

    try:
        with open(movie_path, "rb") as f:
            r = requests.post(
                SERVER_URL + "/video.php",
                files={"file": (f"{PLANTOID_N}-{token_Id}.mp4", f, "video/mp4")},
                data={"token_id": token_Id, "plantoid": PLANTOID_N},
                timeout=120
            )
            r.raise_for_status()

            url = r.text.strip()
            print("[http feed] published at ---> " + url)
            return url
    except Exception as e:
        print("[http feed] publish failed: " + str(e))
        return None