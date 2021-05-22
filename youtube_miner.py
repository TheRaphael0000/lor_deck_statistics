import json
import os
from urllib.request import urlopen, Request
from collections import defaultdict
import re

from key import key

FILENAME = "playlistItems.json"
PLAYLIST = "PL_NQ1VZHmIfY5g0CPrJEEQ213nw2wdsSw"


def playlistItems(params):
    model = fr"https://www.googleapis.com/youtube/v3/playlistItems?"
    p = "&".join([fr"{k}={v}" for k, v in params.items()])
    url = model + p
    text = urlopen(url).read().decode("utf8")
    js = json.loads(text)
    return js


def playlistToJson():
    params = {
        "part": "snippet",
        "key": key,
        "playlistId": PLAYLIST,
        "maxResults": 50,
    }
    items = []

    hasNext = True
    while hasNext:
        js = playlistItems(params)
        try:
            params["pageToken"] = js["nextPageToken"]
        except KeyError:
            hasNext = False

        items.extend(js["items"])
        print(len(items))

    # keep every video only once
    unique_items = []
    ids = set()
    for i in items:
        id = i["snippet"]["resourceId"]["videoId"]
        if id not in ids:
            unique_items.append(i)
        ids.add(id)

    open(FILENAME, "w").write(json.dumps(unique_items))


def codes_from_playlists():
    if not os.path.isfile(FILENAME):
        playlistToJson()
    items = json.load(open(FILENAME))
    codes = defaultdict(list)
    for i in items:
        d = i["snippet"]["description"]
        ms = re.findall(r"[A-Z0-9]{35,120}", d)
        if len(ms) > 0:
            for mi in ms:
                codes[mi].append(i)
    return codes
