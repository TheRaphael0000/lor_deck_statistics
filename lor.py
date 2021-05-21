import glob
import json
import os


folder = os.path.join(os.path.dirname(__file__), "lor")

def get_cards():
    filenames = glob.glob(os.path.join(folder, "set*-en_us.json"))

    cards = {}
    for filename in filenames:
        cards_json = json.loads(open(filename, "rb").read())
        cards_by_code = {i["cardCode"]:i for i in cards_json}
        cards.update(cards_by_code)
    return cards
