# Clue & Cue
# ---------------------------- IMPORTS ------------------------------- #
import random


# ---------------------------- FUNCTIONS ------------------------------- #

def generate_room_code():
    room_code = random.randint(1000, 9999)
    return room_code