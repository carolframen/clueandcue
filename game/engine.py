# Clue & Cue
# engine.py
# ---------------- IMPORTS ---------------- #
from .database import cards
import random
import time


# ---------------- PLAYER CLASS ---------------- #
class Player:
    """
    Represents a single user in the game.
    Stores their hand, team assignment, and connection ID.
    """

    def __init__(self, username):
        self.user = username
        self.team = None  # Assigned as 1 or 2
        self.initial_cards = []  # The 8 cards dealt at start
        self.selected_cards = []  # The 5 cards chosen for the deck
        self.sid = None  # Socket ID for private communication

    def to_dict(self):
        """Converts player object to a dictionary for JSON transmission."""
        return {
            "user": self.user,
            "team": self.team,
            "has_selected": len(self.selected_cards) == 5
        }


# ---------------- ROOM CLASS ---------------- #
class Room:
    """
    Manages the state of a single game room.
    Handles logic for turns, scoring, and card management.
    """

    def __init__(self, roomcode, creator_username):
        self.roomcode = roomcode
        self.creator = creator_username
        self.game_state = "LOBBY"  # Phases: LOBBY -> SELECTION -> ROUND_1 -> ROUND_2 -> ROUND_3 -> FINISHED

        # Card Decks
        self.round_one_cards = []
        self.round_two_cards = []
        self.round_three_cards = []

        # Player Data
        self.players = []
        self.players_map = {}

        # Scores
        self.team_one_score = 0
        self.team_two_score = 0

        # Turn Roles
        self.team_one_captain = None
        self.team_two_captain = None
        self.current_captain_chooser = None  # The captain whose turn it is to pick a giver
        self.current_clue_giver = None  # The player currently giving clues

        # Turn State
        self.card_in_play = None
        self.turn_end_timestamp = 0

        # Auto-add creator
        self.add_player(creator_username)

    def add_player(self, username):
        """Adds a new player or returns existing one if reconnecting."""
        if username in self.players_map:
            return self.players_map[username]

        new_player = Player(username)
        self.players.append(new_player)
        self.players_map[username] = new_player
        return new_player

    def start_selection_phase(self):
        """
        Transition from LOBBY to SELECTION.
        Assigns teams, captains, and deals 8 random cards to everyone.
        """
        if len(self.players) < 4:
            return False, "Need at least 4 players."

        # 1. Randomize and Assign Teams
        random.shuffle(self.players)
        for i, player in enumerate(self.players):
            player.team = (i % 2) + 1

        self.team_one_score = 0
        self.team_two_score = 0

        # 2. Assign Captains (First player of each team list)
        t1 = [p for p in self.players if p.team == 1]
        t2 = [p for p in self.players if p.team == 2]

        self.team_one_captain = t1[0]
        self.team_two_captain = t2[0]
        self.current_captain_chooser = self.team_one_captain  # Team 1 always starts choosing

        # 3. Deal Cards
        total_needed = len(self.players) * 8
        deck = random.sample(cards, total_needed)

        start_index = 0
        for player in self.players:
            player.initial_cards = deck[start_index: start_index + 8]
            start_index += 8

        self.game_state = "SELECTION"
        return True, "Started"

    def submit_selection(self, username, selected_indices):
        """
        Processes a player's choice of 5 cards.
        If all players have submitted, it compiles the game deck.
        """
        player = self.players_map.get(username)
        if not player: return False

        # Convert UI indices to Card Objects
        selected = []
        for idx in selected_indices:
            if 0 <= idx < len(player.initial_cards):
                selected.append(player.initial_cards[idx])

        if len(selected) != 5: return False

        player.selected_cards = selected

        # Check if everyone is ready
        all_ready = all(len(p.selected_cards) == 5 for p in self.players)
        if all_ready:
            self.compile_match_deck()

        return True

    def compile_match_deck(self):
        """Combines all selected cards into the main deck for the game."""
        master_list = []
        for p in self.players:
            master_list.extend(p.selected_cards)
        random.shuffle(master_list)

        # Copy deck for all 3 rounds
        self.round_one_cards = master_list[:]
        self.round_two_cards = master_list[:]
        self.round_three_cards = master_list[:]
        self.game_state = "ROUND_1"

    def set_clue_giver(self, username):
        """Sets who is giving clues this turn."""
        player = self.players_map.get(username)
        if player:
            self.current_clue_giver = player
            self.start_turn()

    def start_turn(self):
        """Starts the timer and reveals the first card."""
        deck = self._get_current_deck()
        if deck:
            self.card_in_play = deck[0]
            # TIMER: Set to 30 seconds from now
            self.turn_end_timestamp = time.time() + 30
        else:
            self.end_round()

    def guess_correct(self):
        """Logic when 'Got it!' is pressed."""


        # Allow 1 second buffer for latency
        if self.turn_end_timestamp > 0 and time.time() > self.turn_end_timestamp + 1:
            return

        deck = self._get_current_deck()
        if not deck: return

        # Remove card from deck
        deck.pop(0)

        # Add points
        if self.current_clue_giver.team == 1:
            self.team_one_score += 1
        else:
            self.team_two_score += 1

        # Reveal next card or end round
        if deck:
            self.card_in_play = deck[0]
        else:
            self.end_round()

    def skip_card(self):
        """Logic when 'Skip' is pressed (moves card to bottom)."""
        if self.game_state == "ROUND_1": return  # No skipping in Round 1

        # Check if time is up here too
        if self.turn_end_timestamp > 0 and time.time() > self.turn_end_timestamp + 1:
            return

        deck = self._get_current_deck()
        if not deck: return

        card = deck.pop(0)
        deck.append(card)
        self.card_in_play = deck[0]

    def end_turn(self):
        """Clean up after time runs out or turn is ended."""
        self.current_clue_giver = None
        self.card_in_play = None
        self.turn_end_timestamp = 0

        # Switch Captain control
        if self.current_captain_chooser == self.team_one_captain:
            self.current_captain_chooser = self.team_two_captain
        else:
            self.current_captain_chooser = self.team_one_captain

    def end_round(self):
        """Transitions to the next round or finishes the game."""
        self.end_turn()
        if self.game_state == "ROUND_1":
            self.game_state = "ROUND_2"
        elif self.game_state == "ROUND_2":
            self.game_state = "ROUND_3"
        else:
            self.game_state = "FINISHED"

    def _get_current_deck(self):
        """Helper to get the active card list based on state."""
        if self.game_state == "ROUND_1": return self.round_one_cards
        if self.game_state == "ROUND_2": return self.round_two_cards
        if self.game_state == "ROUND_3": return self.round_three_cards
        return []

    def get_public_state(self):
        """
        Returns a dictionary representing the Room that is safe to send to frontend.
        This runs every time an event happens to update the UI.
        """
        giver_team = self.current_clue_giver.team if self.current_clue_giver else None

        # Calculate seconds remaining based on server time
        if self.turn_end_timestamp > 0:
            time_left = max(0, self.turn_end_timestamp - time.time())
        else:
            time_left = 0

        return {
            "roomcode": self.roomcode,
            "host": self.creator,
            "state": self.game_state,
            "players": [p.to_dict() for p in self.players],
            "scores": {"1": self.team_one_score, "2": self.team_two_score},
            "round_info": {
                "captain_chooser": self.current_captain_chooser.user if self.current_captain_chooser else None,
                "clue_giver": self.current_clue_giver.user if self.current_clue_giver else None,
                "clue_giver_team": giver_team,
                "card": self.card_in_play if self.card_in_play else None,
                "time_remaining": time_left
            }
        }