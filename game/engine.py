# Clue & Cue
# ---------------------------- IMPORTS ------------------------------- #
from database import cards
import random


# ---------------------------- PLAYER ------------------------------- #
class Player:
    def __init__(self, username):
        self.user = username
        self.team = None
        self.initial_cards = []  # Will hold the 8 cards the player can choose from
        self.selected_cards = []  # Will hold the 5 cards the player selects

    def __repr__(self):
        # For testing remove later *************************
        return f"<Player: {self.user}, Team: {self.team}>"


# ---------------------------- ROOM ------------------------------- #
class Room:
    def __init__(self, roomcode, creator_username):
        self.roomcode = roomcode

        # Keeps the match's full card list
        self.round_one_cards = []
        self.round_two_cards = []
        self.round_three_cards = []

        # Players and Teams
        self.players = []
        self.team_one = []
        self.team_two = []

        # Captains
        self.team_one_captain = None
        self.team_two_captain = None
        self.current_captain_chooser = None

        # Info to keep the game going
        self.round = 1
        self.scores = {1: 0, 2: 0}
        self.current_clue_giver = None
        self.time_left = 30
        self.card_in_play = None  # The card currently being guessed

        # Adds the creator to the player list and marks them as the creator
        creator = Player(creator_username)
        self.players.append(creator)
        self.opener = creator

    def add_player(self, username):
        new_player = Player(username)  # Creates a new player
        self.players.append(new_player)  # Adds the new player to the players list
        return new_player

    def create_teams(self):
        if len(self.players) < 4:
            print(f"ERROR: Cannot start game. Minimum 4 players required, found {len(self.players)}.")
            return False  # Indicate that team creation failed

        # Reset teams for a fresh start (useful if this method is called multiple times)
        self.team_one = []
        self.team_two = []
        self.team_one_captain = None
        self.team_two_captain = None
        self.current_captain_chooser = None

        # Splits the players in two teams and assigns the team to each player
        for i, player in enumerate(self.players):
            team_number = (i % 2) + 1

            player.team = team_number

            if team_number == 1:
                self.team_one.append(player)
            else:
                self.team_two.append(player)

        # Sets team captains
        if self.team_one:
            # First player in the list becomes the captain
            self.team_one_captain = self.team_one[0]
            print(f"Team 1 Captain: {self.team_one_captain.user}")  # For testing remove later *************************

        if self.team_two:
            # First player in the list becomes the captain
            self.team_two_captain = self.team_two[0]
            print(f"Team 2 Captain: {self.team_two_captain.user}")  # For testing remove later *************************

        # Set the initial captain chooser (T1 always starts)
        self.current_captain_chooser = self.team_one_captain

        return True  # Team was created

    def deal_cards(self):
        num_players = len(self.players)
        num_of_cards_needed = num_players * 8  # Sets the num of cards needed to deal

        if len(cards) < num_of_cards_needed:
            print(f"ERROR: Not enough cards available. Need {num_of_cards_needed} cards.")
            return

        cards_to_deal = random.sample(cards, num_of_cards_needed)  # Creates the dealing pool

        for player in self.players:
            hand = cards_to_deal[:8]  # Select 8 cards to give to the player
            player.initial_cards = hand  # Assigns the cards to the player
            cards_to_deal = cards_to_deal[8:]  # Remove those 8 cards from the options

    def submit_selection(self, player_username, selected_cards_list):
        # Checks if the submitted list has the correct length
        if len(selected_cards_list) != 5:
            print(f"ERROR: {player_username} submitted {len(selected_cards_list)} cards, requires 5.")
            return False

        for player in self.players:
            if player.user == player_username:
                # Assign the list of cards to the player's attribute
                player.selected_cards = selected_cards_list
                print(f"Submission recorded for {player_username}.") # For testing remove later *****************************

                # Attempt to compile the match list after every submission
                self.compile_match_list()
                return True

        print(f"ERROR: Player {player_username} not found in room.")
        return False

    def compile_match_list(self):
        # checks if this is the last player to choose the cards
        for player in self.players:
            if len(player.selected_cards) != 5:
                break


        else:
            print(
                "\n--- All players ready. Compiling Match List... ---")  # For testing remove later *****************************
            master_list = []
            for p in self.players:
                # Add all 5 cards from the player to the temporary list
                master_list.extend(p.selected_cards)

            # Assign the list to all rounds
            self.round_one_cards = master_list[:]
            self.round_two_cards = master_list[:]
            self.round_three_cards = master_list[:]
            print(
                f"Match list compiled successfully. Total cards: {len(master_list)}")  # For testing remove later *****************************

    def set_clue_giver(self, clue_giver_username):
        for player in self.players:
            if player.user == clue_giver_username:
                self.current_clue_giver = player
                print(
                    f"Clue giver successfully set: {player.user} (Team {player.team})")  # For testing remove later *****************************

                # After setting the giver, start the turn
                self.start_turn()
                return

        print(f"ERROR: Clue giver '{clue_giver_username}' not found.")

    def start_turn(self):
        # Chooses the correct card list to play
        current_card_list = self.get_current_card_list()

        # Check if the clue giver has been set
        if not self.current_clue_giver:
            print("ERROR: Clue giver must be selected before starting the turn.")
            return

        if not current_card_list:
            print(f"Round {self.round} is complete!")  # For testing remove later *****************************
            # Add self.end_round() later
            self.end_turn()  # For now, end the turn, which rotates the chooser
            return

        # Get the card to show the player
        self.card_in_play = current_card_list[0]

        # Prints for testing remove later**************************
        print(f"\n--- Round {self.round} Turn Start ---")
        # Access the user attribute from the Player object
        print(f"Clue Giver: {self.current_clue_giver.user} (Team {self.current_clue_giver.team})")
        print(f"Current Card: {self.card_in_play}")

        # Timer logic (placeholder for SocketIO later)
        # self.time_left = 30
        # self.start_timer()

    def get_current_card_list(self):
        # Checks the round and returns the correct card list
        if self.round == 1:
            return self.round_one_cards
        elif self.round == 2:
            return self.round_two_cards
        elif self.round == 3:
            return self.round_three_cards
        else:
            return []

    def card_guessed(self):
        if not self.card_in_play:
            print("ERROR: No card in play to guess.")
            return

        # Removes the guessed card from the list
        current_card_list = self.get_current_card_list()
        guessed_card = current_card_list.pop(0)

        # Adds a point to the team
        clue_giver_team = self.current_clue_giver.team
        self.scores[clue_giver_team] += 1

        # Prints for testing remove later**************************
        print(f"\n✅ GUESS SUCCESS! Card '{guessed_card}' removed.")
        print(f"Team {clue_giver_team} score is now: {self.scores[clue_giver_team]}")

        # Calls next card
        self.next_card()

    def next_card(self):
        current_card_list = self.get_current_card_list()

        if not current_card_list:
            # If the list is empty, the round is over
            print(f"Round {self.round} is finished!")  # Prints for testing remove later**************************
            self.end_turn()  # End the turn and rotate the captain chooser
            return

        # Set the next card to the item at index 0
        self.card_in_play = current_card_list[0]
        print(f"Next Card in Play: {self.card_in_play}")  # Prints for testing remove later**************************

    def skip_card(self):
        if self.round == 1:
            print(
                f"🛑 SKIP FAILED: Skipping is not allowed in Round {self.round}. Card remains in play.")  # Prints for testing remove later**************************
            return

        # On rounds 2 and 3, removes the card to skip it, but appends it to the end of the list
        current_card_list = self.get_current_card_list()
        skipped_card = current_card_list.pop(0)
        current_card_list.append(skipped_card)

        print(
            f"\n🔄 CARD SKIPPED: '{skipped_card}' moved to the back of the list.")  # Prints for testing remove later**************************

        self.next_card()

    def end_turn(self):
        self.card_in_play = None  # Resets the card in play
        print("\n⏳ TURN ENDED. Rotating captain chooser.")  # Prints for testing remove later**************************

        # Determine the opposite captain
        if self.current_captain_chooser == self.team_one_captain:
            self.current_captain_chooser = self.team_two_captain
        else:
            self.current_captain_chooser = self.team_one_captain

        print(
            f"Captain Chooser for next turn: {self.current_captain_chooser.user}")  # Prints for testing remove later**************************

    def end_round(self):
        # Check the team that just finished the round
        last_clue_giver_team = None
        if self.current_clue_giver:
            last_clue_giver_team = self.current_clue_giver.team

        # Makes sure the turn ends correctly
        self.card_in_play = None
        self.current_clue_giver = None

        if self.round >= 3:
            self.end_game()
        else:
            self.round += 1
            print(
                f"\n======== STARTING ROUND {self.round}! ========")  # For testing remove later *************************

            # Sets the captain chooser for the new round.
            if last_clue_giver_team == 1:
                # If T1 just finished, T2 starts the next round.
                self.current_captain_chooser = self.team_two_captain
            elif last_clue_giver_team == 2:
                # If T2 just finished, T1 starts the next round.
                self.current_captain_chooser = self.team_one_captain
            else:
                # Default to T1 if the round ended without an active clue giver (shouldn't happen)
                self.current_captain_chooser = self.team_one_captain

            print(
                f"New Round Chooser is: {self.current_captain_chooser.user}")  # For testing remove later *************************

    def end_game(self):
        print("\n============== GAME OVER ==============")  # For testing remove later *************************
        score1 = self.scores[1]
        score2 = self.scores[2]

        if score1 > score2:
            winner = "Team One"
        elif score2 > score1:
            winner = "Team Two"
        else:
            winner = "It's a Tie!"

        print(
            f"FINAL SCORE - Team 1: {score1} | Team 2: {score2}")  # For testing remove later *************************
        print(f"Winner: {winner}")  # For testing remove later *************************


