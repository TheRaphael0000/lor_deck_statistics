import json
import re
from collections import defaultdict, Counter
from lor_deckcodes import LoRDeck, CardCodeAndCount
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from lor import get_cards
from playlistItems import codes_from_playlists

codes = codes_from_playlists()
cards = get_cards()

first_date = {}
for code, items in codes.items():
    dates = [i["snippet"]["publishedAt"] for i in items]
    dates = [datetime.fromisoformat(d[:-1]) for d in dates]
    min_date = min(dates)
    first_date[code] = min_date

sets_dates = [
    datetime(2020, 1, 23),
    datetime(2020, 4, 28),
    datetime(2020, 8, 26),
    datetime(2021, 3, 3),
]
deck_set_ids = {}
for c, d in first_date.items():
    deck_set_id = sum([d > set_date for set_date in sets_dates]) - 1
    deck_set_ids[c] = deck_set_id

codes = {c:i for c, i in codes.items() if deck_set_ids[c] == 0}

print(Counter([len(c) for c in codes.values()]).most_common())
print(len(codes))

cards_found = []

for code in codes:
    deck = LoRDeck.from_deckcode(code)
    for c in deck.cards:
        qte, code = str(c).split(":")
        if cards[code]["rarity"] == "Champion":
            cards_found.append(code)

counter = Counter(cards_found)

x = []
l = []
for c, n in counter.most_common(10):
    x.append(n)
    l.append(cards[c]["name"])

y = list(range(len(x)))[::-1]

plt.figure(figsize=(16,9), dpi=100)
plt.barh(y, x)
plt.xticks(list(range(max(x)+1)))
plt.yticks(ticks=y, labels=l)
# plt.invert_ypltis()  # labels read top-to-bottom
# plt.set_xlabel('Performance')
# plt.set_title('How fast do you want to go today?')
plt.tight_layout()
plt.savefig("plot.png")
