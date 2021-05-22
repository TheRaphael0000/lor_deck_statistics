import json
import re
from collections import defaultdict, Counter
import itertools

from lor_deckcodes import LoRDeck, CardCodeAndCount
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore


from lor_data_files import get_cards
from youtube_miner import codes_from_playlists

codes = codes_from_playlists()
cards_infos = get_cards()

min_date, max_date = None, None

# Keep only the first apearence of the deck
code_first_date = {}
for code, items in codes.items():
    dates = [i["snippet"]["publishedAt"] for i in items]
    dates = [datetime.fromisoformat(d[:-1]) for d in dates]
    min_date_ = min(dates)
    max_date_ = max(dates)
    if min_date is None or max_date is None:
        min_date = min_date_
        max_date = max_date_
    min_date = min(min_date, min_date_)
    max_date = max(max_date, max_date_)
    code_first_date[code] = items[dates.index(min_date_)]

print(min_date, max_date)

codes = code_first_date


def get_cards_infos_from_code(code):
    deck = LoRDeck.from_deckcode(code)
    cards = []
    for c in deck.cards:
        qte, code = str(c).split(":")
        cards.append((qte, cards_infos[code]))
    return cards


decks = [(c, get_cards_infos_from_code(c)) for c, i in codes.items()]

cards = [[card["cardCode"] for qte, card in cards] for code, cards in decks]
cards = itertools.chain(*cards)

cards_counter = dict(Counter(cards).most_common()).items()

cards_counter_by_set = defaultdict(list)

for card, n in cards_counter:
    cards_counter_by_set[cards_infos[card]["set"]].append((card, n))


def bar_plot(x, labels, title, filename):
    y = list(range(len(x)))[::-1]
    plt.figure(figsize=(10, 7), dpi=200)
    plt.grid()
    plt.barh(y, x)
    max_x = np.max(x)
    if max_x > 10:
        ticks = list(np.arange(0, max_x + 1, 5))
        plt.minorticks_on()
    else:
        ticks = np.arange(0, max_x + 1, 1)
        plt.minorticks_off()
    plt.xticks(ticks)
    plt.yticks(ticks=y, labels=labels)
    plt.xlabel(
        "Number of different decks containing this card, from the deck codes proposed on his channel")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)


champions_by_set = []
spells_by_set = []
followers_by_set = []

for set_, cards_in_set in cards_counter_by_set.items():
    print(set_)

    top_n = 25

    champions = []
    for card, n in cards_in_set:
        info = cards_infos[card]
        if info["rarity"] == "Champion":
            champions.append((n, info["name"]))
    champions_by_set.append(champions)

    spells = []
    for card, n in cards_in_set:
        info = cards_infos[card]
        if info["type"] == "Spell":
            spells.append((n, info["name"]))
    spells_by_set.append(spells)
    spells = spells[:top_n]

    followers = []
    for card, n in cards_in_set:
        info = cards_infos[card]
        if info["type"] == "Unit" and info["rarity"] != "Champion":
            followers.append((n, info["name"]))
    followers_by_set.append(followers)
    followers = followers[:top_n]

    date_format = f"up to {max_date:%B %Y}"

    title = f"MegaMogwai top champions from {set_} {date_format}"
    bar_plot(*zip(*champions), title, f"img/champs_{set_}.png")

    title = f"MegaMogwai top {top_n} spells from {set_} {date_format}"
    bar_plot(*zip(*spells), title, f"img/spells_{set_}.png")

    title = f"MegaMogwai top {top_n} followers from {set_} {date_format}"
    bar_plot(*zip(*followers), title, f"img/followers_{set_}.png")


def zscoreify(cards_by_set):
    qte_by_set = [[c[0] for c in i] for i in cards_by_set]
    qte_by_set = [zscore(i) for i in qte_by_set]
    labels_by_set = [[c[1] for c in i] for i in cards_by_set]
    qte = np.array(list(itertools.chain(*qte_by_set)))
    labels = np.array(list(itertools.chain(*labels_by_set)))
    order = np.argsort(qte)[::-1]
    qte = qte[order]
    labels = labels[order]
    return qte, labels


x, labels = zscoreify(champions_by_set)
y = list(range(len(x)))[::-1]
plt.figure(figsize=(10, 10), dpi=200)
plt.grid()
plt.barh(y, x)
plt.yticks(ticks=y, labels=labels)
plt.xlabel("Z-score")
title = f"MegaMogwai top champions with z-score across sets {date_format}"
plt.title(title)
plt.tight_layout()
plt.savefig(f"img/champs_overall.png")


def get_regions_from_deck(deck):
    regions = set()
    for qte, card in deck:
        regions.add(card["region"])
    return list(regions)


regions = list(itertools.chain(
    *[get_regions_from_deck(cards) for code, cards in decks]))
labels, x = zip(*dict(Counter(regions).most_common()).items())
colors = ["#D85754", "#F7B863", "#CE7D9C", "#089A7B",
          "#DECFA5", "#9AE2FA", "#AD5121", "#736FE7", "#CC971F"]
plt.figure(figsize=(10, 7), dpi=200)
plt.pie(x=x, labels=labels, autopct="%1.1f%%", colors=colors)
plt.title(f"MegaMogwai regions fequencies {date_format}")
plt.tight_layout()
plt.savefig(f"img/regions.png")
