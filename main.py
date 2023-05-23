import requests
import os
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple
# API token
api_token = os.environ.get("api_token")

# The endpoint URL for the Clash Royale API
api_url = "https://api.clashroyale.com/v1"

# The player tag of the player you want to get information for
player_tag = "%238CQU9PY8"

# Set the headers for the API request
headers = {"Accept": "application/json", "Authorization": "Bearer " + api_token}

# Get the player's battle log
#TODO figure out how to get more than 25 previous battles (if possible)
response = requests.get("https://api.clashroyale.com/v1/players/" + player_tag + "/battlelog", headers=headers)

def populate_maps(deck: list, one_card: dict, two_card: dict) -> Tuple[dict, dict]:
    two_card_combinations = list(combinations(deck, 2))
    # Iterate through all possible two card combinations
    # populate freq map
    for card_pairing in two_card_combinations:
        if card_pairing in two_card:
            two_card[card_pairing] += 1
        else:
            two_card[card_pairing] = 1
    
    # populate freq map
    for card in deck:
        if card in one_card:
            one_card[card] += 1
        else:
            one_card[card] = 1

    return one_card, two_card

#TODO determine parameters for this function, and how to differentiate between
# the maps passed in (two_card vs one_card vs something else maybe?)
def make_plot(map: dict, x_label: str , y_label: str, title: str, two_card: bool) -> None:

    sorted_map = sorted(map.items(), key= lambda x: x[1], reverse=True)
    labels = [sorted_map[i][0] for i in range(len(sorted_map))]
    values = [sorted_map[i][1] for i in range(len(sorted_map))]


    if two_card:
        labels = [f"{k[0]} \n {k[1]}" for k in labels]

    sns.set_style("darkgrid")

    fig, ax = plt.subplots(figsize=(10, 7.5))
    sns.barplot(x=labels[:10], y=values[:10], palette="Set2")

    ax.set_xlabel(x_label, fontsize=10)
    ax.set_ylabel(y_label, fontsize=10)
    ax.set_title(title, fontsize=16)

    plt.setp(ax.get_xticklabels(), fontsize=7)
    plt.show()


def main():
    # If the request was successful, process the battle log
    if response.status_code == 200:
        battle_log = response.json()

        # Create a dictionary to store the count of each two card combination
        card_combinations_lost: dict[Tuple[str, str], int] = {}
        card_combinations_win: dict[Tuple[str, str], int] = {}
        # Create a dictionary to store the count of cards
        card_counts_lost: dict[str, int] = {}
        card_counts_win: dict[str, int] = {}



        c = 0
        # Iterate through each battle in the player's battle log
        for battle in battle_log:
            c += 1
            if battle["type"] == "PvP":
                # Get the player's deck and the opponent's deck
                player_deck = [card["name"] for card in battle["team"][0]["cards"]]
                opponent_deck = [card["name"] for card in battle["opponent"][0]["cards"]]
                # Check if the player lost the battle
                if battle["team"][0]["trophyChange"] < 0:
                    card_counts_lost, card_combinations_lost = populate_maps(opponent_deck, card_counts_lost, card_combinations_lost)
                # player won the game 
                elif battle["team"][0]["trophyChange"] > 0:
                    card_counts_win, card_combinations_win = populate_maps(opponent_deck, card_counts_win, card_combinations_win)


        sorted_combinations_loss = sorted(card_combinations_lost.items(), key=lambda x: x[1], reverse=True)
        print("The two card combinations that", player_tag, "loses to most often are:")
        for i in range(min(len(sorted_combinations_loss), 10)):
            print(sorted_combinations_loss[i][0], "-", sorted_combinations_loss[i][1], "times")
        
        sorted_combinations_win = sorted(card_combinations_win.items(), key=lambda x: x[1], reverse=True)
        print("The two card combinations that", player_tag, "wins against the most often are:")
        for i in range(min(len(sorted_combinations_win), 10)):
            print(sorted_combinations_win[i][0], "-", sorted_combinations_win[i][1], "times")

        #TODO

        make_plot(card_combinations_lost, "Card Combinations", "Frequency", "Card Combination Lost to Frequencies", two_card=True)
        make_plot(card_combinations_win, "Card Combinations", "Frequency", "Card Combination Frequencies Won to", two_card=True)
        make_plot(card_counts_win, "Cards", "Frequency", "Card Frequencies Won", two_card=False)
        make_plot(card_counts_lost, "Cards", "Frequency", "Card Frequencies Lost", two_card=False)

    else:
        print("Error getting player information. Status code:", response.status_code)



if __name__ == "__main__":
    main()
