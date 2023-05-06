import requests
import os

# Your API token
api_token = os.environ.get("api_token")

# The endpoint URL for the Clash Royale API
api_url = "https://api.clashroyale.com/v1"

# The player tag of the player you want to get information for
player_tag = "#8CQU9PY8"

# Set the headers for the API request
headers = {"Authorization": "Bearer " + api_token}

# Get the player's battle log
response = requests.get(api_url + "/players/" + player_tag + "/battlelog", headers=headers)

# If the request was successful, process the battle log
if response.status_code == 200:
    battle_log = response.json()

    # Create a dictionary to store the count of each two card combination
    card_combinations = {}

    # Iterate through each battle in the player's battle log
    for battle in battle_log:
        if battle["type"] == "PvP" and battle["battle_type"] == "PvP":
            # Check if the player lost the battle
            if battle["result"] == "defeat":
                # Get the player's deck and the opponent's deck
                player_deck = battle["team"][0]["deck"]
                opponent_deck = battle["opponent"][0]["deck"]

                # Iterate through all possible two card combinations
                for i in range(len(player_deck)):
                    for j in range(i+1, len(player_deck)):
                        player_cards = [player_deck[i], player_deck[j]]
                        player_cards.sort()
                        opponent_cards = [card for card in opponent_deck if card not in player_cards]
                        opponent_cards.sort()
                        card_combination = tuple(player_cards + opponent_cards)
                        # Add the combination to the dictionary, or increment its count if it already exists
                        if card_combination in card_combinations:
                            card_combinations[card_combination] += 1
                        else:
                            card_combinations[card_combination] = 1

    # Sort the combinations by count and print the top 10
    sorted_combinations = sorted(card_combinations.items(), key=lambda x: x[1], reverse=True)
    print("The two card combinations that", player_tag, "loses to most often are:")
    for i in range(10):
        print(sorted_combinations[i][0], "-", sorted_combinations[i][1], "times")
else:
    print("Error getting player information. Status code:", response.status_code)
