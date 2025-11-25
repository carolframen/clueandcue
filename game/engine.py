# Clue & Cue
# ---------------------------- IMPORTS ------------------------------- #
from database import cards
import random



# ---------------------------- PLAYER ------------------------------- #
class Player:
    def __init__(self,username):
        self.user = username
        self.team = None
        self.initial_cards = [] # Will hold the 8 cards the player can choose from
        self.selected_cards = [] # Will hold the 5 cards the player selects



# ---------------------------- ROOM ------------------------------- #
class Room:
    def __init__(self, roomcode,creator_username):
        self.roomcode = roomcode

        # Keeps the match's full card list
        self.round_one_cards = []
        self.round_two_cards = []
        self.round_three_cards = []

        # Players and Teams
        self.players = []
        self.team_one = []
        self.team_two = []

        # Info to keep the game going
        self.round = 1
        self.scores = {1: 0, 2: 0}
        self.current_clue_giver = None
        self.time_left = 30
        self.current_card_index = 0

        # Adds the creator to the player list and marks them as the creator
        creator = Player(creator_username)
        self.players.append(creator)
        self.opener = creator

    def add_player(self, username):
        new_player = Player(username) # Creates a new player
        self.players.append(new_player) # Adds the new player to the players list
        return new_player

    def create_teams(self):
        # Splits the players in two teams and assigns the team to each player
        for i, player in enumerate(self.players):
            if i % 2 == 0:
                self.team_one.append(player)
                player.team = 1
            else:
                self.team_two.append(player)
                player.team = 2

    def deal_cards(self):
        num_of_cards = len(self.players)*8 # Sets the num of cards needed to deal
        cards_to_deal = random.sample(cards,num_of_cards) # Creates the dealing pool

        for player in self.players:
            hand = cards_to_deal[:8] # Select 8 cards to give to the player
            player.initial_cards = hand # Assigns the cards to the player
            cards_to_deal = cards_to_deal[8:] # Remove those 8 cards from the options

    def submit_selection(self, player_username, selected_cards_list):
        for player in self.players:
            if player.user == player_username:
                # Assign the list of cards to the player's attribute
                player.selected_cards = selected_cards_list
                print(f"Successfully recorded 5 cards for {player_username}.")


                return True

        print(f"ERROR: Player {player_username} not found in room.")
        return False

    def compile_match_list(self):
        for player in self.players:
            if len(player.selected_cards) != 5:
                break
        else:
            master_list = []
            for p in self.players:
                # Add all 5 cards from the player to the temporary list
                master_list.extend(p.selected_cards)

            # Assign the list to all rounds
            self.round_one_cards = master_list[:]
            self.round_two_cards = master_list[:]
            self.round_three_cards = master_list[:]
















# ---------------------------- TESTING ------------------------------- #
# Create game
test = Room(1234, "carol")

# Add players
test.add_player("manda")
test.add_player("mand")
test.add_player("mari")
test.add_player("haack")

# Split them into teams
test.create_teams()

# Check the teams
team_one_users = [player.user for player in test.team_one]
team_two_users = [player.user for player in test.team_two]
print(f"Team One: {team_one_users} | Team Two: {team_two_users}")
print(f"{test.players[0].user}'s team is {test.players[0].team}")

# Checking cards dealt
test.deal_cards()
print("--- All cards dealt. Selection phase begins. ---")

print(f"{test.players[0].user} has {len(test.players[0].initial_cards)} cards. They are: {test.players[0].initial_cards}")







